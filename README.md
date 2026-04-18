# conqrse-cerbos

Cerbos authorization server and policy definitions for the Conqrse platform. This repository is the **Single Source of Truth** for all RBAC policies enforced across `conqrse-admin` (frontend/BFF) and `conqrse-api3` (NestJS backend).

---

## Quick Start

### Local Development with Docker

#### Prerequisites

- Docker Desktop installed and running

#### Build & Run

```bash
# Build image
docker build -t cerbos:local .

# Run container
docker run -d \
  --name cerbos-dev \
  -p 3592:3592 \
  -p 3593:3593 \
  -v $(pwd)/k8s/base/policies:/policies \
  cerbos:local
```

Cerbos will be available on:
- **HTTP API & Admin UI**: `http://localhost:3592`
- **gRPC API**: `localhost:3593`

#### Verify

```bash
curl http://localhost:3592/_cerbos/health
# Expected: { "status": "SERVING" }
```

#### Stop & Clean

```bash
docker stop cerbos-dev
docker rm cerbos-dev
docker rmi cerbos:local
```

### Kubernetes Deployment

#### Prerequisites

- kubectl configured with cluster access
- kustomize (built into kubectl >= 1.21)
- Cerbos CLI (optional, for policy validation)

#### Deploy to Staging

```bash
chmod +x k8s/deploy.sh
./k8s/deploy.sh staging
```

#### Deploy to Production

```bash
./k8s/deploy.sh production [kubectl-context]
```

#### Verify Deployment

```bash
# Check deployment status
kubectl get deployment -n staging
kubectl logs -n staging -l app=cerbos -f

# Check service endpoints
kubectl get service -n staging -l app=cerbos
```

#### Access Cerbos

- **Staging**: https://staging-cerbos.conqrse.com
- **Production**: https://cerbos.conqrse.com
- **gRPC**: Service DNS `cerbos.{staging|production}:3593`

#### Validate Policies

```bash
cerbos compile k8s/base/policies/
```

---

## Policy Overview

All policies live in `k8s/base/policies/` and are hot-reloaded by Cerbos when storage watching is enabled.

**Current Setup:** Minimal working policies for development/testing

| File | Purpose |
|------|---------|
| `01-derived_roles.yaml` | Minimal derived roles (for testing) |
| `02-test_resource.yaml` | Test resource policy (allow all for testing) |

**For Production:** Extend policies using the authorization model defined in `docs/CERBOS_CONQRSE.md`

The documentation includes:
- Full resource and action mapping (90+ resources)
- 25 derived roles (15 base + 10 act-as delegation)
- User dimensions (userLevel × userType)
- 22 real-world validation scenarios

### User Dimensions

Every user has two attributes determining access:

| Dimension | Values | Purpose |
|-----------|--------|---------|
| **userLevel** | `su`, `agency`, `retailer` | Organizational scope |
| **userType** | `owner`, `admin`, `lead`, `member`, `collaborator` | Permission role |

### Action Rules Summary

- **Read Operations** (list, view, export): All roles except collaborators
- **Write Operations** (create, update, delete, import): owner, admin, lead, member (NOT collaborator)
- **Settings Operations**: owner, admin only (all user levels)
- **Product Validation**: Only applied at retailer level; SU/Agency bypass
- **Act AS Scope**: SU → any level; Agency → child retailers only; Retailer → none

---

## Adding a New Resource

1. Create a policy file in `k8s/base/policies/` following Cerbos 0.51.0 format:

```yaml
---
apiVersion: api.cerbos.dev/v1
resourcePolicy:
  version: default
  importDerivedRoles:
    - conqrse_roles
  resource: myproduct:resource
  rules:
    - actions: ["*"]
      effect: EFFECT_ALLOW
      derivedRoles:
        - any_user
```

2. Validate policies compile correctly:

```bash
cerbos compile k8s/base/policies/
```

3. Test locally (optional):

```bash
docker run -d --name cerbos-test -p 3592:3592 -p 3593:3593 \
  -v $(pwd)/k8s/base/policies:/policies cerbos:local
curl http://localhost:3592/_cerbos/health
docker stop cerbos-test
```

4. Commit and deploy:

```bash
git add k8s/base/policies/
git commit -m "feat: add myproduct authorization policy"
./k8s/deploy.sh staging
./k8s/deploy.sh production
```

