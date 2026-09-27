# conqrse-cerbos

Cerbos authorization server and policy definitions for the Conqrse platform. This repository is the **Single Source of Truth** for all RBAC policies enforced across `conqrse-admin` (frontend/BFF) and `conqrse-api3` (NestJS backend).

## Documentation Map

Start here based on your role:

| Audience | Start with |
|---|---|
| **QA / PM / Ops** — What's deployed, what's covered, drift status | [`docs/CERBOS_STATUS.md`](docs/CERBOS_STATUS.md) |
| **All roles** — Authoritative resource × product × action matrix | [`docs/RESOURCES_ACTIONS_MATRIX.md`](docs/RESOURCES_ACTIONS_MATRIX.md) |
| **Devs adding resources** — How the policy generator works | [`docs/POLICY_GENERATION.md`](docs/POLICY_GENERATION.md) |
| **Devs integrating** — The `@conqrse/permission-types` npm package | [`docs/PERMISSION_TYPES_PACKAGE.md`](docs/PERMISSION_TYPES_PACKAGE.md) |
| **QA writing tests** — Example allow/deny scenarios | [`docs/CERBOS_CONQRSE_EXAMPLES.md`](docs/CERBOS_CONQRSE_EXAMPLES.md) |
| **Devs writing tests** — Testing guide | [`docs/TESTING.md`](docs/TESTING.md) |

Refresh the status doc anytime with `python3 scripts/generate_status.py`.

---

## Quick Start

### Local Development with Docker

Prerequisites: Docker Desktop.

```bash
# Build image
docker build -t cerbos:local .

# Run container
docker run -d \
  --name cerbos-dev \
  -p 3592:3592 \
  -p 3593:3593 \
  -v $(pwd)/k8s/base/policies:/policies:ro \
  cerbos:local
```

The local configuration uses Cerbos's disk driver and reads the checked-in
policy bundle directly. Kubernetes supplies a separate SQLite configuration;
the local container does not create or persist policy state.

Cerbos will be available on:
- **HTTP API & Admin UI**: `http://localhost:3592`
- **gRPC API**: `localhost:3593`

Verify:

```bash
curl http://localhost:3592/_cerbos/health
# Expected: { "status": "SERVING" }
```

Stop & clean:

```bash
docker stop cerbos-dev && docker rm cerbos-dev && docker rmi cerbos:local
```

### Kubernetes Deployment

Prerequisites: `kubectl` configured with cluster access, `kustomize` (built into kubectl >= 1.21), Cerbos CLI (for policy validation).

```bash
# Deploy to staging
./k8s/deploy.sh staging

# Deploy to production
./k8s/deploy.sh production
```

The deploy script validates policies (`cerbos compile`) before applying manifests and re-runs the seed job so the new policies land on the Cerbos server.

Verify deployment:

```bash
kubectl get deployment -n staging cerbos
kubectl logs -n staging -l app=cerbos --tail=50
kubectl logs -n staging job/cerbos-seed-policies | tail
```

**Endpoints:**
- **Staging**: https://staging-cerbos.conqrse.com
- **Production**: https://cerbos.conqrse.com
- **In-cluster gRPC**: `cerbos.{staging|production}:3593`

Validate policies locally before deploying:

```bash
cerbos compile k8s/base/policies/
```

---

## Authorization Model (Summary)

Every principal has two attributes that combine into a derived role:

| Dimension | Values | Purpose |
|---|---|---|
| **userLevel** | `su`, `agency`, `retailer`, `brand` | Organizational scope |
| **userType** | `owner`, `admin`, `lead`, `member`, `collaborator` | Permission role |

**Derived role tiers:**
- **SU**: `root_user`, `platform_administrator`, `platform_lead`, `platform_member`, `platform_collaborator`
- **Agency**: `agency_owner`, `agency_manager`, `agency_lead`, `agency_member`, `agency_collaborator`
- **Retailer**: `retailer_owner`, `retailer_manager`, `team_lead`, `staff_operator`, `guest_collaborator`
- **Brand** (DealDesk only): `brand_owner`, `brand_manager`, `brand_lead`, `brand_member`

