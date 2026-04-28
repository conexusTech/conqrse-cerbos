# @conqrse/permission-types Package

## Overview

`@conqrse/permission-types` is an npm package that provides TypeScript enums and types for Conqrse permission integration with Cerbos. It contains strongly-typed definitions for all resources, actions, roles, and principals used in your authorization policies.

**Package Location:** `packages/permission-types/`  
**Registry:** `https://npm.conqrse.com/`  
**Scope:** `@conqrse`

## What's Included

### Enums (Auto-Generated)

- **Resource** — 83 resource types from the matrix (e.g., `SETTINGS_ADMIN_USERS`, `QR_CAMPAIGNS`, `CONTENTS_PLAYLISTS`)
- **Action** — 7 standard actions (`LIST`, `VIEW`, `CREATE`, `UPDATE`, `DELETE`, `EXPORT`, `IMPORT`)
- **DerivedRole** — 15 derived roles (`ROOT_USER`, `PLATFORM_ADMINISTRATOR`, `AGENCY_OWNER`, `RETAILER_OWNER`, `TEAM_LEAD`, `STAFF_OPERATOR`, `GUEST_COLLABORATOR`, etc.)
- **UserLevel** — User authorization levels (`SU`, `AGENCY`, `RETAILER`)
- **UserType** — User role types within a level (`OWNER`, `ADMIN`, `LEAD`, `MEMBER`, `COLLABORATOR`)
- **Product** — Available products (`QR`, `PRICE_TAGS`, `COMPLIANCE`, `PRODUCT`, `SIGNAGE`, `LANDING`, `CONNECT`, `PPT`)

### Types (Auto-Generated & Static)

- **Principal** (static) — Shape of a principal/user: `{ userId, userLevel, userType, retailerId?, products? }`
- **ResourceMeta** (auto-generated) — Mapping of each resource to its type (`collection` | `item`) and allowed actions

## Single Source of Truth

All enums are generated from `docs/RESOURCES_ACTIONS_MATRIX.md`, which is the single source of truth for all permissions, resources, and actions.

When the matrix is updated, the enums must be regenerated to stay in sync.

---

## Generating Enums

### Quick Start

Generate enums from the current matrix:

```bash
make generate-types
```

### Manual Generation

Generate using the Python script directly:

```bash
python3 scripts/generate_types.py
```

### Options

**Preview without writing files:**
```bash
python3 scripts/generate_types.py --dry-run
```

**Force regenerate (overwrite existing):**
```bash
python3 scripts/generate_types.py --force
```

### What Gets Generated

The generator creates 7 TypeScript files in `packages/permission-types/`:

```
enums/
├── resource.enum.ts       # All resources from matrix
├── action.enum.ts         # Standard actions
├── role.enum.ts           # 15 derived roles
├── user-level.enum.ts     # 3 user levels
├── user-type.enum.ts      # 5 user type names
├── product.enum.ts        # 8 products
└── index.ts               # Re-exports all enums

types/
├── principal.type.ts       # Principal shape (static, pre-existing)
├── resource-action.type.ts # ResourceMeta mapping (auto-generated)
└── index.ts               # Re-exports all types
```

### Generator Behavior

- **Skips existing files** unless `--force` is used (safe by default)
- **Parses** `docs/RESOURCES_ACTIONS_MATRIX.md` to extract resources, actions, and roles
- **Generates** SCREAMING_SNAKE_CASE enum keys with string values
- **Creates** TypeScript files with proper imports and exports
- **Reports** progress with summary (Generated/Skipped counts)

---

## Updating the Package

### When to Update

Update the package when:

1. **Matrix Changes** — New resources, actions, or roles are added to `docs/RESOURCES_ACTIONS_MATRIX.md`
2. **Enum Structure Changes** — The generator script is modified
3. **Type Definitions Change** — New types or Principal shape changes

### Update Workflow

#### 1. Regenerate Enums

After modifying the matrix:

```bash
make generate-types --force
```

or

```bash
python3 scripts/generate_types.py --force
```

#### 2. Verify Changes

Check what changed:

```bash
git status
git diff packages/permission-types/
```

#### 3. Review Generated Files

Spot-check the generated enums to ensure they're correct:

```bash
# Check resource count
grep -c "= '" packages/permission-types/enums/resource.enum.ts

# Check a specific enum
head -20 packages/permission-types/enums/resource.enum.ts
```

#### 4. Test Imports (Optional)

Create a quick test file to verify TypeScript imports work:

```typescript
// test-imports.ts
import { 
  Resource, 
  Action, 
  DerivedRole, 
  RESOURCE_META 
} from './packages/permission-types';

const r: Resource = Resource.SETTINGS_ADMIN_USERS;
const a: Action = Action.LIST;
const role: DerivedRole = DerivedRole.ROOT_USER;

console.log(RESOURCE_META[Resource.QR_CAMPAIGNS]);
// Output: { type: 'collection', actions: [...] }
```

#### 5. Commit Changes

```bash
git add packages/permission-types/enums/
git commit -m "chore: Regenerate permission types from updated matrix"
```

---

## Publishing

### Prerequisites

- You have write access to the `https://npm.conqrse.com/` registry
- Your `.npmrc` is configured with the registry token (typically stored in `~/.npmrc` at user level)
- The `.npmrc` in the repo root has `@conqrse:registry=https://npm.conqrse.com/` (already configured)

### Publishing Steps

#### 1. Bump Version

Use npm's built-in version management:

```bash
cd packages/permission-types

# Patch version (1.0.0 → 1.0.1)
npm version patch

# Minor version (1.0.0 → 1.1.0)
npm version minor

# Major version (1.0.0 → 2.0.0)
npm version major
```

This automatically:
- Updates `package.json` version
- Creates a git tag (optional, you can use `--no-git-tag-version` to skip)
- Commits the version change

#### 2. Publish to Registry

```bash
npm publish --registry https://npm.conqrse.com/
```

Or from the root directory:

```bash
cd packages/permission-types && npm publish --registry https://npm.conqrse.com/
```

#### 3. Verify Publication

Check that the package appeared in the registry:

```bash
npm view @conqrse/permission-types@latest --registry https://npm.conqrse.com/
```

#### 4. Commit Version Bump

If the version bump wasn't auto-committed (or you used `--no-git-tag-version`):

```bash
git add packages/permission-types/package.json
git commit -m "chore: Bump @conqrse/permission-types to v1.X.X"
```

### Publishing Errors

**Error: `409 Conflict - this package is already present`**

→ The version already exists. Bump the version again using `npm version`.

**Error: `401 Unauthorized`**

→ Your npm registry token is missing or expired. Configure via:

```bash
npm login --registry https://npm.conqrse.com/
```

Then try publishing again.

---

## Installation

### In Your Project

```bash
npm install @conqrse/permission-types
```

### With Specific Version

```bash
npm install @conqrse/permission-types@1.0.3
```

### In Package.json

```json
{
  "dependencies": {
    "@conqrse/permission-types": "^1.0.3"
  }
}
```

### Next.js / Turbopack Compatibility

If you encounter build errors in Next.js 16+ with Turbopack:

```
Missing module type - The module type effect must be applied before adding Ecmascript transforms
```

**Solution:** Update to version 1.0.3 or later, which includes proper TypeScript module type declarations in package.json.

```bash
npm update @conqrse/permission-types
```

Then rebuild your Next.js app:

```bash
npm run build
```

---

## Usage

### Import All Types

```typescript
import {
  // Enums
  Resource,
  Action,
  DerivedRole,
  UserLevel,
  UserType,
  Product,
  // Types
  Principal,
  RESOURCE_META,
  ResourceMeta,
  ResourceType,
} from '@conqrse/permission-types';
```

### Import Specific Exports

```typescript
// By enum
import { Resource, Action } from '@conqrse/permission-types/enums';

// By type
import { Principal } from '@conqrse/permission-types/types';

// Specific files
import { RESOURCE_META } from '@conqrse/permission-types/types/resource-action.type';
```

### Common Usage Examples

#### Check Resource Type

```typescript
import { RESOURCE_META, Resource } from '@conqrse/permission-types';

const meta = RESOURCE_META[Resource.QR_CAMPAIGNS];
console.log(meta.type);    // 'collection'
console.log(meta.actions); // [Action.LIST, Action.VIEW, ...]
```

#### Define a Principal

```typescript
import { Principal, UserLevel, UserType } from '@conqrse/permission-types';

const principal: Principal = {
  userId: 'user-123',
  userLevel: UserLevel.RETAILER,
  userType: UserType.OWNER,
  retailerId: 'retailer-456',
  products: [Product.QR, Product.SIGNAGE],
};
```

#### Check Permissions with Cerbos

```typescript
import { Resource, Action } from '@conqrse/permission-types';
import { grpc } from '@cerbos/grpc';

const cerbos = new grpc.CerbosClient('localhost:3593');

const result = await cerbos.checkResource({
  resource: {
    kind: Resource.QR_CAMPAIGNS,
    id: 'campaign-123',
  },
  actions: [Action.VIEW, Action.UPDATE],
  principal: {
    id: principal.userId,
    roles: [DerivedRole.RETAILER_OWNER],
    attributes: {
      userLevel: principal.userLevel,
      userType: principal.userType,
      retailerId: principal.retailerId,
      products: principal.products,
    },
  },
});
```

