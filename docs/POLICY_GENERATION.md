# Cerbos Policy Generation Automation

This guide explains how to use the policy generation script to create and maintain Cerbos policy files from the authoritative resource matrix.

## Overview

The `scripts/generate_policies.py` script automatically generates all 81 Cerbos resource policy YAML files by parsing:
- `docs/RESOURCES_ACTIONS_MATRIX.md` — resource definitions and product requirements
- `docs/CERBOS_CONQRSE.md` — user roles and permissions

This eliminates manual YAML editing and ensures policies stay in sync with your documentation.

## Quick Start

### Generate All Policies (Safe Mode)

```bash
python scripts/generate_policies.py
```

This skips any existing files. Use when adding new resources or on a fresh clone.

### Generate All Policies (Force Overwrite)

```bash
python scripts/generate_policies.py --force
```

Overwrites all existing files. Use when the matrix changes and you need to regenerate everything.

### Preview Without Writing

```bash
python scripts/generate_policies.py --dry-run
```

Shows which files would be generated without actually writing them. Useful for validation before committing.

### Generate a Single Resource

```bash
python scripts/generate_policies.py --resource "connect:contacts"
```

Generates only the specified resource policy. Useful for testing or debugging.

## How It Works

### 1. Parsing Phase

The script reads two markdown files and extracts:

**From Resource Tables** (Footprints, Content, Signage, QR, Reports, Connect, Settings):
- Resource name (e.g., `qr:campaigns`)
- Resource type: `collection` or `item`
- Available actions (list, view, create, update, delete, export, import)

**From Product × Resource Matrix**:
- File name mapping
- Required products per resource
- Whether resource is "default" (no product validation)

### 2. Classification Phase

Resources are categorized into 4 policy patterns:

| Category | Characteristics | Example |
|----------|---|---|
| **product_resource** | Has required products, not a settings resource | `connect:contacts`, `reports:campaign_compliance` |
| **product_settings** | Has required products, is a settings resource | `settings:footprints_sites_property` |
| **admin_settings** | No products (default), is an admin settings resource | `settings:admin_users`, `settings:admin_teams` |
| **user_settings** | Special universal resource for user profile | `settings:user_profile:item` |

### 3. Generation Phase

For each resource, the appropriate YAML template is rendered with:
- Correct conditions (product check, retailer ID check)
- Appropriate derived roles (operators vs collaborators)
- Valid actions from the matrix

## Authorization Patterns Generated

### Product Resources (Collection)

```yaml
rules:
  # Operators: full CRUD access
  - actions: ["list", "view", "create", "update", "delete", "export", "import"]
    condition:
      - product subscription check
      - retailer ID check
    derivedRoles: [retailer_owner, retailer_manager, team_lead, staff_operator]
  
  # Collaborators: read-only access
  - actions: ["list", "view", "export"]
    condition: (same)
    derivedRoles: [guest_collaborator]
```

### Product Resources (Item)

Same conditions as collections, but:
- Operators: `view`, `update`, `delete` (no list, create, export, import)
- Collaborators: `view` only

### Product Settings

Only owner/admin access:
- Conditions: product check + retailer ID check
- Roles: `retailer_owner`, `retailer_manager` only
- Collaborators: NOT included (settings: NONE for non-owners)
- Actions: `list, view, create, update, delete, export, import` (no prefix)

### Admin Settings

Cross-level admin access:
- No conditions (cross-cutting concern)
- Roles: all owner/admin at all levels
  - `root_user`, `platform_administrator` (SU)
  - `agency_owner`, `agency_manager` (Agency)
  - `retailer_owner`, `retailer_manager` (Retailer)

### User Profile

Universal access:
- No conditions
- All 15 derived roles
- Actions: `view`, `update` only

## Workflow: When Matrix Changes

When you update `docs/RESOURCES_ACTIONS_MATRIX.md`:

### 1. Verify Changes

