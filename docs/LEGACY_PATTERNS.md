# Legacy Patterns & Migration Reference

This document preserves architectural patterns and knowledge from the previous `old/` Cerbos policy structure, which has been consolidated into the current resource-based authorization model.

---

## Overview of Previous Structure

The legacy system used **page-centric policies** with granular, domain-specific policy files organized by product/feature:

```
old/resource_policies/
├── page_dashboard.yaml      (3 dashboard resources)
├── page_reports.yaml        (9 report resources)
├── page_footprint.yaml      (4 footprint resources)
├── page_content.yaml        (7 content resources)
├── page_products.yaml       (4 product resources)
├── page_signage.yaml        (2 signage resources)
├── page_connect.yaml        (1 connect resource)
├── page_campaigns.yaml      (1 campaign resource)
├── page_data.yaml           (2 data resources)
├── page_settings.yaml       (10 settings resources)
└── menu.yaml                (sidebar visibility)
```

This was **refactored** to a **resource-centric model** with consolidated policy files:

```
current/policies/
├── resource_product.yaml    (products + campaigns + reports)
├── resource_settings.yaml   (all settings pages)
├── resource_profile.yaml    (dashboards)
└── _derived_roles.yaml      (role definitions)
```

---

## Complete Product-to-Page Mapping

This mapping was previously documented in `PERMISSIONS.md` and serves as the authoritative reference for all features across the Conqrse platform.

### Footprint Product

| Resource ID | Route | Actions |
|-------------|-------|---------|
| `footprint:sites` | `/footprint/sites`, `/footprint/sites/[id]` | view, create, update, delete |
| `footprint:endpoints` | `/footprint/endpoints`, `/footprint/endpoints/[id]` | view, create, update, delete |
| `footprint:products` | `/footprint/products` | view, create, update, delete |
| `footprint:pricing` | `/footprint/pricing` | view, create, update, delete |

### Signage Product (Content + Signage)

| Resource ID | Route | Actions |
|-------------|-------|---------|
| `content:templates` | `/content/templates`, `/content/templates/create`, `/content/templates/[id]` | view, create, update, delete |
| `content:assets` | `/content/assets`, `/content/assets/create-template` | view, create, update, delete |
| `content:playlists` | `/content/playlists`, `/content/playlists/[id]/manage` | view, create, update, delete |
| `content:backgrounds` | `/content/backgrounds` | view, create, update, delete |
| `content:channels` | `/content/channels`, `/content/channels/add`, `/content/channels/[id]` | view, create, update, delete |
| `content:tags` | `/content/tags` | view, create, update, delete |
| `content:content-groups` | `/content/content-groups`, `/content/content-groups/[id]` | view, create, update, delete |
| `signage:people-places-things` | `/signage/people-places-things` | view, create, update, delete |
| `signage:layouts` | `/signages/layouts` | view, create, update, delete |

### Products Product

| Resource ID | Route | Actions |
|-------------|-------|---------|
| `products:details` | `/products/details`, `/products/[id]` | view, create, update, delete |
| `products:pricing` | `/products/pricing` | view, create, update, delete |
| `products:promotions` | `/products/promotions`, `/products/promotions/promotion-creation` | view, create, update, delete |
| `products:properties` | `/products/properties` | view, create, update, delete |

### QR Product (Campaigns)

| Resource ID | Route | Actions |
|-------------|-------|---------|
| `campaigns:main` | `/campaigns` | view, create, update, delete |

### Reports Product

| Resource ID | Route | Actions |
|-------------|-------|---------|
| `reports:qr-performance` | `/reports/qr-performance` | view |
| `reports:qr-performance-site-to-site` | `/reports/qr-performance-site-to-site` | view |
| `reports:campaign-compliance` | `/reports/campaign-compliance` | view |
| `reports:campaign-compliance-details` | `/reports/campaign-compliance-details` | view |
| `reports:site-performance-maps` | `/reports/site-performance-maps` | view |
| `reports:media-performance-maps` | `/reports/media-performance-maps` | view |
| `reports:campaign-performance-maps` | `/reports/campaign-performance-maps` | view |
| `reports:content-proof-of-play` | `/reports/content-proof-of-play` | view |
| `reports:export` | `/export` | view |