---

## Architecture

### Generator Script

**File:** `scripts/generate_types.py`

The generator:

1. **Parses** `docs/RESOURCES_ACTIONS_MATRIX.md` markdown
   - Extracts resource definitions (name, type, actions)
   - Reads the Product × Resource Matrix section
   - Maps resources to their required products

2. **Generates** TypeScript enums
   - Converts resource names to SCREAMING_SNAKE_CASE keys
   - Creates string-valued enums matching the matrix

3. **Outputs** to `packages/permission-types/`
   - 6 enum files (resource, action, role, user-level, user-type, product)
   - 1 type file (resource-action mapping)

### Package Structure

```
packages/permission-types/
├── package.json          # NPM package metadata
├── index.ts              # Main export barrel
├── enums/
│   ├── *.enum.ts         # Generated enum files
│   └── index.ts          # Enum re-exports
└── types/
    ├── principal.type.ts           # Static Principal type
    ├── resource-action.type.ts     # Generated ResourceMeta
    └── index.ts                    # Type re-exports
```

### Publishing Configuration

**File:** `.npmrc`

```
@conqrse:registry=https://npm.conqrse.com/
```

Routes all `@conqrse` scoped packages to the private registry.

---

## Troubleshooting

### Enums Don't Match Matrix

**Symptom:** New resources in matrix don't appear in enums.

**Solution:** Regenerate enums:

```bash
python3 scripts/generate_types.py --force
```

Ensure `docs/RESOURCES_ACTIONS_MATRIX.md` is up-to-date before regenerating.

### Import Errors in TypeScript

**Symptom:** `Cannot find module '@conqrse/permission-types'`

**Solution:**

1. Ensure package is installed: `npm list @conqrse/permission-types`
2. Check `.npmrc` has the correct registry for `@conqrse` scope
3. Verify package.json exports are correct: `npm view @conqrse/permission-types`

### Version Already Exists

**Symptom:** Publishing fails with `409 Conflict - this package is already present`

**Solution:** Bump the version before publishing:

```bash
cd packages/permission-types
npm version patch
npm publish --registry https://npm.conqrse.com/
```

### Stale Enums After Matrix Update

**Symptom:** Using old enum values that no longer exist.

**Solution:**

1. Regenerate enums: `make generate-types --force`
2. Commit and publish new package version
3. Update consuming projects to new package version: `npm update @conqrse/permission-types`

---

## Makefile Targets

| Command | Purpose |
|---------|---------|
| `make generate-types` | Regenerate TypeScript enums from matrix (skips if files exist) |
| `make generate-policies` | Regenerate Cerbos policies from matrix |
| `make help` | Show all available targets |

---

## Related Documentation

- **[RESOURCES_ACTIONS_MATRIX.md](./RESOURCES_ACTIONS_MATRIX.md)** — Matrix definition (source of truth)
- **[POLICY_GENERATION.md](./POLICY_GENERATION.md)** — Cerbos policy generation (parallel to this package)
- **[API Documentation](https://docs.cerbos.dev/)** — Cerbos official docs

---

## Contributing

When updating the matrix (`docs/RESOURCES_ACTIONS_MATRIX.md`):

1. **Update the matrix** with new resources, actions, or roles
2. **Regenerate enums**: `make generate-types --force`
3. **Regenerate policies** (if applicable): `make generate-policies --force`
4. **Commit both** in a single commit:
   ```bash
   git add packages/permission-types/ k8s/base/policies/
   git commit -m "feat: Add new resources to permission matrix"
   ```
5. **Publish package** if enums changed:
   ```bash
   cd packages/permission-types
   npm version patch
   npm publish --registry https://npm.conqrse.com/
   ```

---

## Version History

- **1.0.3** — Fixed Next.js/Turbopack compatibility with proper module type declarations in package.json
- **1.0.2** — (skipped)
- **1.0.1** — Fixed repository URL metadata
- **1.0.0** — Initial release with 83 resources, 7 actions, 15 roles

---

## Questions?

For issues or questions:

1. Check the [Troubleshooting](#troubleshooting) section
2. Review the matrix definition in `docs/RESOURCES_ACTIONS_MATRIX.md`
3. Examine the generator script: `scripts/generate_types.py`
4. Check npm registry metadata: `npm view @conqrse/permission-types --registry https://npm.conqrse.com/`
