# Cerbos Policy Structure Guide

This document covers how Cerbos policies are structured, how derived roles work, and how to add new resources.

---

## Permission Key Format

All permissions follow the pattern:

```
${productType}:${resource}:${action}
```

Examples:
- `footprint:sites:view`
- `signage:channels:create`
- `settings:general:edit`
- `reports:export:export`

---

## Policy File Types

### 1. Derived Roles (`_derived_roles.yaml`)

Derived roles map user attributes to logical roles used in resource policies. They are evaluated at request time based on the principal's attributes.

```yaml
apiVersion: "api.cerbos.dev/v1"
derivedRoles:
  name: conqrse_roles
  definitions:
    - name: role_name
      parentRoles: ["authenticated"]
      condition:
        match:
          expr: <CEL expression>
```

**Key attributes used in conditions:**
- `P.attr.userLevel` -- organizational scope (`su`, `agency`, `retailer`)
- `P.attr.userType` -- action permissions (`owner`, `admin`, `lead`, `member`, `collaborator`)
- `P.attr.retailerId` -- principal's retailer ID
- `P.attr.products` -- list of products the principal has access to
- `R.attr.retailerId` -- resource's owning retailer ID
- `R.attr.product` -- product type of the resource

### 2. Resource Policies (`resource_*.yaml`)

Resource policies define which derived roles can perform which actions on a resource.

```yaml
apiVersion: "api.cerbos.dev/v1"
resourcePolicy:
  version: default
  importDerivedRoles:
    - conqrse_roles
  resource: "resource_name"
  rules:
    - actions: ["view", "create", "edit", "delete"]
      effect: EFFECT_ALLOW
      derivedRoles:
        - super_user
      condition:           # optional
        match:
          expr: <CEL expression>
```

---

## Derived Roles Reference

| Role | Condition | Purpose |
|------|-----------|---------|
| `super_user` | `userLevel == "su"` | Full access to everything |
| `agency_user` | `userLevel == "agency"` | Full access, product check bypassed |
| `retailer_writer` | `userLevel == "retailer"` AND `userType in [owner, admin, lead, member]` | Full CRUD on own resources with product access |
| `retailer_collaborator` | `userLevel == "retailer"` AND `userType == "collaborator"` | Read-only on own resources with product access |
| `settings_manager` | `userType in [owner, admin]` | Can manage product and general settings |
| `own_resource` | `principal.retailerId == resource.retailerId` | Ownership check |
| `has_product` | `resource.product in principal.products` | Product subscription check |

---

## Decision Flow

```
1. Is userLevel == 'su'?
   YES -> ALLOW all actions on all resources

2. Is userLevel == 'agency'?
   YES -> ALLOW all actions on child retailer data

3. Is this a settings resource?
   Is settingsType == 'personal'?
     YES -> ALLOW view + edit for all authenticated
   Is userType in [owner, admin]?
     YES -> ALLOW (product/general settings)
   NO -> DENY

4. Does retailer.products contain the product?
   NO -> DENY
   YES:
     Is userType == 'collaborator'?
       YES -> ALLOW view only
     NO -> ALLOW all actions
```

---

## Available Actions

| Action | Description |
|--------|-------------|
| `view` | Read/view resource |
| `create` | Create new resource |
| `edit` | Update/modify resource |
| `delete` | Delete/remove resource |
| `upload` | Upload files |
| `download` | Download files |
| `report` | Generate reports |
| `export` | Export data |

---

## How to Add a New Resource

### 1. Create or edit a policy file

For a new product resource, either add to `resource_product.yaml` or create a new file (e.g., `resource_myfeature.yaml`):

```yaml
---
apiVersion: "api.cerbos.dev/v1"
resourcePolicy:
  version: default
  importDerivedRoles:
    - conqrse_roles
  resource: "myproduct:myresource"
  rules:
    # SU -- full access
    - actions: ["view", "create", "edit", "delete"]
      effect: EFFECT_ALLOW
      derivedRoles:
        - super_user

    # Agency -- full access
    - actions: ["view", "create", "edit", "delete"]
      effect: EFFECT_ALLOW
      derivedRoles:
        - agency_user

    # Retailer writer -- full access on own resource with product
    - actions: ["view", "create", "edit", "delete"]
      effect: EFFECT_ALLOW
      derivedRoles:
        - retailer_writer
      condition:
        match:
          all:
            of:
              - expr: P.attr.retailerId == R.attr.retailerId
              - expr: R.attr.product in P.attr.products

    # Retailer collaborator -- view only on own resource with product
    - actions: ["view"]
      effect: EFFECT_ALLOW
      derivedRoles:
        - retailer_collaborator
      condition:
        match:
          all:
            of:
              - expr: P.attr.retailerId == R.attr.retailerId
              - expr: R.attr.product in P.attr.products
```

### 2. Restart Cerbos

```bash
docker-compose restart
```

Or if `watchForChanges: true` is set, Cerbos will pick up changes automatically.

### 3. Wire up in frontend and backend

- **Frontend**: Use `<CanI resource="myproduct:myresource" action="view">` in `conqrse-admin`
- **Backend**: Use `@RequirePermission('myproduct:myresource', 'view')` in `conqrse-api3`

---

## YAML Schema Notes

- `apiVersion` must be `"api.cerbos.dev/v1"`
- `resourcePolicy.version` is typically `"default"`
- `importDerivedRoles` must reference `conqrse_roles` (defined in `_derived_roles.yaml`)
- Conditions use [CEL (Common Expression Language)](https://github.com/google/cel-spec)
- `P` is shorthand for the principal (user), `R` for the resource
- `effect` must be `EFFECT_ALLOW` or `EFFECT_DENY`
