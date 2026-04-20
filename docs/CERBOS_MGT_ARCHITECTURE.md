# Implementation: API-Driven Cerbos Policy Management

## Context

Policies are managed via Conqrse Admin UI through API v3 REST endpoints. Cerbos Server (with native Admin REST API) is the source of truth for policy storage. MongoDB stores policy metadata only (timestamps, audit info, creator info). Storage backend uses SQLite3 with persistent volume for data durability across pod restarts.

**Architecture Flow:**
```
Admin UI → POST/PUT /v1/cerbos/policies (API v3)
         → Validates request
         → Saves metadata to MongoDB
         → Proxies to Cerbos POST /admin/policy (Basic Auth)
         → Cerbos persists policy to SQLite3 database (PVC-backed)

Admin UI → GET /v1/cerbos/policies (API v3)
         → Fetches policy IDs from Cerbos GET /admin/policies
         → Hydrates full bodies via GET /admin/policy
         → Enriches with MongoDB metadata
         → Returns merged response
```

---

## Repositories Involved

- `conqrse-api3` — NestJS API (policy REST wrapper)
- `conqrse-cerbos` — Cerbos k8s deployment

---

## Part 1: conqrse-api3 Implementation

### New Module: `src/backend/cerbos-policy/`

**1. Schema** — `src/backend/schemas/cerbos-policy.schema.ts`
```typescript
CerbosPolicy {
  cerbosId: string (unique, indexed)     // e.g., "resource.album.default"
  kind: string                            // "resourcePolicy", "principalPolicy", "derivedRoles", etc.
  name: string                            // policy name
  version: string                         // policy version (default: "default")
  description: string                     // optional description
  disabled: boolean                       // mirrors Cerbos disabled state
  annotations: Record<string, string>     // metadata from Cerbos
  createdBy: string                       // Cognito user ID
  updatedBy: string                       // Cognito user ID
  createdAt, updatedAt                    // from BaseSchema/commonSchema
}
```

**2. Service** — `src/backend/services/data/cerbos-policy.service.ts`
- `list()` → GET `/admin/policies` (IDs) + GET `/admin/policy` (bodies) + merge with MongoDB metadata
- `getById(cerbosId)` → GET `/admin/policy?id=...` + fetch MongoDB metadata
- `upsert(dto, userId)` → POST `/admin/policy` + upsert MongoDB metadata
- `remove(cerbosId)` → POST `/admin/policy/delete` + delete MongoDB doc
- `disable(cerbosId)` → PUT `/admin/policy/disable` + update MongoDB
- `enable(cerbosId)` → PUT `/admin/policy/enable` + update MongoDB

All requests use HTTP Basic Auth (`Authorization: Basic base64(username:password)`)

**3. Controller** — `src/backend/controllers/cerbos-policy.controller.ts`
Endpoints (all under `/v1/cerbos/policies`):
| Method | Path | Guards | Purpose |
|--------|------|--------|---------|
| GET | `/` | Auth + Cerbos | List all policies |
| GET | `/:id` | Auth + Cerbos | Get specific policy |
| POST | `/` | Auth + Cerbos | Create/upsert policy |
| PUT | `/:id` | Auth + Cerbos | Update policy |
| DELETE | `/:id` | Auth + Cerbos | Delete policy |
| POST | `/:id/disable` | Auth + Cerbos | Disable policy |
| POST | `/:id/enable` | Auth + Cerbos | Enable policy |

Uses `CerbosAuthorizationGuard` with `@RequirePermission('cerbos_policy', action)` per method.

**4. DTOs and Entity**
- `CreateCerbosPolicyDto` / `UpdateCerbosPolicyDto` — accept full Cerbos v1Policy object
- `CerbosPolicyEntity` — response entity merging Cerbos policy + MongoDB metadata

**5. Config**
- Added to `src/config/interfaces/config.interface.ts`:
  - `CERBOS_BASE_URL`
  - `CERBOS_ADMIN_USERNAME`
  - `CERBOS_ADMIN_PASSWORD`
- Added defaults in `src/config/configuration.ts`

**6. Module Registration** — `src/backend/backend.module.ts`
- MongooseModule.forFeature for CerbosPolicy schema (connection: 'main')
- Registered CerbosPolicyController and CerbosPolicyService

---

## Part 2: conqrse-cerbos Implementation

### Storage Migration: Disk → SQLite3

**1. Configuration Files**

