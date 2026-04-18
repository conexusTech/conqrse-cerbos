# conqrse-cerbos

Cerbos authorization server and policy definitions for the Conqrse platform. This repository is the **Single Source of Truth** for all RBAC policies enforced across `conqrse-admin` (frontend/BFF) and `conqrse-api3` (NestJS backend).

---

## Quick Start

### Local Development

#### Prerequisites

- Docker & Docker Compose installed

#### Start Cerbos Server

```bash
cd conqrse-cerbos
docker-compose up
```

Cerbos will be available on:
- **gRPC**: `localhost:3593` (used by frontend and API)
- **HTTP**: `localhost:3592` (admin UI and health checks)

#### Verify

```bash
curl -s http://localhost:3592/health | jq .
# Expected: { "status": "ok" }
```

#### View Policies

Open http://localhost:3592/ in your browser.

#### Stop

```bash
docker-compose down
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

| File | Purpose |
|------|---------|
| `_derived_roles.yaml` | 25 derived roles mapping user attributes (`userLevel`, `userType`) + Act AS delegation |
| `resource_base.yaml` | Base resource policy (read/write rules for all roles) |
| `resource_product.yaml` | Product resources (footprints, signage, qr, reports, connect) with product subscription check |
| `resource_settings_base.yaml` | Base settings policy (owner/admin only) |
| `resource_settings.yaml` | Settings admin resources (users, teams, general) |
| `resource_dashboards.yaml` | Dashboard resources (SU, agency, retailer dashboards) |
| `resource_profile.yaml` | Profile resource (all can view, owner/admin can update) |
| `resource_users.yaml` | Users settings resource (owner/admin only) |

### Derived Roles (25 total)

**Base Roles (15):**
- **SU Level** (5): `root_user`, `platform_administrator`, `platform_lead`, `platform_member`, `platform_collaborator`
- **Agency Level** (5): `agency_owner`, `agency_manager`, `agency_lead`, `agency_member`, `agency_collaborator`
- **Retailer Level** (5): `retailer_owner`, `retailer_manager`, `team_lead`, `staff_operator`, `guest_collaborator`

**Act AS Delegation Roles (10):**
- **SU delegating** (5): `su_acting_retailer_*` roles for each user type
- **Agency delegating** (5): `agency_acting_retailer_*` roles for each user type (validates child relationship)

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

1. Create or edit a policy file in `k8s/base/policies/`:

```yaml
apiVersion: api.cerbos.dev/v1
kind: ResourcePolicy
metadata:
  name: myproduct_resource_policy
spec:
  version: "default"
  resource: "myproduct:*"
  rules:
    - actions: ["resource:list", "resource:view", "resource:create"]
      effect: EFFECT_ALLOW
      derivedRoles:
        - root_user
        - platform_administrator
        - agency_owner
        - retailer_owner
```

2. Update `k8s/base/kustomization.yaml` to include the new policy file in `configMapGenerator`:

```yaml
configMapGenerator:
  - name: cerbos-policies
    files:
      - policies/your_new_policy.yaml
```

3. Validate policies:

```bash
cerbos compile k8s/base/policies/
```

4. Commit and deploy:

```bash
git add k8s/base/policies/ k8s/base/kustomization.yaml
git commit -m "feat: add myproduct authorization policy"
./k8s/deploy.sh staging
./k8s/deploy.sh production
```

5. Use in frontend (`<CanI>`) and backend (`@RequirePermission`) -- see respective repo docs.

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

- **HTTP API**: Port 3592 (admin UI, health checks)
- **gRPC API**: Port 3593 (used by applications)
- **Metrics**: Port 3591 (Prometheus)

### Ingress Configuration

- **Gzip Compression**: Enabled (1-9 compression level)
- **Proxy Buffer Size**: 128KB
- **Max Body Size**: 1024MB
- **Timeouts**: 90s (connect, read, send)
- **Load Balancing**: Round robin

### Health Checks

- **Liveness Probe**: HTTP GET `/health` every 10s
- **Readiness Probe**: HTTP GET `/health` every 5s

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
