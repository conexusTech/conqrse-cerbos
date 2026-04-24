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

## Resources by Product

### Connect Product

| Resource | Type | Actions |
|----------|------|---------|
| `connect:contacts` | Collection | list, view, create, update, delete, export, import |

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

### Signage Product

| Resource | Type | Actions |
|----------|------|---------|
| `signage:content:templates` | Collection | list, view, create, update, delete, export, import |
| `signage:content:templates:create` | Action | create |
| `signage:content:templates:item` | Item | view, update, delete |
| `signage:content:assets` | Collection | list, view, create, update, delete, export, import |
| `signage:content:assets:create-template` | Action | create |
| `signage:content:assets:create-content-template` | Action | create |
| `signage:content:playlists` | Collection | list, view, create, update, delete, export, import |
| `signage:content:playlists:item:manage` | Item | view, update, delete |
| `signage:content:backgrounds` | Collection | list, view, create, update, delete, export, import |
| `signage:content:channels` | Collection | list, view, create, update, delete, export, import |
| `signage:content:channels:add` | Action | create |
| `signage:content:channels:item` | Item | view, update, delete |
| `signage:content:tags` | Collection | list, view, create, update, delete, export, import |
| `signage:content:content-groups` | Collection | list, view, create, update, delete, export, import |
| `signage:content:content-groups:item` | Item | view, update, delete |
| `signage:signage:people` | Collection | list, view, create, update, delete, export, import |
| `signage:signage:places` | Collection | list, view, create, update, delete, export, import |
| `signage:signage:things` | Collection | list, view, create, update, delete, export, import |

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

### Reports Product

| Resource | Type | Actions |
|----------|------|---------|
| `reports` | Root | list, view |
| `reports:qr-performance` | Collection | list, view, export |
| `reports:qr-performance-site-to-site` | Collection | list, view, export |
| `reports:campaign-compliance` | Collection | list, view, export |
| `reports:campaign-compliance-details` | Collection | list, view, export |
| `reports:site-performance-maps` | Collection | list, view, export |
| `reports:media-performance-maps` | Collection | list, view, export |
| `reports:campaign-performance-maps` | Collection | list, view, export |
| `reports:content-proof-of-play` | Collection | list, view, export |
| `reports:export` | Collection | export |

### Dashboards (Non-Product)

| Resource | Type | Actions |
|----------|------|---------|
| `dashboards:su-dashboard` | Dashboard | view |
| `dashboards:agency-dashboard` | Dashboard | view |
| `dashboards:retailer-dashboard` | Dashboard | view |

### Permission Management (Non-Product)

| Resource | Type | Actions |
|----------|------|---------|
| `permission` | Settings | list, view, create, update, delete, export, import |

### Settings - Admin

| Resource | Type | Actions |
|----------|------|---------|
| `settings:admin:general` | Settings | list, view, create, update, delete |
| `settings:admin:users` | Settings | list, view, create, update, delete, export, import |
| `settings:admin:teams` | Settings | list, view, create, update, delete, export, import |
| `settings:admin:acting-as` | Settings | view |

### Settings - User

| Resource | Type | Actions |
|----------|------|---------|
| `settings:user:profile` | Settings | list, view, update |

### Settings - Footprints

| Resource | Type | Actions |
|----------|------|---------|
| `settings:footprints:sites:property` | Settings | list, view, create, update, delete, export, import |
| `settings:footprints:sites:property:item` | Item | view, update, delete |
| `settings:footprints:products:property` | Settings | list, view, create, update, delete, export, import |
| `settings:footprints:products:property:item` | Item | view, update, delete |
| `settings:footprints:products:pricing-group` | Settings | list, view, create, update, delete, export, import |
| `settings:footprints:products:pricing-group:item` | Item | view, update, delete |

### Settings - QR

| Resource | Type | Actions |
|----------|------|---------|
| `settings:qr` | Settings | list, view, create, update, delete |
| `settings:qr:design` | Settings | list, view, create, update, delete, export, import |
| `settings:qr:design:item` | Item | view, update, delete |
| `settings:qr:power-tag` | Settings | list, view, create, update, delete, export, import |
| `settings:qr:power-tag:item` | Item | view, update, delete |
| `settings:qr:default-redirect` | Settings | list, view, create, update, delete |
| `settings:qr:domain` | Settings | list, view, create, update, delete, export, import |
| `settings:qr:domain:item` | Item | view, update, delete |

### Settings - Signage

| Resource | Type | Actions |
|----------|------|---------|
| `settings:signage` | Settings | list, view, create, update, delete |
| `settings:signage:layout` | Settings | list, view, create, update, delete, export, import |
| `settings:signage:layout:item` | Item | view, update, delete |
| `settings:signage:people:property` | Settings | list, view, create, update, delete, export, import |
| `settings:signage:people:property:item` | Item | view, update, delete |
| `settings:signage:places:property` | Settings | list, view, create, update, delete, export, import |
| `settings:signage:places:property:item` | Item | view, update, delete |
| `settings:signage:things:property` | Settings | list, view, create, update, delete, export, import |
| `settings:signage:things:property:item` | Item | view, update, delete |

---

## Summary Statistics

- **Total Resources**: 71
- **Collection Resources**: 49
- **Item Resources**: 17
- **Action Resources**: 5
- **Total Unique Resource:Action Combinations**: Varies by role and conditions

### Action Coverage

| Action | Count | Scope |
|--------|-------|-------|
| `list` | 49 | resource |
| `view` | 70 | resource |
| `create` | 47 | resource |
| `update` | 47 | resource |
| `delete` | 47 | resource |
| `export` | 32 | resource |
| `import` | 20 | resource |
| Settings actions | 4 per resource | settings |

---

## Resource Type Definitions

- **Collection**: Full CRUD operations (list, view, create, update, delete), plus export/import
- **Item**: Detail view and mutations (view, update, delete)
- **Action**: Specific operation triggers (e.g., create-template)
- **Settings**: Configuration management with settings scope (list, create, update, delete)
- **Dashboard**: Read-only dashboard views (view only)

---

## Access Control Notes

1. **Product Resources** (`footprints:*`, `signage:*`, `qr:*`, `reports:*`, `connect:*`):
   - Retailer-scoped and require product subscription validation
   - Require proper `retailerId` in request
   - Support delegation via "Act AS" model

2. **Settings Resources**:
   - Cross-cutting concern, managed centrally
   - May have stricter access control (e.g., admin-only)
   - User settings are personal to the authenticated user

3. **Dashboard Resources**:
   - Read-only, role-based visibility
   - No modification actions allowed

4. **Permission Resource**:
   - Special management resource for permission administration
   - Typically restricted to system admins