**Product gating:** Resources declare required products in the matrix. A policy allows access only when the principal's `P.attr.products` satisfies the row's marker:
- `required` — OR semantics (`.exists()` in CEL). Any one of the marked products grants access.
- `required-all` — AND semantics (`.all()` in CEL). All marked products required simultaneously. Used exclusively by DealDesk (`ssp` + `trade` + `brand_center`).

**DealDesk two-rule structure:** Every `dealdesk:*` policy has two rule blocks that OR together at the policy level — a Retailer path (AND product check + `retailerId ==`) and a Brand path (`brand_center` + `retailerId in retailerIds`). Full details in [`docs/RESOURCES_ACTIONS_MATRIX.md`](docs/RESOURCES_ACTIONS_MATRIX.md).

For the complete model — every resource, its actions, and required products — see [`docs/RESOURCES_ACTIONS_MATRIX.md`](docs/RESOURCES_ACTIONS_MATRIX.md).

---

## How To

This section is the end-to-end workflow for changing what Cerbos enforces. It is the same workflow whether you are **adding** a new resource, **modifying** an existing one, or **removing** one.

### Golden Rules

1. **Matrix first.** Never hand-edit a `resource_*.yaml` for a resource that lives in the generator. Change the matrix (`docs/RESOURCES_ACTIONS_MATRIX.md`) and regenerate.
2. **Kustomization allowlist is easy to forget.** A policy file that isn't listed in `k8s/base/kustomization.yaml`'s `configMapGenerator.files:` **will never reach any cluster.** The status generator flags this explicitly.
3. **Every policy change bumps `@conqrse/permission-types`.** Consumers (`conqrse-admin`, `conqrse-api3`) rely on the generated enums. If a resource/role/product exists in the deployed policies but not in the enums (or vice versa), runtime auth breaks — this is why the version bump is mandatory, not optional.
4. **Both environments get the same policies.** Never deploy a policy to production that hasn't run in staging first. Never leave staging ahead of production for more than one release cycle without an explicit reason (dealdesk pilot, feature flag, etc.).
5. **Removing an action from the matrix breaks `conqrse-api3`'s build.** That is deliberate — see below.

### The api3 route contract (CBS-4)

`conqrse-api3` asserts, on every build, that each of its ~215 `@RequirePermission` decorators names a resource that exists in `RESOURCE_META` and an action that resource **grants** (`test/cerbos-route-contract.spec.ts`). This exists because the failure it catches is otherwise invisible: api3's decorator is typed `(resource: string, action: string)`, Cerbos is default-deny, and `PERMISSION_BYPASS=true` means the guard never asks the PDP. A route naming an action the matrix does not grant therefore compiles, passes its tests, and works in production — right up until enforcement is switched on, at which point it 403s for everyone with nothing in the logs explaining why.

Two consequences for work in this repo:

- **Narrowing a resource's action list is a breaking change for api3.** If you remove an action that a route still uses, api3's suite fails with the offending file and route named. Check consumers before narrowing, and land the api3 change first.
- **Widening is always safe**, which is why adding the taxonomy read tier (CBS-1) needed no api3 coordination.

Audited clean on 2026-07-27 against `permission-types` 1.9.0: 215 sites, 118 distinct resource+action pairs, zero mismatches — including `contents:tags:item`, which still matches after API-6 moved those routes under `/retailers/:retailer/`.

### HOW TO — Update seeded policies (new / modified / removed)

This covers the full path from matrix change to the policies being live on **both staging AND production**.

**Step 1. Update the matrix**

Edit `docs/RESOURCES_ACTIONS_MATRIX.md`:
- Adding a resource: append rows to the resource-actions table under its grouping AND to the Product × Resource Matrix table (with `required` / `required-all` markers).
- Modifying a resource: change its actions row and/or its matrix row.
- Removing a resource: delete both rows.

**Step 2. Update the kustomization allowlist**

Edit `k8s/base/kustomization.yaml`:
- Adding: append the new filename under `configMapGenerator.files:` (alphabetized).
- Removing: delete the entry.
- Modifying only: no change here.

Skipping this step is the single most common cause of "I deployed but nothing changed" — the file is generated but never ships. `scripts/generate_status.py` will flag missing entries under "Sync Status".

**Step 3. Regenerate policy YAMLs**

For a single resource (recommended — preserves hand-edits elsewhere):

```bash
python3 scripts/generate_policies.py --resource "<resource:name>" --force
```

