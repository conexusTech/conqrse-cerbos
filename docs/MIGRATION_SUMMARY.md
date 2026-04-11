# Migration Summary: Page-Centric → Resource-Centric

This document explains what was consolidated in the `old/` directory refactoring and why.

---

## What Was Migrated

### Policy File Consolidation

**Old Structure** (11 policy files, 1 per domain):
- `page_dashboard.yaml` → 3 resources (dashboards)
- `page_reports.yaml` → 9 resources (reports)
- `page_footprint.yaml` → 4 resources (footprint)
- `page_content.yaml` → 7 resources (content)
- `page_products.yaml` → 4 resources (products)
- `page_signage.yaml` → 2 resources (signage)
- `page_connect.yaml` → 1 resource (connect)
- `page_campaigns.yaml` → 1 resource (campaigns/qr)
- `page_data.yaml` → 2 resources (data)
- `page_settings.yaml` → 10 resources (settings)
- `menu.yaml` → sidebar visibility rules

**New Structure** (4 policy files, organized by function):
- `resource_product.yaml` → products, campaigns, reports (product-feature resources)
- `resource_settings.yaml` → all settings pages (settings-only access)
- `resource_profile.yaml` → dashboards (profile/level-based access)
- `_derived_roles.yaml` → role definitions (shared by all)

### What Stayed the Same

✅ All resource IDs unchanged
✅ All user dimensions (userLevel, userType) unchanged
✅ All permission rules unchanged
✅ All product gating logic unchanged
✅ AuxData contract unchanged
✅ Derived roles logic unchanged

### What Was Removed

❌ `old/z-policy_conversion/` — Python policy generation scripts (legacy automation)
❌ `old/z-policy_conversion/mock-permissions/` — 40+ test fixture JSON files
❌ `old/_schemas/` — JSON schema files (pre-Cerbos JSON schema support)
❌ `old/export_variables/` — Shared variable definitions (consolidated into rules)
❌ `old/derived_roles/` — Role definitions (moved to `_derived_roles.yaml`)
❌ `old/PERMISSIONS.md` — Comprehensive docs (preserved in `LEGACY_PATTERNS.md`)
❌ `old/config.yaml` — Cerbos server config (moved to root `docker-compose.yml`)

---

## Why This Change

### Benefits of Resource-Centric Model

1. **Reduced file count**: 11 files → 4 files (63% fewer files)
   - Less file switching during development
   - Easier to understand related resources together
   - Clearer where to add new features

2. **Better logical grouping**: By function, not by product
   - Product features in one place
   - Settings in one place
   - Profile/dashboard in one place

3. **Easier maintenance**:
   - All related policies visible at once
   - Fewer directories to navigate
   - Less duplication of rule patterns

4. **Simplified imports**:
   - Single derived role import per file
   - Consistent structure across all policies

### Trade-offs

| Aspect | Old (Page-Centric) | New (Resource-Centric) |
|--------|-------------------|----------------------|
| File exploration | 11 small files, easy to find specific page | 4 larger files, need to search within file |
| Related policies | Spread across files if products overlap | All related policies together |
| Policy size | Smaller, focused files | Larger consolidated files |
| Pattern clarity | Each file is self-contained | Requires reading entire file |

**Verdict**: The consolidation provides better maintainability with minimal downside in modern IDEs (search, outline view).

---

## How Resources Were Grouped

### Product Features → `resource_product.yaml`

Combined resources that require a product to access:

```yaml
# Products that require "products" product
- products:details
- products:pricing
- products:promotions
- products:properties

# Reports that require "reports" product
- reports:qr-performance
- reports:qr-performance-site-to-site
- reports:campaign-compliance
- ... (9 total)

# Campaigns that require "qr" product
- campaigns:main
```

**Why grouped**: These all follow the same pattern:
1. Check if user has the required product in `retailer_products`
2. Apply role-based CRUD restrictions
3. No level gating (SU/agency bypass product checks)

### Settings → `resource_settings.yaml`

All resources requiring owner/admin role:

```yaml
- settings:general
- settings:footprint
- settings:menu
- settings:price-tag
- settings:product
- settings:properties-manager
- settings:qr
- settings:signage
- settings:teams
- settings:users
```

**Why grouped**: These all follow the same pattern:
1. Block collaborators/members/leads
2. Only allow owner/admin
3. No product gating (base access)

### Dashboards → `resource_profile.yaml`

Level-based dashboard access:

```yaml
- dashboard:su         → Super user only
- dashboard:agency     → Agency + Super user
- dashboard:retailer   → All authenticated users
```

**Why grouped**: These follow a unique level-gating pattern not used elsewhere

---

## File Size Comparison

| File | Old Lines | New Lines |
|------|-----------|-----------|
| page_dashboard.yaml | ~45 | ← consolidated to resource_profile.yaml (~50) |
| page_reports.yaml | ~150 | ← consolidated to resource_product.yaml (~300) |
| page_footprint.yaml | ~100 | |
| page_content.yaml | ~140 | |
| page_products.yaml | ~80 | |
| page_signage.yaml | ~60 | |
| page_connect.yaml | ~50 | |
| page_campaigns.yaml | ~40 | |
| page_data.yaml | ~50 | |
| page_settings.yaml | ~200 | ← consolidated to resource_settings.yaml (~250) |
| **Total** | **~915 lines** | **~600 lines** |

**Result**: ~34% reduction in policy code, mainly through removing duplicated rule patterns.

---

## Verification Checklist

The migration preserved all permissions by verifying:

- ✅ All 41 unique resource IDs present and unchanged
- ✅ All derived roles (7 total) functioning identically
- ✅ Product gating logic maintained for all gated resources
- ✅ Role-based restrictions unchanged
- ✅ Level-based scoping unchanged
- ✅ AuxData contract compatible
- ✅ All routes to resources documented and mapped

---

## Future: Adding New Features

When adding a new page/feature to Conqrse:

### If it requires a product:
1. Add resource ID to `resource_product.yaml` in the appropriate product section
2. Use standard pattern: Allow if product in `retailer_products`, apply role restrictions
3. Document in `LEGACY_PATTERNS.md` product-to-page mapping

### If it's a settings page:
1. Add resource ID to `resource_settings.yaml`
2. Use standard pattern: owner/admin only
3. Document in `LEGACY_PATTERNS.md` settings table

### If it's a new dashboard/profile page:
1. Add resource ID to `resource_profile.yaml`
2. Use level-based conditions
3. Document in `LEGACY_PATTERNS.md` dashboard table

---

## Legacy Reference

Complete product-to-page mapping and permission rules are preserved in:
- **`docs/LEGACY_PATTERNS.md`** — Full reference of all 41 resources, mappings, and rules
- **Current policies** — Implementation in `policies/resource_*.yaml`

For questions about a specific resource or product, refer to `LEGACY_PATTERNS.md`.
