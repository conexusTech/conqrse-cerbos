#!/usr/bin/env bash
# Load this repo's Cerbos policies into a Mango Cerbos (conqrse-staging or
# conqrse-production) through the admin API, with a decision probe before and after.
#
#   scripts/mango-load-policies.sh staging              # probe only, no writes
#   scripts/mango-load-policies.sh staging --apply      # load k8s/base/policies at HEAD
#   scripts/mango-load-policies.sh staging --apply --ref ff423c0   # roll back to a commit
#
# Mango's Cerbos runs the upstream image with a sqlite3 store and adminAPI on;
# nothing seeds it (the Avocado seed Job was not carried over). This does what that
# Job's seed.py did: POST every policy file to /admin/policy. Upserts only: it never
# deletes a policy, so a rollback re-posts the old versions over the new ones.
#
# The admin password is read from api3's synced Secret in the same namespace and is
# never printed. Requires: kubectl context for Mango, python3 with pyyaml, curl.
set -euo pipefail

ENV="${1:?usage: $0 staging|production [--apply] [--ref <git-ref>]}"
shift
APPLY=0
REF=HEAD
while [[ $# -gt 0 ]]; do
  case "$1" in
    --apply) APPLY=1 ;;
    --ref) REF="$2"; shift ;;
    *) echo "unknown arg $1" >&2; exit 2 ;;
  esac
  shift
done
case "$ENV" in staging|production) ;; *) echo "env must be staging or production" >&2; exit 2 ;; esac

CTX="arn:aws:eks:us-east-1:082585646836:cluster/mango"
NS="conqrse-$ENV"
PORT=$((13600 + RANDOM % 300))
REPO="$(cd "$(dirname "$0")/.." && pwd)"
WORK="$(mktemp -d)"
trap 'kill "${PF:-0}" 2>/dev/null || true; rm -rf "$WORK"' EXIT

kubectl --context "$CTX" -n "$NS" port-forward deploy/cerbos "$PORT:3592" >/dev/null 2>&1 &
PF=$!
for _ in $(seq 1 20); do curl -sf "localhost:$PORT/_cerbos/health" >/dev/null && break; sleep 1; done
curl -sf "localhost:$PORT/_cerbos/health" >/dev/null || { echo "Cerbos in $NS not reachable"; exit 1; }
BASE="http://localhost:$PORT"

probe() {
  # A retailer member of team t2 viewing sites in their own retailer.
  curl -s -X POST "$BASE/api/check/resources" -d '{
    "requestId":"probe",
    "principal":{"id":"probe","roles":["user"],"attr":{"userLevel":"retailer","userType":"member","products":["signage"],"retailerId":"r1","teamIds":["t2"]}},
    "resources":[
      {"actions":["view"],"resource":{"kind":"footprints:sites:item","id":"restricted-other-team","attr":{"retailerId":"r1","accessMode":"restricted","teamIds":["t1"]}}},
      {"actions":["view"],"resource":{"kind":"footprints:sites:item","id":"restricted-own-team","attr":{"retailerId":"r1","accessMode":"restricted","teamIds":["t2"]}}},
      {"actions":["view"],"resource":{"kind":"footprints:sites:item","id":"open-to-all","attr":{"retailerId":"r1","accessMode":"all","teamIds":[]}}},
      {"actions":["view"],"resource":{"kind":"footprints:sites:item","id":"other-retailer","attr":{"retailerId":"r2","accessMode":"all","teamIds":[]}}}
    ]}' | python3 -c 'import json,sys
d=json.load(sys.stdin)
for r in d.get("results",[]): print("  %-22s %s" % (r["resource"]["id"], r["actions"]["view"]))
if "results" not in d: print("  unexpected response:", d)'
}

echo "== $NS: decisions BEFORE"
probe
echo "   expected after loading: restricted-other-team DENY, restricted-own-team ALLOW,"
echo "   open-to-all ALLOW, other-retailer DENY"

if [[ $APPLY -eq 0 ]]; then
  echo "Probe only. Re-run with --apply to load policies at $REF."
  exit 0
fi

git -C "$REPO" archive "$REF" k8s/base/policies | tar -x -C "$WORK"
SECRET="$(kubectl --context "$CTX" -n "$NS" get secret -o name | grep -E '^secret/api3' | head -1)"
[[ -n "$SECRET" ]] || { echo "No api3 secret in $NS"; exit 1; }
export CERBOS_ADMIN_USERNAME CERBOS_ADMIN_PASSWORD
CERBOS_ADMIN_USERNAME="$(kubectl --context "$CTX" -n "$NS" get "$SECRET" -o jsonpath='{.data.CERBOS_ADMIN_USERNAME}' | base64 -d)"
CERBOS_ADMIN_PASSWORD="$(kubectl --context "$CTX" -n "$NS" get "$SECRET" -o jsonpath='{.data.CERBOS_ADMIN_PASSWORD}' | base64 -d)"
[[ -n "$CERBOS_ADMIN_PASSWORD" ]] || { echo "No CERBOS_ADMIN_PASSWORD in $SECRET"; exit 1; }

echo "== loading $(git -C "$REPO" rev-parse --short "$REF") policies into $NS"
BASE="$BASE" DIR="$WORK/k8s/base/policies" python3 - <<'PY'
import base64, json, os, sys, time, urllib.request, yaml
base, d = os.environ["BASE"], os.environ["DIR"]
auth = base64.b64encode(f'{os.environ["CERBOS_ADMIN_USERNAME"]}:{os.environ["CERBOS_ADMIN_PASSWORD"]}'.encode()).decode()
files = sorted(f for f in os.listdir(d) if f.endswith((".yaml", ".yml")))
ok = 0
for name in files:
    policy = yaml.safe_load(open(os.path.join(d, name)))
    body = json.dumps({"policies": [policy]}).encode()
    for attempt in range(1, 5):
        req = urllib.request.Request(f"{base}/admin/policy", data=body, method="POST",
              headers={"Content-Type": "application/json", "Authorization": f"Basic {auth}"})
        try:
            urllib.request.urlopen(req, timeout=15); ok += 1; break
        except urllib.error.HTTPError as e:
            if e.code < 500 or attempt == 4:
                print(f"ERROR {name}: {e.code} {e.read().decode()[:300]}"); sys.exit(1)
            time.sleep(2 * attempt)
print(f"loaded {ok}/{len(files)} policies")
PY

echo "== $NS: decisions AFTER"
probe