For multiple related resources (e.g., regenerating all `dealdesk:*`):

```bash
python3 -c "
import sys; sys.path.insert(0, 'scripts')
from generate_policies import MatrixParser
for r in MatrixParser('docs/RESOURCES_ACTIONS_MATRIX.md').merge_data():
    if r.name.startswith('dealdesk:'):
        print(r.name)
" | while read res; do
  python3 scripts/generate_policies.py --resource "$res" --force
done
```

For everything (use with care — overwrites hand-edited comments in every generator-managed file):

```bash
python3 scripts/generate_policies.py --force
```

**Step 4. Regenerate `@conqrse/permission-types`**

```bash
python3 scripts/generate_types.py --force
```

**Step 5. Bump the permission-types package version**

Edit `packages/permission-types/package.json`. Semver guidance:
- New resource / role / product / user-level added → **minor** bump (e.g., `1.5.0 → 1.6.0`)
- Any value renamed or removed → **major** bump (e.g., `1.5.0 → 2.0.0`) — this is a breaking change for consumers
- Package-only fix (build config, layout) with no enum changes → **patch** bump

**Step 6. Build & validate**

```bash
cd packages/permission-types && npm run build && cd -
cerbos compile k8s/base/policies/
```

Both must succeed before proceeding.

**Step 7. Commit**

Stage explicit paths — do NOT `git add -A`:

```bash
git add \
  docs/RESOURCES_ACTIONS_MATRIX.md \
  k8s/base/kustomization.yaml \
  k8s/base/policies/ \
  packages/permission-types/ \
  scripts/
git commit -m "feat: add/update <resource> authorization"
```

**Step 8. Deploy to staging**

```bash
./k8s/deploy.sh staging
```

The deploy script:
1. Validates the policies (`cerbos compile`).
2. Applies the kustomize manifests — the `cerbos-policies` ConfigMap gets replaced with the new file set.
3. Deletes and re-creates the `cerbos-seed-policies` Job, which POSTs every file in `/policies` to the Cerbos admin API.
4. Waits for the deployment rollout.

**Step 9. Verify staging seeded correctly**

```bash
kubectl get job -n staging cerbos-seed-policies
kubectl logs -n staging job/cerbos-seed-policies | tail -20
```

Look for:
- `Successfully seeded <N> policies` where `<N>` matches the number of files in the ConfigMap.
- No `ERROR:` lines.
- Your specific new/modified files appear as `Seeded: resource_<name>.yaml`.

If any of that is off, do NOT proceed to production. Diagnose:
- If the file didn't appear in the seed logs → check `k8s/base/kustomization.yaml` includes it.
- If the seed job errored → check `cerbos compile` locally, review the specific YAML for syntax issues.
- **If the seed died on `_derived_roles.yaml` with a bare `500 Failed to add/update policies`, your policy is almost certainly fine** — see the `SQLITE_BUSY` note below before you go looking for a syntax error.

#### Expect the first seed to fail — `SQLITE_BUSY`

Both tag-policy deploys to date (staging 2026-07-26, production 2026-07-27) failed on the **first** run with:

```
ERROR: Failed to seed _derived_roles.yaml: 500 {"code":13, "message":"Failed to add/update policies"}
```

That message names the first file alphabetically and says nothing useful. The real cause is only in the Cerbos pod logs:

```bash
kubectl logs -n <env> deployment/cerbos --tail=100 | grep -i sqlite
# error: "database is locked (5) (SQLITE_BUSY)"
```

The store is SQLite on the `cerbos-data` PVC with a bare DSN — no `_busy_timeout`, no WAL — so a write fails instantly whenever a reader holds the lock, and Cerbos is serving live authz while the job writes 117 policies. It is a race, not a bad policy, which is why some deploys succeed.

**Nothing breaks when this happens.** Cerbos logs `Error processing storage event, maintaining last valid state` and keeps serving the previous policy set. Recover with:

```bash
kubectl delete job/cerbos-seed-policies -n <env> --wait=true
kubectl rollout restart deployment/cerbos -n <env>
kubectl rollout status  deployment/cerbos -n <env> --timeout=5m
kubectl apply -k k8s/overlays/<env>          # re-creates the seed job
```

