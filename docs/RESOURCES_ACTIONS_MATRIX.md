# Resources × Actions Matrix

This document provides a comprehensive matrix of all Cerbos resources and their supported actions.

## Action Definitions

### Resource Actions (scope: `resource:`)
- `resource:list` — View collection of resources with filters and pagination
- `resource:view` — View individual resource details
- `resource:create` — Create new resources
- `resource:update` — Modify existing resources
- `resource:delete` — Remove resources
- `resource:export` — Download/export resource data
- `resource:import` — Upload/import data

### Settings Actions (scope: `settings:`)
- `settings:list` — View collection of settings
- `settings:create` — Create new settings
- `settings:update` — Modify existing settings
- `settings:delete` — Remove settings

---

## Non-Product Related Resources

These are the resources that doesn't need product and retailer validation.

### Settings - Admin

| Resource | Type | Actions |
|----------|------|---------|
| `settings:admin:general` | Settings | list, view, create, update, delete |
| `settings:admin:users` | Settings | list, view, create, update, delete, export, import |
| `settings:admin:teams` | Settings | list, view, create, update, delete, export, import |
| `settings:admin:cerbos` | Settings | list, view, update, export, import |

### Settings - User

| Resource | Type | Actions |
|----------|------|---------|
| `settings:user:profile` | Settings | list, view, update |

## Product Related Resources

### Reports Product

| Resource | Type | Actions |
|----------|------|---------|
| `reports:qr-performance` | Collection | list, view, export |
| `reports:qr-performance-site-to-site` | Collection | list, view, export |
| `reports:campaign-compliance` | Collection | list, view, export |
| `reports:campaign-compliance-details` | Collection | list, view, export |
| `reports:site-performance-maps` | Collection | list, view, export |
| `reports:media-performance-maps` | Collection | list, view, export |
| `reports:campaign-performance-maps` | Collection | list, view, export |
| `reports:content-proof-of-play` | Collection | list, view, export |
| `reports:export` | Collection | export |

### Footprints Product

| Resource | Type | Actions |
|----------|------|---------|
| `footprints:sites` | Collection | list, view, create, update, delete, export, import |
| `footprints:sites:item` | Item | view, update, delete |
| `footprints:endpoints` | Collection | list, view, create, update, delete, export, import |
| `footprints:endpoints:item` | Item | view, update, delete |
| `footprints:products` | Collection | list, view, create, update, delete, export, import |
| `footprints:products:item` | Item | view, update, delete |
| `footprints:pricing` | Collection | list, view, create, update, delete, export, import |

### Content Management Product

| Resource | Type | Actions |
|----------|------|---------|
| `contents:templates` | Collection | list, view, create, update, delete, export, import |
| `contents:templates:item` | Item | view, update, delete |
| `contents:assets` | Collection | list, view, create, update, delete, export, import |
| `contents:assets:item` | Item | view, update, delete |
| `contents:playlists` | Collection | list, view, create, update, delete, export, import |
| `contents:playlists:item` | Item | view, update, delete |
| `contents:backgrounds` | Collection | list, view, create, update, delete, export, import |
| `contents:backgrounds:item` | Item | view, update, delete |
| `contents:backgrounds:transistion` | Collection | list, view, create, update, delete, export, import |
| `contents:backgrounds:transistion:item` | Item | view, update, delete |
| `contents:channels` | Collection | list, view, create, update, delete, export, import |
| `contents:channels:item` | Item | view, update, delete |
| `contents:tags` | Collection | list, view, create, update, delete, export, import |
| `contents:tags:item` | Item | view, update, delete |
| `contents:tags:assignments` | Item | view, update, delete |
| `contents:content-groups` | Collection | list, view, create, update, delete, export, import |
| `contents:content-groups:item` | Item | view, update, delete |

### Signage Product

| Resource | Type | Actions |
|----------|------|---------|
| `signages:people` | Collection | list, view, create, update, delete, export, import |
| `signages:people:item` | Item | view, update, delete |
| `signages:places` | Collection | list, view, create, update, delete, export, import |
| `signages:places:item` | Item | view, update, delete |
| `signages:things` | Collection | list, view, create, update, delete, export, import |
| `signages:things:item` | Item | view, update, delete |

### Connect Product

