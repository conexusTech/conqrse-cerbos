# conqrse-cerbos

Cerbos authorization server and policy definitions for the Conqrse platform. This repository is the **Single Source of Truth** for all RBAC policies enforced across `conqrse-admin` (frontend/BFF) and `conqrse-api3` (NestJS backend).

---

## Quick Start

### Prerequisites

- Docker & Docker Compose installed

### Start Cerbos Server

```bash
cd conqrse-cerbos
docker-compose up
```

Cerbos will be available on:
- **gRPC**: `localhost:3593` (used by frontend and API)
- **HTTP**: `localhost:3592` (admin UI and health checks)

### Verify

```bash
curl -s http://localhost:3592/health | jq .
# Expected: { "status": "ok" }
```

### View Policies

Open http://localhost:3592/ in your browser.

### Stop

```bash
docker-compose down
```

---

## Policy Overview

All policies live in `policies/` and are hot-reloaded by Cerbos when `watchForChanges: true` is set (default).

| File | Purpose |
|------|---------|
| `_derived_roles.yaml` | Maps user attributes (`userLevel`, `userType`) to Cerbos derived roles |
| `resource_product.yaml` | Product resource access (footprint, signage, QR, etc.) |
| `resource_settings.yaml` | Settings access (personal, product, general) |
| `resource_profile.yaml` | Dashboard routing (SU, agency, retailer dashboards) |

### Derived Roles

| Role | Condition |
|------|-----------|
| `super_user` | `userLevel == "su"` |
| `agency_user` | `userLevel == "agency"` |
| `retailer_writer` | `userLevel == "retailer"` AND `userType in [owner, admin, lead, member]` |
| `retailer_collaborator` | `userLevel == "retailer"` AND `userType == "collaborator"` |
| `settings_manager` | `userType in [owner, admin]` |
| `own_resource` | `principal.retailerId == resource.retailerId` |
| `has_product` | `resource.product in principal.products` |

---

## Adding a New Resource

1. Create or edit a policy file in `policies/`:

```yaml
---
apiVersion: "api.cerbos.dev/v1"
resourcePolicy:
  version: default
  importDerivedRoles:
    - conqrse_roles
  resource: "myproduct:myresource"
  rules:
    - actions: ["view", "create", "edit", "delete"]
      effect: EFFECT_ALLOW
      derivedRoles:
        - super_user
        - agency_user
```

2. Restart Cerbos (or wait for hot-reload):

```bash
docker-compose restart
```

3. Use in frontend (`<CanI>`) and backend (`@RequirePermission`) -- see respective repo docs.

---

## Project Structure

```
conqrse-cerbos/
├── docker-compose.yml      # Cerbos server configuration
├── policies/               # Authorization policy YAML files
│   ├── _derived_roles.yaml
│   ├── resource_product.yaml
│   ├── resource_settings.yaml
│   └── resource_profile.yaml
├── schemas/                # Future: Cerbos JSON schema files
└── docs/
    └── POLICIES.md         # Detailed policy structure guide
```

---

## Related Repositories

| Repository | Role |
|------------|------|
| `conqrse-admin` | Frontend + BFF -- uses `<CanI>` component and `/api/permissions` |
| `conqrse-api3` | NestJS backend -- uses `@RequirePermission` decorator and `CerbosAuthorizationGuard` |

---

## Documentation

- [Policy Structure Guide](docs/POLICIES.md) -- YAML schema, derived roles, how to add resources
- [Cerbos Official Docs](https://docs.cerbos.dev/)
- [Cerbos Playground](https://play.cerbos.dev/)
