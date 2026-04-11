# Implementation Patterns & Best Practices

This document describes tested patterns from the legacy system that should guide future policy development.

---

## Pattern 1: Product-Gated Resource

**Use when**: A feature is only available to users whose retailer has purchased a specific product.

### Pattern

```yaml
rules:
  # Allow actions if retailer has the required product
  - actions: ["view", "create", "update", "delete"]
    effect: EFFECT_ALLOW
    derivedRoles:
      - retailer_writer
      - retailer_collaborator
    condition:
      match:
        expr: |
          (principal.retailerId == resource.retailerId) &&
          ('footprint' in resource.products)
```

### Examples
- `footprint:sites` — requires "footprint" product
- `campaigns:main` — requires "qr" product
- `content:templates` — requires "signage" product

### Important Notes
- SU and Agency users **bypass product checks** (they have their own rules allowing all)
- Only retailer-level users need product gating
- Product key is passed via `resource.products[]` array

---

## Pattern 2: Settings (Owner/Admin Only)

**Use when**: A feature is only accessible to account owners and admins.

### Pattern

```yaml
rules:
  - actions: ["view", "create", "update", "delete"]
    effect: EFFECT_ALLOW
    derivedRoles:
      - settings_manager  # owner/admin only
    condition:
      match:
        expr: 'principal.retailerId == resource.retailerId'
```

### Examples
- `settings:users` — manage team members
- `settings:general` — account settings
- `settings:product` — product configuration

### Important Notes
- Collaborators, members, and leads are **always denied**
- No product gating (base feature)
- Condition checks ownership to prevent cross-retailer access

---

## Pattern 3: Role-Based CRUD Restrictions

**Use when**: Different roles should have different action permissions.

### Pattern

```yaml
rules:
  # Collaborators: view only
  - actions: ["view"]
    effect: EFFECT_ALLOW
    derivedRoles: ["retailer_collaborator"]
    condition:
      match:
        expr: 'principal.retailerId == resource.retailerId'

  # Members and above: full CRUD
  - actions: ["view", "create", "update", "delete"]
    effect: EFFECT_ALLOW
    derivedRoles: ["retailer_writer"]
    condition:
      match:
        expr: 'principal.retailerId == resource.retailerId'
```

### Role Hierarchy

```
collaborator → view only
member       → view, create, update, delete
lead         → view, create, update, delete
admin        → view, create, update, delete
owner        → view, create, update, delete
```

### Important Notes
- Use derived role groupings to avoid repetition
- `retailer_writer` = member + lead + admin + owner
- `retailer_collaborator` = collaborator only

---

## Pattern 4: Level-Based Scoping

**Use when**: Access depends on organizational level (SU > Agency > Retailer).

### Pattern

```yaml
rules:
  # Super users can access anything
  - actions: ["view"]
    effect: EFFECT_ALLOW
    derivedRoles: ["super_user"]

  # Agency users can access their retailers' data
  - actions: ["view"]
    effect: EFFECT_ALLOW
    derivedRoles: ["agency_user"]
    condition:
      match:
        expr: 'principal.agencyId == resource.agencyId'

  # Retailer users can only access their own data
  - actions: ["view"]
    effect: EFFECT_ALLOW
    derivedRoles: ["retailer_user"]
    condition:
      match:
        expr: 'principal.retailerId == resource.retailerId'
```

### Examples
- `dashboard:su` — Super user only
- `dashboard:agency` — Agency + Super user
- `dashboard:retailer` — All authenticated users

### Important Notes
- SU users have **no conditions** (full bypass)
- Agency users check `agencyId` relationship
- Retailer users check `retailerId` equality

---

## Decision Flow Algorithm

When evaluating if a user can perform an action:

```
1. Check user level → most restrictive first
   if (principal.userLevel == "su")
       → ALLOW (no other checks)

2. Check if agency context
   if (principal.userLevel == "agency")
       → Check agencyId condition
       → If authorized, ALLOW for all child retailers

3. For product-gated resources
   if (required_product not in principal.products)
       → DENY

4. Check role restrictions
   if (action == "write" && principal.userType == "collaborator")
       → DENY

5. Check ownership/scope
   if (principal.retailerId != resource.retailerId)
       → DENY

6. Default
   → ALLOW (if reached all checks)
```

### Example Walkthrough

**Scenario**: Retailer member accessing `/content/templates` (requires "signage" product)

```
1. userLevel = "retailer"  → not SU, continue
2. userLevel = "retailer"  → not agency, continue
3. product = "signage" in products[] → YES, continue
4. action = "create", userType = "member" → allowed, continue
5. principal.retailerId == resource.retailerId → YES
→ ALLOW
```

**Scenario**: Retailer collaborator accessing `/settings/users`

```
1. userLevel = "retailer"  → not SU, continue
2. userLevel = "retailer"  → not agency, continue
3. resource.type = "settings" → requires owner/admin
4. userType = "collaborator" → NOT owner/admin
→ DENY
```

---

## Naming and Resource ID Conventions

### Resource ID Format