The deployment is `Recreate` with one replica, so this costs a brief window with no PDP. Permanent fix (one line, not yet applied — it changes storage config for both environments): set the DSN to `/data/cerbos.db?_busy_timeout=5000&_journal_mode=WAL` in `k8s/base/configmap-config.yaml`.

#### Verify against the PDP, not the ConfigMap

`kubectl apply` updates the `cerbos-policies` ConfigMap immediately, but **the PDP serves from its SQLite store, which only the seed job writes.** So reading the ConfigMap back reports success before the seed has run — and is simply wrong if the seed then fails. Ask Cerbos directly:

```bash
kubectl port-forward -n <env> svc/cerbos 13592:3592 &   # allow ~8s to come up
curl -s -X POST http://localhost:13592/api/check/resources \
  -H 'Content-Type: application/json' -d '{
  "requestId":"verify",
  "principal":{"id":"p","roles":["user"],"attr":{
    "userLevel":"retailer","userType":"member","retailerId":"r1","products":["signage"]}},
  "resources":[{"resource":{"kind":"contents:tags_taxonomy","id":"k",
    "attr":{"retailerId":"r1"}},"actions":["list","view","create"]}]}'
```

`userLevel` + `userType` select the derived roles; `products` must intersect the policy's product list or every action returns `EFFECT_DENY`. Check the negative cases too — a policy that allows everything passes a positive-only test.

**Step 10. Deploy to production**

Only after staging is verified. **Establish the blast radius first** — `kubectl apply -k` ships the whole overlay, not just the files you changed, and production may be behind by more than your commit:

```bash
# what will actually change, server-side
kubectl apply -k k8s/overlays/production --dry-run=server
```

To see it per-policy, diff the **kustomization allowlist** against the live ConfigMap — not the `policies/` directory. The repo holds more policy files than ship (the `cms_*` set is generated but not allowlisted), so a naive directory diff invents phantom additions:

```bash
kubectl -n production get cm cerbos-policies -o json > /tmp/prod-policies.json   # also your rollback copy
python3 - <<'PY'
import json, os, re
live = json.load(open('/tmp/prod-policies.json'))['data']
allow = [os.path.basename(m.group(1)) for m in
         (re.match(r'\s*-\s*(policies/\S+\.yaml)\s*$', l)
          for l in open('k8s/base/kustomization.yaml')) if m]
repo = {f: open('k8s/base/policies/' + f).read() for f in allow}
print('added  :', sorted(set(repo) - set(live)))
print('removed:', sorted(set(live) - set(repo)))
print('changed:', [k for k in sorted(set(repo) & set(live))
                   if repo[k].strip() != live[k].strip()])
PY
```

Sanity-check the result before applying: additive-only changes (new `EFFECT_ALLOW` rules, nothing removed) cannot break a working call under default-deny. Removals and new `EFFECT_DENY` rules can, and deserve a closer look.

```bash
./k8s/deploy.sh production
```

Same script, same steps — but targeting the `production` namespace. The seed job will re-run against the production Cerbos server, and see the `SQLITE_BUSY` note above: production serves live reads, so the first attempt commonly fails.

**Step 11. Verify production seeded correctly**

```bash
kubectl get job -n production cerbos-seed-policies
kubectl logs -n production job/cerbos-seed-policies | tail -20
```

Same checks as staging — **including the check request against the PDP**. A green seed log plus an updated ConfigMap is not proof the rules are live; only a `/api/check/resources` response is.

**Step 12. Publish the permission-types package**

Only after production is verified:

```bash
cd packages/permission-types
npm publish --registry https://npm.conqrse.com/
cd -
npm view @conqrse/permission-types@latest --registry https://npm.conqrse.com/
```

**Step 13. Refresh the status doc**

```bash
python3 scripts/generate_status.py
git add docs/CERBOS_STATUS.md
git commit -m "docs: refresh CERBOS_STATUS after <change>"
```

Open `docs/CERBOS_STATUS.md` and confirm:
- Staging: In sync with repo ✓
- Production: In sync with repo ✓
- staging ↔ production drift: none ✓

**Step 14. Notify consumers**

`conqrse-api3` and `conqrse-admin` maintainers need to:

```bash
npm install @conqrse/permission-types@latest
```

…then rebuild and deploy. Until they do, they may reference stale enum values.

### HOW TO — Update `@conqrse/permission-types`