### Connect Product

| Resource ID | Route | Actions |
|-------------|-------|---------|
| `connect:contacts` | `/connect/contacts`, `/connect/contacts/contact-list`, `/connect/contacts/[campaignId]/contact-list` | view, create, update, delete |
| `data:business-cards` | `/data/business-cards` | view, create, update, delete |
| `data:connect` | `/data/connect` | view, create, update, delete |

### Dashboards (No Product Required)

| Resource ID | Route | Restriction |
|-------------|-------|-------------|
| `dashboard:su` | `/su-dashboard` | **userLevel = su only** |
| `dashboard:agency` | `/agency-dashboard` | **userLevel = agency or su** |
| `dashboard:retailer` | `/retailer-dashboard` | All authenticated users |

### Settings (No Product, Role-Restricted)

| Resource ID | Route | Restriction |
|-------------|-------|-------------|
| `settings:general` | `/settings/general` | **owner/admin only** |
| `settings:footprint` | `/settings/footprint` | **owner/admin only** |
| `settings:menu` | `/settings/menu` | **owner/admin only** |
| `settings:price-tag` | `/settings/price-tag` | **owner/admin only** |
| `settings:product` | `/settings/product` | **owner/admin only** |
| `settings:properties-manager` | `/settings/properties-manager` | **owner/admin only** |
| `settings:qr` | `/settings/qr` | **owner/admin only** |
| `settings:signage` | `/settings/signage` | **owner/admin only** |
| `settings:teams` | `/settings/teams` | **owner/admin only** |
| `settings:users` | `/settings/users` | **owner/admin only** |

---

## Core Permission Model

### Two User Dimensions

| Dimension | Values | Purpose |
|-----------|--------|---------|
| **userLevel** | `su`, `agency`, `retailer` | Organizational scope — what data you can see |
| **userType** | `owner`, `admin`, `lead`, `member`, `collaborator` | Permission role — what actions you can perform |

### User Level Scoping

| Level | Data Access |
|-------|-------------|
| **su** (Super User) | All agencies + all retailers. Bypasses all product checks. |
| **agency** | All retailers that are children of their agency. Bypasses product checks. |
| **retailer** | Own retailer data only. Restricted by `retailer.products[]`. |

### Role-Based Action Restrictions

| Role | View Pages | Create/Edit/Delete | Settings Pages |
|------|-----------|-------------------|----------------|
| **owner** | Yes | Yes | Yes |
| **admin** | Yes | Yes | Yes |
| **lead** | Yes | Yes | **No** |
| **member** | Yes | Yes | **No** |
| **collaborator** | Yes | **No (read-only)** | **No** |

---

## Permission Decision Flow

```
1. Is user SU?
   └─ YES → ALLOW (bypasses everything)

2. Is user Agency?
   └─ YES → ALLOW for all child retailer data (bypasses product check)

3. Is this a Settings page?
   ├─ Is user owner or admin? → ALLOW
   └─ Otherwise → DENY

4. Does retailer have the required product?
   ├─ NO → DENY
   └─ YES:
       ├─ Is user collaborator? → ALLOW view only (read-only)
       └─ Is user member+? → ALLOW view + create + update + delete
```

### Example: Retailer member visiting `/content/templates`

1. userLevel = retailer → not SU, not agency
2. Resource = `content:templates`, requires product
3. Check `"signage" in retailer_products` → if YES, continue
4. userType = member → ALLOW view + create + update + delete

### Example: Retailer collaborator visiting `/settings/users`

1. userLevel = retailer → not SU, not agency
2. Resource = `settings:users` → requires owner/admin
3. userType = collaborator → **DENY**

---

## Policy Naming Conventions

### Resource Formats

**Page-centric (legacy):**
- Format: `page:<domain>`
- Examples: `page:dashboard`, `page:content`, `page:settings`

**Resource-centric (current):**
- Format: `<domain>:<resource>`
- Examples: `content:templates`, `settings:users`, `reports:qr-performance`