**Standard**: `<domain>:<feature>`

Examples:
- `footprint:sites` — footprint domain, sites feature
- `content:templates` — content domain, templates feature
- `settings:users` — settings domain, users feature
- `dashboard:retailer` — dashboard domain, retailer level

### Action Names

**Standard 4 actions**:
- `view` — read access
- `create` — add new items
- `update` — modify existing items
- `delete` — remove items

**Special cases**:
- Reports: typically `view` only
- Settings: typically `view`, `create`, `update`, `delete` (when allowed)

### Kebab-Case Rules

- All lowercase
- Hyphens for multi-word names
- No underscores, spaces, or camelCase

Examples:
- ✅ `qr-performance`
- ❌ `QR_Performance`
- ❌ `qrPerformance`

---

## Derived Roles Reference

**Available roles** in `_derived_roles.yaml`:

```yaml
super_user           # userLevel == "su"
agency_user          # userLevel == "agency"
retailer_writer      # userLevel == "retailer" AND userType in [member, lead, admin, owner]
retailer_collaborator # userLevel == "retailer" AND userType == "collaborator"
settings_manager     # userType in [owner, admin]
own_resource         # principal.retailerId == resource.retailerId
has_product          # resource.product in principal.products
```

**Use in rules**:

```yaml
rules:
  - actions: ["*"]
    effect: EFFECT_ALLOW
    derivedRoles:
      - super_user        # OR condition: SU allowed
      - agency_user       # OR condition: Agency allowed
      - retailer_writer   # OR condition: Retailer writer allowed
```

---

## AuxData Contract

**What the BFF sends** when checking permissions:

```json
{
  "jwt": {
    "retailer_products": ["footprint", "qr", "signage", "connect", "products", "reports"],
    "user_level": "retailer",
    "user_type": "owner"
  }
}
```

**What policies check**:

```yaml
# Product check (most common)
'footprint' in resource.products

# User level check (rare, use derived roles instead)
principal.userLevel == "su"

# User type check (rare, use derived roles instead)
principal.userType == "owner"
```

---

## Common Pitfalls & How to Avoid

### Pitfall 1: Forgetting SU Bypass

❌ **Bad**: Gating SU access by product
```yaml
condition:
  match:
    expr: "'footprint' in principal.products"
```

✅ **Good**: Rule for SU with no conditions, separate rule for retailers with product check
```yaml
- actions: ["*"]
  effect: EFFECT_ALLOW
  derivedRoles: ["super_user"]

- actions: ["*"]
  effect: EFFECT_ALLOW
  derivedRoles: ["retailer_writer"]
  condition:
    match:
      expr: "'footprint' in principal.products"
```

### Pitfall 2: Missing Ownership Check

❌ **Bad**: Allowing cross-retailer access
```yaml
- actions: ["view"]
  effect: EFFECT_ALLOW
  derivedRoles: ["retailer_user"]
```

✅ **Good**: Checking retailerId match
```yaml
- actions: ["view"]
  effect: EFFECT_ALLOW
  derivedRoles: ["retailer_user"]
  condition:
    match:
      expr: 'principal.retailerId == resource.retailerId'
```

### Pitfall 3: Forgetting Collaborator Read-Only

❌ **Bad**: Same permissions for all roles
```yaml
- actions: ["view", "create", "update", "delete"]
  effect: EFFECT_ALLOW
  derivedRoles: ["retailer_collaborator", "retailer_writer"]
```

✅ **Good**: Separate rules for collaborator vs writer
```yaml
- actions: ["view"]
  effect: EFFECT_ALLOW
  derivedRoles: ["retailer_collaborator"]

- actions: ["view", "create", "update", "delete"]
  effect: EFFECT_ALLOW
  derivedRoles: ["retailer_writer"]
```

---

## Testing Strategies

### User Profile Combinations to Test

For each new resource, verify these combinations:

| userLevel | userType | Product | Expected Result |
|-----------|----------|---------|-----------------|
| su | owner | any | ✅ Allow |
| su | member | any | ✅ Allow |
| agency | owner | any | ✅ Allow |
| agency | member | any | ✅ Allow |
| retailer | owner | ✅ has | ✅ Allow all |
| retailer | owner | ❌ not has | ❌ Deny |
| retailer | member | ✅ has | ✅ Allow all |
| retailer | member | ❌ not has | ❌ Deny |
| retailer | collaborator | ✅ has | ✅ Allow view |
| retailer | collaborator | ❌ not has | ❌ Deny |

### Manual Testing

Using Cerbos Playground at `http://localhost:3592`:

1. Set Principal: user level, type, id, agency_id
2. Set Resource: type, id, owner_id, products array
3. Set Aux Data: retailer_products array
4. Check Action: view, create, update, delete
5. Verify Result: ALLOW or DENY

---

## References

- **Cerbos Docs**: https://docs.cerbos.dev/
- **Cerbos Condition Language**: https://docs.cerbos.dev/latest/policies/conditions
- **Legacy Reference**: See `LEGACY_PATTERNS.md` for all 41 resources and mappings
