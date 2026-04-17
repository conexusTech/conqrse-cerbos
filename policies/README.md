# Cerbos Policies for Conqrse

This directory contains Cerbos policy definitions for the Conqrse authorization system using the "Act AS" delegation model.

## Policy Files

### Core Policies

- **`_derived_roles.yaml`** — Defines derived roles based on user level and type combinations
  - SU-level roles: `su_user`, `su_owner_admin`, `su_lead_and_below`, `su_collaborator`
  - Agency-level roles: `agency_user`, `agency_owner_admin`, `agency_lead_member`, `agency_collaborator`
  - Retailer-level roles: `retailer_user`, `retailer_owner_admin`, `retailer_lead_member`, `retailer_collaborator`
  - Act AS delegation roles: `is_acting_as`, `su_acting_as_agency`, `su_acting_as_retailer`, `agency_acting_as_retailer`
  - Action permission roles: `can_write_resources`, `can_manage_settings`, `can_read_only`

- **`resource_base.yaml`** — Base resource policies for all product resources (footprints, signage, qr, reports, connect)
  - Controls `resource:list`, `resource:view`, `resource:create`, `resource:update`, `resource:delete`, `resource:export`, `resource:import`
  - Implements product subscription validation for retailer-level users
  - SU/Agency users bypass product checks
  - Handles direct access and "Act AS" delegation patterns

- **`resource_settings_base.yaml`** — Settings resource policies for all levels
  - Controls `settings:list`, `settings:create`, `settings:update`, `settings:delete`
  - Only owner/admin types can manage settings
  - Enforces restrictions on lead/member/collaborator types (no settings access)
  - Handles delegation via "Act AS"

- **`resource_dashboards.yaml`** — Dashboard access policies
  - `su-dashboard` — SU level only
  - `agency-dashboard` — SU level and Agency level (own agency)
  - `retailer-dashboard` — SU, Agency (child retailers), and Retailer level (own retailer)

- **`resource_users.yaml`** — User management policies
  - SU Owner/Admin can create users at any level
  - Agency Owner/Admin can create users only for their child retailers
  - Retailers can manage users within their retailer
  - Delegation rules for "Act AS" pattern

## User Hierarchy

```
Super User (SU)
├── Owner     → Root User (full system access + settings)
├── Admin     → Platform Administrator (full system access + settings)
├── Lead      → Platform Lead (system support, no settings)
├── Member    → Platform Member (system support, no settings)
└── Collaborator → Platform Collaborator (read-only)

Agency (Subscriber)
├── Owner     → Agency Owner (manage retailers + settings)
├── Admin     → Agency Manager (manage retailers + settings)
├── Lead      → Agency Lead (operator, no settings)
├── Member    → Agency Member (operator, no settings)
└── Collaborator → Agency Collaborator (read-only)

Retailer (Tenant)
├── Owner     → Retailer Owner (full retailer access + settings)
├── Admin     → Retailer Manager (full retailer access + settings)
├── Lead      → Team Lead (operator, no settings)
├── Member    → Staff / Operator (operator, no settings)
└── Collaborator → Guest / Collaborator (read-only)
```

## Act AS Delegation Model

SU and Agency users can delegate to lower levels using the "Act AS" pattern:

- **SU Admin acting AS Retailer** → becomes Retailer Admin (retains user type)
- **Agency Member acting AS Retailer** → becomes Retailer Member (retains user type)
- **Retailer users** → cannot act as other users (terminal level)

When acting AS, the user:
1. Assumes the target level's scope
2. Retains their original user type
3. Becomes subject to product validation (unless SU)
4. Cannot escalate permissions

## Resource Validation

### Principal Attributes Required

```json
{
  "userLevel": "su|agency|retailer",
  "userType": "owner|admin|lead|member|collaborator",
  "products": ["footprints", "qr", ...],
  "agencyId": "required for agency/retailer",
  "retailerId": "required for retailer",
  "actingAs": {
    "level": "agency|retailer",
    "agencyId": "when acting as agency",
    "retailerId": "when acting as retailer"
  }
}
```

### Resource Attributes Required

```json
{
  "product": "footprints|signage|qr|reports|connect|settings|dashboards",
  "agencyId": "when scoped to agency",
  "retailerId": "when scoped to retailer",
  "dashboard": "su-dashboard|agency-dashboard|retailer-dashboard"
}
```

## Product Subscription Validation

- **SU level**: Bypasses all product checks
- **Agency level**: Bypasses product checks for their scope
- **Retailer level**: Must have product in `principal.products[]` array

Example: Retailer member with `products: ["qr"]` can access QR resources but will be DENIED access to Signage resources.

## Action Namespacing

Actions are organized by scope:

- **resource:\*** — Resource operations
  - `resource:list` — List resources
  - `resource:view` — View single resource
  - `resource:create` — Create new resource
  - `resource:update` — Update resource
  - `resource:delete` — Delete resource
  - `resource:export` — Export resource data
  - `resource:import` — Import resource data

- **settings:\*** — Settings operations
  - `settings:list` — List settings
  - `settings:create` — Create setting
  - `settings:update` — Update setting
  - `settings:delete` — Delete setting

## Policy Organization

Policies are organized by resource type:
- `resource_base.yaml` — General product resources
- `resource_settings_base.yaml` — Settings at all levels
- `resource_dashboards.yaml` — Dashboard access
- `resource_users.yaml` — User management

To extend with new resources:
1. Create `resource_[type].yaml`
2. Import `_derived_roles`
3. Define rules using derived roles
4. Follow the allow/deny patterns established

## Testing Policies

Use the Cerbos test utilities with payloads from `CERBOS_CONQRSE_EXAMPLES.md` in the docs directory.

Example test case:
```json
{
  "principal": {
    "id": "user-123",
    "userLevel": "retailer",
    "userType": "member",
    "products": ["qr"],
    "agencyId": "agency-456",
    "retailerId": "retail-789"
  },
  "resource": {
    "product": "qr",
    "retailerId": "retail-789"
  },
  "action": "resource:list"
}
```

Expected: **ALLOW**
