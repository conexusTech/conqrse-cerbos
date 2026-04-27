# Resources × Product × Actions Matrix

This document provides a comprehensive matrix of all Cerbos resources and their supported actions.

## Products

- **qr** - QR Code
- **priceTags** - Pricing
- **compliance** - Compliance
- **product** - Product 
- **signage** - Signages
- **landing** - Landing
- **connect** - Connect
- **ppt** - People, Places, and Things

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

### Reports Resource

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

### Footprints Resource

| Resource | Type | Actions |
|----------|------|---------|
| `footprints:sites` | Collection | list, view, create, update, delete, export, import |
| `footprints:sites:item` | Item | view, update, delete |
| `footprints:endpoints` | Collection | list, view, create, update, delete, export, import |
| `footprints:endpoints:item` | Item | view, update, delete |
| `footprints:products` | Collection | list, view, create, update, delete, export, import |
| `footprints:products:item` | Item | view, update, delete |
| `footprints:pricing` | Collection | list, view, create, update, delete, export, import |

### Content Management Resource

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

### Signage Resource

| Resource | Type | Actions |
|----------|------|---------|
| `signages:people` | Collection | list, view, create, update, delete, export, import |
| `signages:people:item` | Item | view, update, delete |
| `signages:places` | Collection | list, view, create, update, delete, export, import |
| `signages:places:item` | Item | view, update, delete |
| `signages:things` | Collection | list, view, create, update, delete, export, import |
| `signages:things:item` | Item | view, update, delete |

### Connect Resource

| Resource | Type | Actions |
|----------|------|---------|
| `connect:contacts` | Collection | list, view, create, update, delete, export, import |
| `connect:contacts:item` | Item | view, update, delete |

### QR Resource

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

## Product × Resource Matrix