| Resource | Type | Actions |
|----------|------|---------|
| `connect:contacts` | Collection | list, view, create, update, delete, export, import |
| `connect:contacts:item` | Item | view, update, delete |

### QR Product

| Resource | Type | Actions |
|----------|------|---------|
| `qr:site` | Collection | list, view, create, update, delete, export, import |
| `qr:site:item` | Item | view, update, delete |
| `qr:media` | Collection | list, view, create, update, delete, export, import |
| `qr:media:item` | Item | view, update, delete |
| `qr:templates` | Collection | list, view, create, update, delete, export, import |
| `qr:templates:item` | Item | view, update, delete |
| `qr:campaigns` | Collection | list, view, create, update, delete, export, import |
| `qr:campaigns:item` | Item | view, update, delete |

## Product Settings Related Resources

### Settings - Footprints

| Resource | Type | Actions |
|----------|------|---------|
| `settings:footprints_sites_property` | Collection | list, view, create, update, delete, export, import |
| `settings:footprints_sites_property:item` | Item | view, update, delete |
| `settings:footprints_products_property` | Collection | list, view, create, update, delete, export, import |
| `settings:footprints_products_property:item` | Item | view, update, delete |
| `settings:footprints_products_pricing_group` | Collection | list, view, create, update, delete, export, import |
| `settings:footprints_products_pricing_group:item` | Item | view, update, delete |

### Settings - QR

| Resource | Type | Actions |
|----------|------|---------|
| `settings:qr_design` | Collection | list, view, create, update, delete, export, import |
| `settings:qr_design:item` | Item | view, update, delete |
| `settings:qr_power-tag` | Collection | list, view, create, update, delete, export, import |
| `settings:qr_power-tag:item` | Item | view, update, delete |
| `settings:qr_default-redirect` | Collection | list, view, create, update, delete |
| `settings:qr_domain` | Collection | list, view, create, update, delete, export, import |
| `settings:qr_domain:item` | Item | view, update, delete |

### Settings - Signage

| Resource | Type | Actions |
|----------|------|---------|
| `settings:signage_layout` | Collection | list, view, create, update, delete, export, import |
| `settings:signage_layout:item` | Item | view, update, delete |
| `settings:signage_people_property` | Collection | list, view, create, update, delete, export, import |
| `settings:signage_people_property:item` | Item | view, update, delete |
| `settings:signage_places_property` | Collection | list, view, create, update, delete, export, import |
| `settings:signage_places_property:item` | Item | view, update, delete |
| `settings:signage_things_property` | Collection | list, view, create, update, delete, export, import |
| `settings:signage_things_property:item` | Item | view, update, delete |

---

## Resource Type Definitions

- **Collection**: Full CRUD operations (list, view, create, update, delete), plus export/import
- **Item**: Detail view and mutations (view, update, delete)
- **Action**: Specific operation triggers (e.g., create-template)

---

## Access Control Notes

1. **Resource Segment** Product in a resource is the first segment. Example, `settings:signage_layout`, the product is `settings`. Another example, `qr:templates:item`, the product is `qr`. The second and third segments are the features of the given product. Example, `connect:contacts:item`, `contacts` is a feature in product `connect`, where the `item` indicates that the resource is pertaining to a resource item, otherwise resource collection.

2. **Product Resources** (`footprints:*`, `signages:*`, `qr:*`, `reports:*`, `connect:*`, `settings:*`, `contents:*`):
   - Retailer-scoped and require product subscription validation
   - Require proper `retailerId` in request

3. **Cerbos Payload**

Principal

```text
{
   "id": string - the ID of the logged in user,
   "roles": string[] - derived roles, see "k8s/base/policies/_derived_roles.yaml",
   "attr": {
      "userLevel": 'retailer', 'su', 'agency' or 'user',
      "userType": 'admin', 'collaborator', 'owner', 'lead', and 'member',
      "name": string,
      "products": list of known products (footprints, signages, qr, reports, connect, settings, contents),
      "agencyId": string - retailer's agency ID,
      "retailerId": string - the retailer in subject,
   }
}
```
Resource

```json
{
   "id": string - the resource in subject,
   "kind": string - the resource in subject,
   "attr": {
      "retailerId": string - the retailer of the resource,
      "product": string,
   },
}
```