### Naming Rules

1. **Kebab-case**: All IDs use kebab-case (lowercase with hyphens)
2. **Descriptive**: Resource IDs describe the specific page/feature
3. **Product-scoped**: Resources grouped by product for clarity
4. **Action names**: Standard actions are `view`, `create`, `update`, `delete`

### Menu ID Format (Legacy)

Format: `menu:<domain>-<item>`

Examples:
- `menu:footprint-sites`
- `menu:content-templates`
- `menu:settings`

---

## Policy Generation Patterns

The legacy system included Python scripts (`generate_policies.py`, `generate_mock_permissions.py`) that automated policy generation based on:

1. **Action word detection**: Identifying view/create/update/delete operations from feature names
2. **Role mapping**: Assigning permissions based on userType
3. **Product gating**: Checking if a retailer has the required product in `auxData.jwt.retailer_products`
4. **Mock permission generation**: Creating test fixtures for different user profiles

### Key Helper Functions

```python
def to_kebab_case(name):
    """Converts a string to kebab-case, handling acronyms and numbers."""

def extract_unique_name_part(child_name, parent_name):
    """Extracts unique part by removing common word prefix with parent."""

def extract_actions_from_name(name):
    """Extracts known action words from a feature name."""
```

### Action Word Dictionary

Common action words extracted during generation:
- **Read**: view, read, show, reports, export, play, filter, download
- **Write**: edit, update, modify, save, set-active, create, add, new, duplicate
- **Delete**: delete, remove, cancel
- **UI**: zoom-in, zoom-out, pan, go-back, click-site

---

## AuxData Contract

The BFF must pass this structure to Cerbos when checking permissions:

```json
{
  "jwt": {
    "retailer_products": ["footprint", "qr", "signage", "connect", "products", "reports"]
  }
}
```

**Fields:**
- `retailer_products`: Array of product keys the active retailer has purchased
- SU and Agency users still receive this (can be empty — they bypass the check)
- Used by policies to gate access to product-specific resources

---

## Testing Patterns

Legacy test suite structure (`tests/page_access_tests.yaml`) tested:
- Each user level (su, agency, retailer) with each role (owner, admin, lead, member, collaborator)
- Product gating (with and without required products)
- Page access rules
- Settings page restrictions
- Menu visibility

Test fixtures included mock permission files for all user profile combinations:
- `su-admin-permissions.json`, `su-member-permissions.json`, etc.
- `agency-admin-permissions.json`, `agency-member-permissions.json`, etc.
- `retailer-owner-permissions.json`, `retailer-collaborator-permissions.json`, etc.

---

## Consolidation Strategy

The migration from page-centric to resource-centric policy structure:

1. **Grouped related resources**: Consolidated product-specific pages into unified policy files
   - `page_products.yaml` + `page_campaigns.yaml` + `page_reports.yaml` → `resource_product.yaml`
   - All `page_settings.yaml` entries → `resource_settings.yaml`
   - Dashboard pages → `resource_profile.yaml`

2. **Simplified hierarchy**: Moved from 11 separate policy files to 4 consolidated files

3. **Maintained compatibility**: All existing resource IDs, user dimensions, and permission rules remain unchanged

4. **Improved maintainability**: Easier to understand the full scope of a domain by viewing a single file

---

## Future Migration Notes

When adding new resources or products:

1. **Determine product assignment**: Which product gates the feature?
2. **Use existing resource ID format**: `<product>:<feature-name>`
3. **Add to appropriate policy file**: resource_product.yaml, resource_settings.yaml, or resource_profile.yaml
4. **Document in this legacy reference**: Ensure product-to-page mapping stays current
5. **Update derived roles if needed**: New user types or conditions should be added to `_derived_roles.yaml`
6. **Test comprehensively**: Verify all user level/type combinations have expected access

---

## References

- **Cerbos Docs**: https://docs.cerbos.dev/
- **Cerbos Playground**: https://play.cerbos.dev/
- **Policy Structure**: See `docs/POLICIES.md` for current policy YAML schema
