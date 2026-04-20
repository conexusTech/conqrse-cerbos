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

deploy() {
  local overlay="$SCRIPT_DIR/overlays/$ENVIRONMENT"

  if [ ! -d "$overlay" ]; then
    echo "✗ Overlay not found: $overlay"
    exit 1
  fi

  echo "Deploying Cerbos to $ENVIRONMENT environment..."
  kubectl apply -k "$overlay"

  echo "✓ Deployment complete"
  echo ""
  echo "Waiting for rollout..."
  kubectl rollout status deployment/cerbos -n "$ENVIRONMENT" --timeout=5m

  echo ""
  echo "Cerbos service endpoints:"
  kubectl get service -n "$ENVIRONMENT" -l app=cerbos -o wide
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