`cerbos.yaml` (local dev):
```yaml
storage:
  driver: "sqlite3"
  sqlite3:
    dsn: "/data/cerbos.db?_journal=WAL&cache=shared"

server:
  adminAPI:
    enabled: true
    adminCredentials:
      username: cerbos
      passwordHash: <bcrypt hash>
```

`k8s/base/configmap-config.yaml` (deployed config):
```yaml
storage:
  driver: "sqlite3"
  sqlite3:
    dsn: "/data/cerbos.db?_journal=WAL&cache=shared"

server:
  adminAPI:
    enabled: true
```

**2. Kubernetes Resources**

`k8s/base/pvc.yaml` — PersistentVolumeClaim:
- 1Gi storage for SQLite3 database
- ReadWriteOnce access mode
- Default storage class

`k8s/base/secret.yaml` — Admin Credentials:
- Stores `cerbos:conqrseCerbos` basic auth credentials
- Referenced by deployment as environment variables

**3. Deployment Updates** (`k8s/base/deployment.yaml`)
- Set `replicas: 1` (SQLite3 does not support multi-process concurrent writes)
- Removed `policies` ConfigMap volume (policies now in SQLite3)
- Added PVC volume mount at `/data`
- Changed `readOnlyRootFilesystem: false` (SQLite3 requires write access)
- Added environment variables from Secret for admin credentials

**4. Kustomization** (`k8s/base/kustomization.yaml`)
- Added `pvc.yaml` and `secret.yaml` to resources list
- Kept existing ConfigMap generator (policies directory for reference/seeding if needed)

---

## Implementation Completed

All files are implemented and committed:
- **conqrse-cerbos**: b99ae81 — Migrate storage to SQLite3, enable Admin API
- **conqrse-api3**: 878ca8fc — Implement Cerbos Admin API wrapper

---

## Data Flow

### Create/Update Policy
1. Admin UI sends PUT `/v1/cerbos/policies` with full v1Policy object
2. API v3 validates request, checks Cognito + Cerbos authorization
3. Service calls `POST /admin/policy` to Cerbos (Basic Auth)
4. Cerbos stores in SQLite3
5. API v3 saves metadata to MongoDB (cerbosId, kind, name, version, createdBy, etc.)
6. Response includes merged Cerbos policy + MongoDB metadata

### List/Read Policies
1. Admin UI requests `GET /v1/cerbos/policies`
2. API v3 calls `GET /admin/policies` → returns IDs only
3. For each ID, calls `GET /admin/policy?id=...` → returns full policy body
4. Looks up metadata in MongoDB per cerbosId
5. Merges Cerbos body with MongoDB metadata
6. Returns enriched response

### Disable/Enable/Delete
- Calls corresponding Cerbos Admin API endpoint (`/admin/policy/disable`, `/admin/policy/enable`, `/admin/policy/delete`)
- Updates MongoDB metadata to reflect state change

---

## Important Notes

- **Replicas**: SQLite3 enforces single-replica deployments. If multi-replica scaling is needed in the future, migrate to PostgreSQL or MySQL.
- **PVC Persistence**: All policy data survives pod restarts, redeployments, and rolling updates
- **Metadata**: MongoDB stores audit trail (createdBy, timestamps, annotations). Authoritative policy content stays in Cerbos.
- **Admin API**: Requires Basic Auth credentials. Current hardcoded to `cerbos:conqrseCerbos` (from Secret).

---

## Testing Checklist

1. ✅ Cerbos starts with SQLite3 storage (`docker logs` shows no disk-related errors)
2. ✅ `curl -u cerbos:conqrseCerbos http://localhost:3592/admin/policies` returns empty list
3. ✅ `POST /v1/cerbos/policies` creates policy in both Cerbos and MongoDB
4. ✅ `GET /v1/cerbos/policies` hydrates full policies with metadata
5. ✅ `PUT /v1/cerbos/policies/:id` updates policy in Cerbos and MongoDB
6. ✅ `DELETE /v1/cerbos/policies/:id` removes from both stores
7. ✅ `POST /v1/cerbos/policies/:id/disable` disables in Cerbos + updates MongoDB
8. ✅ `POST /v1/cerbos/policies/:id/enable` enables in Cerbos + updates MongoDB
9. ✅ Pod restart → policies persist (PVC data preserved)
10. ✅ Cerbos hot-reloads policies from SQLite3 on Admin API updates
