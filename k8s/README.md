# Cerbos Kubernetes Deployment

This directory contains Kubernetes manifests for deploying Cerbos authorization server using Kustomize for environment-specific configurations.

## Directory Structure

```
k8s/
├── base/                    # Shared base manifests (common to all environments)
│   ├── namespace.yaml
│   ├── configmap-config.yaml
│   ├── configmap-policies.yaml
│   ├── configmap-schemas.yaml
│   ├── service.yaml
│   ├── ingress.yaml
│   ├── deployment.yaml
│   └── kustomization.yaml
├── overlays/
│   ├── production/          # Production-specific overrides
│   │   └── kustomization.yaml
│   └── staging/             # Staging-specific overrides
│       └── kustomization.yaml
└── README.md
```

## Environment Differences

### Staging (`cerbos-staging`)
- **Namespace**: `cerbos-staging`
- **Ingress Host**: `cerbos-staging.conqrse.com`
- **Replicas**: 1
- **Resources**: 100m CPU (request), 128Mi memory (request), 500m CPU (limit), 256Mi memory (limit)
- **Use Case**: Testing new policies and configurations before production deployment

### Production (`cerbos-production`)
- **Namespace**: `cerbos-production`
- **Ingress Host**: `cerbos-production.conqrse.com`
- **Replicas**: 2 (for high availability)
- **Resources**: 250m CPU (request), 256Mi memory (request), 1000m CPU (limit), 512Mi memory (limit)
- **Use Case**: Live authorization policies serving production traffic

## Deployment

### Prerequisites
- Kubernetes cluster running 1.19+
- `kubectl` configured to access your cluster
- `kustomize` installed (or use `kubectl apply -k` which has kustomize built-in)

### Deploy to Staging

```bash
# Using kustomize directly
kustomize build k8s/overlays/staging | kubectl apply -f -

# Or using kubectl with kustomize (recommended)
kubectl apply -k k8s/overlays/staging
```

### Deploy to Production

```bash
# Using kustomize directly
kustomize build k8s/overlays/production | kubectl apply -f -

# Or using kubectl with kustomize
kubectl apply -k k8s/overlays/production
```

### Preview Generated Manifests

Before applying, preview the final generated manifests:

```bash
# For staging
kubectl kustomize k8s/overlays/staging

# For production
kubectl kustomize k8s/overlays/production
```

## Managing Policies

### Update Policies in Staging

1. Edit policies in `k8s/base/configmap-policies.yaml`
2. Deploy to staging:
   ```bash
   kubectl apply -k k8s/overlays/staging
   ```
3. Test policies using the staging Cerbos instance at `cerbos-staging.conqrse.com`

### Promote to Production

Once policies are tested and validated in staging:

```bash
kubectl apply -k k8s/overlays/production
```

## Troubleshooting

### Check Deployment Status

```bash
# Staging
kubectl get deployments -n cerbos-staging
kubectl get pods -n cerbos-staging
kubectl logs -n cerbos-staging deployment/cerbos

# Production
kubectl get deployments -n cerbos-production
kubectl get pods -n cerbos-production
kubectl logs -n cerbos-production deployment/cerbos
```

### Verify Service and Ingress

```bash
# Check services
kubectl get svc -n cerbos-staging
kubectl get svc -n cerbos-production

# Check ingress
kubectl get ingress -n cerbos-staging
kubectl get ingress -n cerbos-production

# Describe ingress for troubleshooting
kubectl describe ingress -n cerbos-staging
kubectl describe ingress -n cerbos-production
```

## Key Differences from Original Manifests

- **Kustomize overlays**: Environment-specific configurations without duplication
- **Separate namespaces**: Production and staging are isolated
- **Configurable resources**: Production has higher resource limits and replicas
- **Scalability**: Production can easily scale to more replicas if needed

## Next Steps

1. Test policies in `cerbos-staging`
2. Validate authorization behavior
3. Deploy to `cerbos-production` once validated
4. Monitor logs and metrics in both environments

## Notes

- TLS/HTTPS is commented out in ingress manifests. Uncomment and configure with your certificate when ready.
- The current configuration watches for policy changes on disk. Ensure ConfigMaps are mounted correctly.
- For large-scale deployments, consider using a dedicated storage backend instead of disk storage.