5. Use in applications via:
   - Frontend: `<CanI>` component
   - Backend: `@RequirePermission` decorator (see respective repo docs)

---

## Kubernetes Configuration

### Image & Version

- **Image**: `ghcr.io/cerbos/cerbos:0.51.0`
- **Replicas**: 2 (staging), 3 (production)

### Node Scheduling

- **Node Selector**: `Workload: heavy` (runs only on heavy workload nodes)
- **Tolerations**:
  - `workload=heavy:NoSchedule`
  - `env=staging:NoSchedule` (staging environment)

### Service Configuration

- **HTTP API**: Port 3592 (admin UI, health checks, decision API)
- **gRPC API**: Port 3593 (used by applications, decision API)

### Ingress Configuration

- **Gzip Compression**: Enabled (1-9 compression level)
- **Proxy Buffer Size**: 128KB
- **Max Body Size**: 1024MB
- **Timeouts**: 90s (connect, read, send)
- **Load Balancing**: Round robin

### Health Checks

- **Liveness Probe**: HTTP GET `/_cerbos/health` every 10s
- **Readiness Probe**: HTTP GET `/_cerbos/health` every 5s

---

## Validation & Testing

### Test Authorization Examples

See `docs/CERBOS_CONQRSE_EXAMPLES.md` for 22 real-world scenarios:
- 11 Allow scenarios (different roles accessing resources)
- 11 Deny scenarios (permission violations)

Test against these scenarios when adding new policies.

### Policy Compilation

```bash
cerbos compile k8s/base/policies/
```

### View Policy Coverage

```bash
curl -s http://cerbos.staging.conqrse.com/api/policies | jq .
```

---

## Project Structure

```
conqrse-cerbos/
├── docker-compose.yml          # Local Cerbos server configuration
├── k8s/                         # Kubernetes deployment manifests
│   ├── base/
│   │   ├── namespace.yaml
│   │   ├── configmap-config.yaml
│   │   ├── deployment.yaml      # Cerbos deployment (2 replicas, tolerations, nodeSelector)
│   │   ├── service.yaml
│   │   ├── ingress.yaml         # HTTPS, gzip compression, large file support
│   │   ├── kustomization.yaml
│   │   ├── policies/            # All policy YAML files
│   │   │   ├── _derived_roles.yaml
│   │   │   ├── resource_base.yaml
│   │   │   ├── resource_product.yaml
│   │   │   ├── resource_settings_base.yaml
│   │   │   ├── resource_settings.yaml
│   │   │   ├── resource_dashboards.yaml
│   │   │   ├── resource_profile.yaml
│   │   │   └── resource_users.yaml
│   │   └── schemas/             # JSON Schema validation
│   │       ├── principal.json
│   │       └── resource.json
│   ├── overlays/
│   │   ├── staging/             # 1 replica, staging-cerbos.conqrse.com
│   │   │   └── kustomization.yaml
│   │   └── production/          # 3 replicas, cerbos.conqrse.com
│   │       └── kustomization.yaml
│   └── deploy.sh                # Deployment script with validation
├── docs/
│   ├── CERBOS_CONQRSE.md       # Authorization model (resources, roles, actions)
│   ├── CERBOS_CONQRSE_EXAMPLES.md  # 22 example scenarios (allow/deny)
│   └── POLICIES.md              # Detailed policy structure guide
└── README.md                    # This file
```

---

## Related Repositories

| Repository | Role |
|------------|------|
| `conqrse-admin` | Frontend + BFF -- uses `<CanI>` component and `/api/permissions` |
| `conqrse-api3` | NestJS backend -- uses `@RequirePermission` decorator and `CerbosAuthorizationGuard` |

---

## Documentation

### Internal Documentation
- [Authorization Model](docs/CERBOS_CONQRSE.md) -- Complete specification of resources, actions, roles, and validation payload
- [Validation Examples](docs/CERBOS_CONQRSE_EXAMPLES.md) -- 22 real-world scenarios with allow/deny outcomes
- [Policy Structure Guide](docs/POLICIES.md) -- YAML schema, derived roles, how to add resources

### External Resources
- [Cerbos Official Docs](https://docs.cerbos.dev/)
- [Cerbos Playground](https://play.cerbos.dev/)
- [Cerbos GitHub](https://github.com/cerbos/cerbos)