Standalone workflow if you only need to bump the package (e.g., after a matrix edit that already shipped policy changes):

1. `python3 scripts/generate_types.py --force`
2. Bump `packages/permission-types/package.json` per semver guidance above.
3. `cd packages/permission-types && npm run build`
4. Commit: `chore(permission-types): bump to v<version>`
5. Publish: `npm publish --registry https://npm.conqrse.com/`
6. Consumers run `npm install @conqrse/permission-types@latest`.

See [`docs/PERMISSION_TYPES_PACKAGE.md`](docs/PERMISSION_TYPES_PACKAGE.md) for full details, publishing troubleshooting, and version history.

### HOW TO — Roll back a bad deploy

If a policy change causes production to reject legitimate requests:

1. Revert the offending commit(s) locally.
2. Regenerate the affected policies (`scripts/generate_policies.py --resource ... --force`).
3. `./k8s/deploy.sh production` — the seed job will overwrite the bad policies with the reverted set.
4. Verify with `kubectl logs -n production job/cerbos-seed-policies | tail`.
5. Do the same for staging so it stays consistent.
6. Publish a **new** permission-types version reflecting the reverted state — do NOT unpublish the bad version (npm rejects re-use of published versions; a new patch/minor is required).

---

## Kubernetes Configuration

- **Image**: `ghcr.io/cerbos/cerbos:0.51.0`
- **HTTP API**: Port 3592 (admin UI, health checks, decision API)
- **gRPC API**: Port 3593 (in-cluster consumers)
- **Node selector**: `Workload: heavy`
- **Tolerations**: `workload=heavy:NoSchedule` (plus `env=staging:NoSchedule` on staging)
- **Ingress**: gzip enabled (1–9), 128KB proxy buffer, 1024MB max body size, 90s timeouts
- **Health checks**: liveness/readiness on `/_cerbos/health`

---

## Repository Structure

```
conqrse-cerbos/
├── docker-compose.yml
├── k8s/
│   ├── base/
│   │   ├── configmap-config.yaml
│   │   ├── configmap-seed-script.yaml
│   │   ├── deployment.yaml
│   │   ├── ingress.yaml
│   │   ├── kustomization.yaml         # policy allowlist for ConfigMap generator
│   │   ├── policies/                  # source policies (hand-edited + generated)
│   │   │   ├── _derived_roles.yaml    # SU/Agency/Retailer/Brand tiers
│   │   │   └── resource_*.yaml        # one file per Cerbos resource
│   │   ├── pvc.yaml
│   │   ├── seed-job.yaml
│   │   └── service.yaml
│   ├── overlays/
│   │   ├── staging/                   # namespace: staging
│   │   └── production/                # namespace: production
│   └── deploy.sh                      # validates, applies, and re-runs seed
├── packages/
│   └── permission-types/              # @conqrse/permission-types npm package
├── scripts/
│   ├── generate_policies.py           # matrix → policy YAMLs
│   ├── generate_types.py              # matrix → permission-types package
│   ├── generate_status.py             # live cluster state → CERBOS_STATUS.md
│   └── update_policies_from_matrix.py # patch product lists in existing YAMLs
├── tests/                             # allow/deny scenario tests
└── docs/
    ├── RESOURCES_ACTIONS_MATRIX.md    # authoritative resource × product × action matrix
    ├── CERBOS_STATUS.md               # live deployment + consumer coverage status
    ├── CERBOS_CONQRSE_EXAMPLES.md     # validation payload examples
    ├── PERMISSION_TYPES_PACKAGE.md    # npm package docs
    ├── POLICY_GENERATION.md           # generator script guide
    ├── TESTING.md                     # testing guide
    └── consumer_integrations.yaml     # hand-maintained consumer coverage
```

---

## Related Repositories

| Repository | Role |
|---|---|
| `conqrse-admin` | Frontend + BFF — uses `<CanI>` component and `/api/permissions` |
| `conqrse-api3` | NestJS backend — uses `@RequirePermission` decorator and `CerbosAuthorizationGuard` |

---

## External Resources

- [Cerbos Official Docs](https://docs.cerbos.dev/)
- [Cerbos Playground](https://play.cerbos.dev/)
- [Cerbos GitHub](https://github.com/cerbos/cerbos)
