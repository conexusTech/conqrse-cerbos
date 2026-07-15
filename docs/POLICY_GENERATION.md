# Cerbos Policy Generation Automation

This guide explains how to generate and maintain Cerbos policy files from the authoritative resource matrix.

## Overview

`scripts/generate_policies.py` reads [`docs/RESOURCES_ACTIONS_MATRIX.md`](./RESOURCES_ACTIONS_MATRIX.md) and emits one Cerbos policy YAML per resource under `k8s/base/policies/`.

- **Source of truth**: the matrix doc — resource definitions, actions, required products.
- **Output**: `k8s/base/policies/resource_*.yaml` (currently **132** files).
- **Companion generator**: `scripts/generate_types.py` regenerates the `@conqrse/permission-types` npm package (enums for Resource/Action/Product/DerivedRole/UserLevel/UserType and the `RESOURCE_META` map).

The related updater `scripts/update_policies_from_matrix.py` does a lighter-weight in-place patch of the product list in existing YAMLs; it skips any resource marked `required-all` because those need the full two-rule structure (regenerate them via `generate_policies.py --force`).

## Quick Start

### Generate all policies (safe — skip existing)

```bash
python3 scripts/generate_policies.py
```

Use on a fresh clone or when adding new resources.

### Regenerate all (force overwrite)

```bash
python3 scripts/generate_policies.py --force
```

Use when the matrix changes and you need every YAML rebuilt. **Note:** overwrites hand-edited comments/annotations — reserve for when policies should match the generator output exactly.

### Preview without writing

```bash
python3 scripts/generate_policies.py --dry-run
```

Shows which files would be generated. Useful to confirm the parser sees your new matrix rows.

### Generate a single resource

```bash
python3 scripts/generate_policies.py --resource "connect:contacts" --force
```

Useful for targeted regeneration — e.g., we used this to regenerate all 28 dealdesk YAMLs without touching non-dealdesk hand-edited policies.

## How It Works

### 1. Parse

The parser reads two kinds of tables from `RESOURCES_ACTIONS_MATRIX.md`:

**Resource-actions tables** (grouped by namespace — QR, Content, Signage, DealDesk, Reports, etc.):

- Resource name (e.g., `dealdesk:campaigns`)
- Type: `collection` or `item`
- Actions: any of `list, view, create, update, delete, export, import`

**Product × Resource Matrix** — the giant table:

- Filename mapping
- Required products, per column
- Marker semantics per cell:
  - `required` → OR semantics (`.exists()` CEL)
  - `required-all` → AND semantics (`.all()` CEL) — introduced for DealDesk
  - `default` column → skip product check entirely (admin-tier resources)

### 2. Classify

Each parsed resource is placed into one of 5 categories:

| Category | Trigger | Example |
|---|---|---|
| `admin_settings` | `default = required` on a non-user-profile resource | `settings:admin_users`, `settings:admin_teams` |
| `user_settings` | `default = required` AND `user_profile` in name | `settings:user_profile:item` |
| `dealdesk_resource` | Any cell in the row is `required-all` | `dealdesk:campaigns`, `dealdesk:brands:item` |
| `product_settings` | Resource name starts with `settings:` AND has product markers | `settings:footprints_sites_property` |
| `product_resource` | Everything else | `connect:contacts`, `qr:campaigns` |

### 3. Render

Each category is emitted by a dedicated renderer inside `PolicyRenderer`:

#### `product_resource` (Collection / Item)

Two rule blocks:
1. **Operator rule** — full CRUD (or `view`/`update`/`delete` for items). Product check `.exists()` + retailerId check (`:item` only). Roles: SU tier + Agency owner/manager + Retailer operator tier.
2. **Collaborator rule** — read-only subset (`list`/`view`/`export` for collections, `view` for items). Same conditions. Roles: SU tier + Agency owner/manager + Agency lead/member/collaborator + `guest_collaborator`.

#### `dealdesk_resource` (introduced with the DealDesk model)

Three rule blocks that OR together at the policy level:

1. **Retailer operator rule** — full actions. Product check: `["ssp","trade","brand_center"].all(p, p in P.attr.products)`. Item resources also check `P.attr.retailerId == R.attr.retailerId`. Roles: SU tier + Agency (all 5) + Retailer operator tier.
2. **Retailer collaborator rule** — read-only subset (`list`/`view`/`export` or just `view`). Same conditions. Role: `guest_collaborator`.
3. **Brand rule** — full actions. Product check: `["brand_center"].exists(p, p in P.attr.products)`. Cross-retailer scoping: `R.attr.retailerId in P.attr.retailerIds`. Roles: `brand_owner`, `brand_manager`, `brand_lead`, `brand_member`.

See the "DealDesk Access Model" section of the matrix doc for the semantic rationale.

#### `product_settings`

Owner/admin-only settings — no collaborator rule. Roles: `root_user`, `platform_administrator`, `platform_lead`, `agency_owner`, `agency_manager`, `agency_lead`, `retailer_owner`, `retailer_manager`.

#### `admin_settings`

Cross-level admin access with no product condition. Roles: all owner/admin/lead across SU/Agency/Retailer.

#### `user_settings`

Universal — no product/tenancy conditions. Actions: `view`, `update`. Roles: all 15 legacy roles (excludes brand tier).

## Workflow: When the Matrix Changes

1. Edit `docs/RESOURCES_ACTIONS_MATRIX.md` — add rows to the resource-actions section AND the Product × Resource Matrix.
2. Add new files to `k8s/base/kustomization.yaml` `configMapGenerator.files:` allowlist. **This is easy to forget** — a policy not in the allowlist never reaches any cluster. The status generator (`scripts/generate_status.py`) flags this explicitly.
3. Dry-run:
   ```bash
   python3 scripts/generate_policies.py --dry-run
   ```
4. Generate:
   ```bash
   python3 scripts/generate_policies.py --resource "<new:resource>" --force
   # or, to rebuild everything:
   python3 scripts/generate_policies.py --force
   ```
5. Regenerate the types package:
   ```bash
   python3 scripts/generate_types.py --force
   ```
6. Bump `packages/permission-types/package.json` version and rebuild:
   ```bash
   cd packages/permission-types && npm run build
   ```
7. Validate:
   ```bash
   cerbos compile k8s/base/policies/
   ```
8. Commit and deploy per the workflow in the top-level [`README`](../README.md).

## Troubleshooting

**"Warning: No action definition found for X"**
The resource appears in the Product × Resource Matrix but is missing from the resource-actions table for its grouping. Add a row to the appropriate `### <Namespace> Resource` section of the matrix doc.

**Script runs but generates 0 files**
Parser found no rows. Check:
- The `## Product × Resource Matrix` heading is intact.
- Table rows use pipe delimiters and don't have stray blank lines mid-table.
- Resource names are not wrapped in backticks in the matrix table (backticks are only used in the resource-actions tables).

**Generated policy doesn't match the matrix**
For non-dealdesk resources, re-run the generator with `--resource <name> --force`. If the policy still looks wrong, the classifier probably picked the wrong category — check whether the row uses `required-all` (which would push it to `dealdesk_resource`).

**Policy generates but doesn't reach the cluster**
The file is missing from `k8s/base/kustomization.yaml`'s `configMapGenerator.files:` allowlist. Add it and re-deploy.

## Key Principles

- **Single source of truth**: the matrix doc.
- **Idempotent**: safe to run multiple times.
- **Selective**: prefer `--resource <name>` over global `--force` when you don't want to disturb hand-edited comments in other files.
- **Coupled with kustomize allowlist**: generating a file is not enough; it must also be listed in `kustomization.yaml`.

## See Also

- [`RESOURCES_ACTIONS_MATRIX.md`](./RESOURCES_ACTIONS_MATRIX.md) — matrix source data
- [`CERBOS_STATUS.md`](./CERBOS_STATUS.md) — deployment/coverage/drift status
- [`PERMISSION_TYPES_PACKAGE.md`](./PERMISSION_TYPES_PACKAGE.md) — companion npm package
- [`scripts/generate_policies.py`](../scripts/generate_policies.py) — generator implementation