| Resource | default | qr | priceTags | compliance | product | signage | landing | connect | ppt |
|--------|---------|----|-----------|-----------|---------|---------|---------|---------|----|
| connect:contacts:list | | | | | | | | required | |
| connect:contacts:item | | | | | | | | required | |
| contents:assets:list | | | | | | | required | | |
| contents:assets:item | | | | | | | required | | |
| contents:backgrounds:list | | | | | | | required | | |
| contents:backgrounds:item | | | | | | | required | | |
| contents:backgrounds:transistion:list | | | | | | | required | | |
| contents:backgrounds:transistion:item | | | | | | | required | | |
| contents:channels:list | | | | | | | required | | |
| contents:channels:item | | | | | | | required | | |
| contents:content-groups:list | | | | | | | required | | |
| contents:content-groups:item | | | | | | | required | | |
| contents:playlists:list | | | | | | | required | | |
| contents:playlists:item | | | | | | | required | | |
| contents:tags:list | | required | required | required | required | required | | | |
| contents:tags:assignments | | required | required | required | required | required | | | |
| contents:tags:item | | required | required | required | required | required | | | |
| contents:templates:list | | | required | | | required | | | |
| contents:templates:item | | | required | | | required | | | |
| footprints:endpoints:list | | | required | | | required | | | |
| footprints:endpoints:item | | | required | | | required | | | |
| footprints:pricing:list | | | required | | required | required | | | |
| footprints:products:list | | | required | required | required | required | | | |
| footprints:products:item | | | required | required | required | required | | | |
| footprints:sites:list | | required | required | required | required | required | | | |
| footprints:sites:item | | required | required | required | required | required | | | |
| qr:campaigns:list | | required | required | required | required | required | required | required | required |
| qr:campaigns:item | | required | required | required | required | required | required | required | required |
| qr:media:list | | required | | | | | | | |
| qr:media:item | | required | | | | | | | |
| qr:site:list | | required | | | | | | | |
| qr:site:item | | required | | | | | | | |
| qr:templates:list | | required | | | | | | | |
| qr:templates:item | | required | | | | | | | |
| reports:campaign-compliance-details:list | | required | | required | | required | | | |
| reports:campaign-compliance:list | | required | | required | | required | | | |
| reports:campaign-performance-maps:list | | required | | required | | required | | | |
| reports:content-proof-of-play:list | | | | | | | required | | |
| reports:media-performance-maps:list | | required | | | | | | | |
| reports:qr-performance-site-to-site:list | | required | | | | | | | |
| reports:qr-performance:list | | required | | | | | | | |
| reports:site-performance-maps:list | | required | | | | | | | |
| reports:erequiredport | | required | | required | required | required | | required | |
| settings:admin:cerbos:list | required | | | | | | | | |
| settings:admin:general:list | required | | | | | | | | |
| settings:admin:teams:list | required | | | | | | | | |
| settings:admin:users:list | required | | | | | | | | |
| settings:footprints_products_pricing_group:list | | | required | | required | | | | |
| settings:footprints_products_pricing_group:item | | | required | | required | | | | |
| settings:footprints_products_property:list | | | required | required | required | | | | |
| settings:footprints_products_property:item | | | required | required | required | | | | |
| settings:footprints_sites_property:list | | required | required | required | | | | | |
| settings:footprints_sites_property:item | | required | required | required | | | | | |
| settings:qr_default-redirect:list | | required | | | | | | | |
| settings:qr_design:list | | required | | | | | | | |
| settings:qr_design:item | | required | | | | | | | |
| settings:qr_domain:list | | required | | | | | | | |
| settings:qr_domain:item | | required | | | | | | | |
| settings:qr_power-tag:list | | required | | | | | | | |
| settings:qr_power-tag:item | | required | | | | | | | |
| settings:signage_layout:list | | | | | | required | | | |
| settings:signage_layout:item | | | | | | required | | | |
| settings:signage_people_property:list | | | | | | | | | required |
| settings:signage_people_property:item | | | | | | | | | required |
| settings:signage_places_property:list | | | | | | | | | required |
| settings:signage_places_property:item | | | | | | | | | required |
| settings:signage_things_property:list | | | | | | | | | required |
| settings:signage_things_property:item | | | | | | | | | required |
| settings:user:profile:list | required | | | | | | | | |
| signages:people:list | | | | | | required | | | required |
| signages:people:item | | | | | | required | | | required |
| signages:places:list | | | | | | required | | | required |
| signages:places:item | | | | | | required | | | required |
| signages:things:list | | | | | | required | | | required |
| signages:things:item | | | | | | required | | | required |

---

## Access Control Notes

1. **Resource Segment** The first segment is called group, each features has its own groupings.

Example #1: `settings:signage_layout`
- `settings` is the group where `signage_layout` feature belongs to.

Example #2: `connect:contacts:item`
- `contacts` is a feature under the grouping `connect`
- `item` indicates that the resource is pertaining to a resource item, otherwise resource collection.

2. **Main Groupings**

- `footprints:*`
- `signages:*`
- `qr:*`
- `reports:*`
- `connect:*`
- `settings:*`
- `contents:*`
   
3. **Retailer-scoped** - A resource requires a retailer data. It is scoped to retailer-only resources.
4. **Product Validation** - A retailer-scoped resource also requires product validation. It means, the subject retailer must have the required products (listed in the Resource payload) to have access to it. See "Product x Resource Matrix".

5. **Cerbos Payload**

Principal

```json
{
   "id": string - the ID of the logged in user,
   "roles": string[] - derived roles, see "k8s/base/policies/_derived_roles.yaml",
   "attr": {
      "userLevel": 'retailer', 'su', 'agency' or 'user',
      "userType": 'admin', 'collaborator', 'owner', 'lead', or 'member',
      "name": string,
      "products": string[] - list of known products (qr, priceTags, compliance, product, signage, landing, connect, ppt),
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
      "products": string[] - required products the retailer must have to have access to the resource,
   },
}
```