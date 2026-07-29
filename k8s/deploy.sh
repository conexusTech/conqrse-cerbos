#!/bin/bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENVIRONMENT="${1:-staging}"
KUBECTL_CONTEXT="${2:-}"

validate_environment() {
  case "$ENVIRONMENT" in
    staging|production)
      echo "✓ Valid environment: $ENVIRONMENT"
      ;;
    *)
      echo "✗ Invalid environment: $ENVIRONMENT"
      echo "Usage: $0 [staging|production] [kubectl-context]"
      exit 1
      ;;
  esac
}

set_kubectl_context() {
  if [ -n "$KUBECTL_CONTEXT" ]; then
    echo "Setting kubectl context to: $KUBECTL_CONTEXT"
    kubectl config use-context "$KUBECTL_CONTEXT"
  fi
}

validate_kubeconfig() {
  if ! kubectl cluster-info &>/dev/null; then
    echo "✗ Cannot connect to Kubernetes cluster"
    exit 1
  fi
  echo "✓ Connected to cluster: $(kubectl config current-context)"
}

validate_cerbos_policies() {
  if command -v cerbos &>/dev/null; then
    echo "Validating Cerbos policies..."
    cerbos compile "${SCRIPT_DIR}/base/policies/" || {
      echo "✗ Policy validation failed"
      exit 1
    }
    echo "✓ Policies are valid"
  else
    echo "⚠ Cerbos CLI not found, skipping policy validation"
  fi
}

# Splits rendered manifests into the seed Job and everything else.
# `kubectl apply` cannot filter by kind, and the two halves must be applied at
# different points in the sequence — see the ordering note in deploy().
split_manifests() {
  local want="$1" # "job" | "rest"
  python3 -c '
import sys, yaml
want = sys.argv[1]
docs = [d for d in yaml.safe_load_all(sys.stdin) if d]
keep = [d for d in docs
        if (d.get("kind") == "Job") == (want == "job")]
sys.stdout.write(yaml.safe_dump_all(keep) if keep else "")
' "$want"
}

# True when the rendered cerbos.yaml differs from what the cluster is running.
# Used to decide whether a restart is needed, so a routine policy-only deploy
# does not pay a PDP gap it does not need.
config_changed() {
  local rendered="$1" desired live
  desired="$(printf '%s' "$rendered" | python3 -c '
import sys, yaml
for d in yaml.safe_load_all(sys.stdin):
    if d and d.get("kind") == "ConfigMap" and d["metadata"]["name"] == "cerbos-config":
        sys.stdout.write(d["data"]["cerbos.yaml"]); break
')"
  live="$(kubectl get configmap/cerbos-config -n "$ENVIRONMENT" \
    -o jsonpath='{.data.cerbos\.yaml}' 2>/dev/null || true)"
  [ "$desired" != "$live" ]
}

deploy() {
  local overlay="$SCRIPT_DIR/overlays/$ENVIRONMENT"

  if [ ! -d "$overlay" ]; then
    echo "✗ Overlay not found: $overlay"
    exit 1
  fi

  echo "Deploying Cerbos to $ENVIRONMENT environment..."

  # ORDER MATTERS — config, then RESTART, then seed. BL-8, 2026-07-29.
  #
  # `cerbos-config` is a plain ConfigMap and `cerbos-policies` sets
  # disableNameSuffixHash, so neither is name-hashed and changing them does NOT
  # alter the Deployment's pod spec — no rollout happens. Cerbos reads its
  # storage config once at STARTUP from the mounted /etc/cerbos, so a changed
  # cerbos.yaml has no effect until the pod restarts.
  #
  # The previous sequence applied the ConfigMap and the seed Job in one
  # `kubectl apply -k`, then called `rollout status` — which returned
  # immediately, because nothing had changed in the pod spec. So the seed ran
  # against a pod still holding the OLD config, and the new one took effect
  # only at some unrelated later restart. That is how a storage fix can look
  # applied, be committed, and quietly do nothing: exactly the failure mode
  # BL-8's DSN change was written to end.
  local rendered
  rendered="$(kubectl kustomize "$overlay")"

  local needs_restart=0
  if config_changed "$rendered"; then
    needs_restart=1
    echo "• cerbos.yaml differs from the cluster — a restart is required"
  else
    echo "• cerbos.yaml unchanged — no restart needed"
  fi

  if kubectl get job/cerbos-seed-policies -n "$ENVIRONMENT" &>/dev/null; then
    echo "Deleting existing cerbos-seed-policies job..."
    kubectl delete job/cerbos-seed-policies -n "$ENVIRONMENT" --wait=true
  fi

  # Everything but the seed Job, so the seed cannot start before the restart.
  echo "Applying config, policies and workloads..."
  printf '%s' "$rendered" | split_manifests rest | kubectl apply -f -

  if [ "$needs_restart" -eq 1 ]; then
    echo "Restarting Cerbos so the new config is live before seeding..."
    kubectl rollout restart deployment/cerbos -n "$ENVIRONMENT"
  fi

  echo "Waiting for rollout..."
  kubectl rollout status deployment/cerbos -n "$ENVIRONMENT" --timeout=5m

  # Only now — against a pod running the config we just applied.
  echo "Starting the policy seed job..."
  printf '%s' "$rendered" | split_manifests job | kubectl apply -f -

  echo "✓ Deployment complete"
  echo ""
  echo "Cerbos service endpoints:"
  kubectl get service -n "$ENVIRONMENT" -l app=cerbos -o wide
  echo ""
  echo "Seed progress:  kubectl logs -n $ENVIRONMENT job/cerbos-seed-policies -f"
  # A failed seed is safe — Cerbos logs "maintaining last valid state" and keeps
  # serving the previous policy set — but it is NOT visible from this script,
  # which returns as soon as the Job object is created.
  echo "VERIFY against the PDP, not the ConfigMap: the PDP serves from its own"
  echo "SQLite store, which only the seed job writes."
}

main() {
  echo "Cerbos Deployment Script"
  echo "========================"
  echo ""

  validate_environment
  set_kubectl_context
  validate_kubeconfig
  validate_cerbos_policies
  deploy

  echo ""
  echo "✓ Deployment successful!"
}

main
