#!/bin/bash

# Deploy script for Cerbos Kubernetes manifests
# Usage: ./deploy.sh [staging|production]

set -e

ENVIRONMENT=${1:-staging}
VALID_ENVS=("staging" "production")

if [[ ! " ${VALID_ENVS[@]} " =~ " ${ENVIRONMENT} " ]]; then
    echo "Error: Invalid environment. Must be 'staging' or 'production'"
    echo "Usage: $0 [staging|production]"
    exit 1
fi

OVERLAY_PATH="k8s/overlays/${ENVIRONMENT}"

if [ ! -d "$OVERLAY_PATH" ]; then
    echo "Error: Overlay path does not exist: $OVERLAY_PATH"
    exit 1
fi

echo "=== Deploying Cerbos to $ENVIRONMENT ==="
echo "Overlay path: $OVERLAY_PATH"
echo ""

# Preview manifests
echo "=== Previewing manifests that will be applied ==="
kubectl kustomize "$OVERLAY_PATH"
echo ""

# Confirm deployment
read -p "Do you want to proceed with deployment? (yes/no) " -n 3 -r
echo
if [[ $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
    echo "Applying manifests to cluster..."
    kubectl apply -k "$OVERLAY_PATH"
    echo ""
    echo "=== Deployment complete ==="

    # Get namespace
    NAMESPACE="cerbos-${ENVIRONMENT}"

    echo ""
    echo "=== Deployment Status ==="
    kubectl get deployments -n "$NAMESPACE"
    echo ""
    kubectl get pods -n "$NAMESPACE"
    echo ""
    echo "=== Service Status ==="
    kubectl get svc -n "$NAMESPACE"
    echo ""
    echo "=== Ingress Status ==="
    kubectl get ingress -n "$NAMESPACE"
else
    echo "Deployment cancelled."
    exit 1
fi