```bash
# Check what would be generated
python scripts/generate_policies.py --dry-run
```

### 2. Review Output

Look for:
- New resources being generated ✅
- Existing resources being updated ✅
- Any warnings about missing action definitions ⚠️

### 3. Generate

```bash
# If satisfied, generate all files
python scripts/generate_policies.py --force
```

### 4. Test

Run the Cerbos test suite:
```bash
bash tests/run-tests.sh
```

### 5. Commit

```bash
git add k8s/base/policies/ scripts/generate_policies.py
git commit -m "chore: Regenerate policies from updated matrix"
```

## File Structure

```
conqrse-cerbos/
├── scripts/
│   └── generate_policies.py          ← The generator script
├── docs/
│   ├── RESOURCES_ACTIONS_MATRIX.md   ← Source of truth
│   ├── CERBOS_CONQRSE.md             ← Role definitions
│   └── POLICY_GENERATION.md          ← This file
└── k8s/base/policies/
    ├── _derived_roles.yaml           ← Role definitions (unchanged)
    ├── resource_connect_contacts.yaml  ← Generated files...
    ├── resource_qr_campaigns.yaml
    └── ... (81 total resource policies)
```

## Troubleshooting

### "Warning: No action definition found for X"

The resource exists in the matrix but not in the resource action tables. 

**Solution**: Add the resource to the appropriate resource table section in `docs/RESOURCES_ACTIONS_MATRIX.md` with its actions.

### Script runs but generates 0 files

Parsing failed. Check that:
- `docs/RESOURCES_ACTIONS_MATRIX.md` exists and is readable
- Matrix has the "## Product × Resource Matrix" section header
- Resource action tables are properly formatted (pipes, backticks, etc.)

### Generated file missing actions

The resource table might list wrong actions. Check `docs/RESOURCES_ACTIONS_MATRIX.md`:
- Collection resources should have: `list, view, create, update, delete, export, import`
- Item resources should have: `view, update, delete`
- Reports typically have: `list, view, export`
- Exception: `reports:export` has `list, export, delete`

## Advanced Usage

### Generate with Logging

```bash
# Standard output is sufficient for most cases
python scripts/generate_policies.py 2>&1 | tee generation.log
```

### Batch Process Multiple Resources

```bash
# Generate specific resources
for resource in "qr:campaigns" "connect:contacts" "settings:admin_users"; do
  python scripts/generate_policies.py --resource "$resource"
done
```

### Integration with CI/CD

Add to your pipeline to validate policies:

```bash
#!/bin/bash
# Verify matrix is consistent
python scripts/generate_policies.py --dry-run || exit 1

# Generate in temp directory
mkdir -p /tmp/generated-policies
python scripts/generate_policies.py --force
# ^ Could also validate with Cerbos schema checker
```

## Reference: Policy Categories

### Determining Category Automatically

The script determines category from:

1. **Is it settings?** Check if resource name starts with `settings:`
2. **Is it user_profile?** Check if `user_profile` in resource name
3. **Has products?** Check Product × Resource Matrix

Logic:
```
if is_settings and is_default and not is_user_profile:
    category = "admin_settings"
elif is_settings and is_user_profile:
    category = "user_settings"
elif is_settings and has_products:
    category = "product_settings"
else:
    category = "product_resource"
```

## Key Principles

✅ **Single Source of Truth**: Matrix docs are authoritative  
✅ **Idempotent**: Safe to run multiple times  
✅ **Audit Trail**: All policies in git with generation history  
✅ **Maintainable**: Changes in one place (the matrix)  
✅ **Testable**: Run tests after generation  

## See Also

- [RESOURCES_ACTIONS_MATRIX.md](./RESOURCES_ACTIONS_MATRIX.md) — Matrix source data
- [CERBOS_CONQRSE.md](./CERBOS_CONQRSE.md) — Authorization rules
- [scripts/generate_policies.py](../scripts/generate_policies.py) — Generator implementation
