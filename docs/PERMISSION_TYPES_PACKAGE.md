# @conqrse/permission-types Package

TypeScript enums and types for Conqrse consumers (`conqrse-admin`, `conqrse-api3`) that integrate with Cerbos.

- **Package location:** `packages/permission-types/`
- **Registry:** `https://npm.conqrse.com/`
- **Scope:** `@conqrse`
- **Current version:** see `packages/permission-types/package.json` (as of writing: **1.5.0**)

## What's Inside

### Enums (auto-generated from the matrix)

| Enum | Count | Notes |
|---|---|---|
| `Resource` | 131 | All resource kinds — e.g., `SETTINGS_ADMIN_USERS`, `QR_CAMPAIGNS`, `DEALDESK_CAMPAIGNS_ITEM` |
| `Action` | 7 | `LIST`, `VIEW`, `CREATE`, `UPDATE`, `DELETE`, `EXPORT`, `IMPORT` |
| `DerivedRole` | 19 | SU tier (5) + Agency tier (5) + Retailer tier (5) + Brand tier (4) |
| `UserLevel` | 4 | `SU`, `AGENCY`, `RETAILER`, `BRAND` |
| `UserType` | 5 | `OWNER`, `ADMIN`, `LEAD`, `MEMBER`, `COLLABORATOR` |
| `Product` | 12 | `QR`, `PRICE_TAGS`, `COMPLIANCE`, `PRODUCT`, `SIGNAGE`, `LANDING`, `CONNECT`, `PPT`, `CMS`, `SSP`, `TRADE`, `BRAND_CENTER` |

### Types

- `Principal` (static) — shape of the principal payload sent to Cerbos: `{ userId, userLevel, userType, retailerId?, brandId?, retailerIds?, products? }`
- `ResourceMeta` (auto-generated) — per-resource metadata:
  ```ts
  { type: 'collection' | 'item'; actions: Action[]; products: Product[] }
  ```
- `RESOURCE_META: Record<Resource, ResourceMeta>` — the full lookup map.

### Single source of truth

All enums are derived from [`docs/RESOURCES_ACTIONS_MATRIX.md`](./RESOURCES_ACTIONS_MATRIX.md). When the matrix changes, regenerate. **Never hand-edit the generated files** — they'll be blown away on the next regeneration.

---

## Generating the Package

```bash
python3 scripts/generate_types.py           # skip existing files
python3 scripts/generate_types.py --dry-run # preview
python3 scripts/generate_types.py --force   # overwrite everything
```

Generated files land in `packages/permission-types/`:

```
enums/
├── resource.enum.ts       # generated — 131 Resource entries
├── action.enum.ts         # generated — 7 Action entries
├── role.enum.ts           # generated — 19 DerivedRole entries
├── user-level.enum.ts     # generated — 4 UserLevel entries
├── user-type.enum.ts      # generated — 5 UserType entries
├── product.enum.ts        # generated — 12 Product entries
└── index.ts               # hand-maintained re-exports

types/
├── principal.type.ts       # static — Principal shape
├── resource-action.type.ts # generated — RESOURCE_META
└── index.ts                # hand-maintained re-exports
```

After regenerating, always build the package to verify the emitted TypeScript compiles:

```bash
cd packages/permission-types && npm run build
```

---

## Update & Publish Workflow

**Every change to policy files must be paired with a version bump of this package.** Consumers depend on the enums; if the enums drift from the deployed policies, they will type-check successfully but fail at runtime when Cerbos rejects the (missing) resource or role.

### 1. Regenerate

```bash
python3 scripts/generate_types.py --force
```

### 2. Bump the version

Edit `packages/permission-types/package.json`. Semver guidance:

| Change | Version bump |
|---|---|
| New resource / product / role / user-level added, no removals | **minor** (`1.5.0` → `1.6.0`) |
| Resource / product / role removed, or a value string changed | **major** (`1.5.0` → `2.0.0`) — breaking |
| Package-only fix (types file layout, build config), no enum values changed | **patch** (`1.5.0` → `1.5.1`) |

### 3. Build

```bash
cd packages/permission-types && npm run build
```

Fail fast: the build must be clean before publishing.

### 4. Commit

```bash
git add packages/permission-types/
git commit -m "chore(permission-types): bump version to v1.6.0"
```

Do this in the same PR / commit chain as the matrix + policy changes so consumers see a consistent view.

### 5. Publish

```bash
cd packages/permission-types
npm publish --registry https://npm.conqrse.com/
```

Verify:

```bash
npm view @conqrse/permission-types@latest --registry https://npm.conqrse.com/
```

### 6. Update consumers

In `conqrse-api3` and `conqrse-admin`:

```bash
npm install @conqrse/permission-types@latest
```

Then rebuild each consumer and deploy. If a consumer keeps referencing an old enum value that was removed, TypeScript will fail — that's the point of the coupled version bump.

---

## Installation (in a consumer)

```bash
npm install @conqrse/permission-types
```

Ensure `.npmrc` in the consumer repo has:

```
@conqrse:registry=https://npm.conqrse.com/
```

---

## Usage

### Import

```typescript
import {
  Resource,
  Action,
  DerivedRole,
  UserLevel,
  UserType,
  Product,
  Principal,
  RESOURCE_META,
  ResourceMeta,
  ResourceType,
} from '@conqrse/permission-types';
```

### Look up a resource

```typescript
const meta = RESOURCE_META[Resource.QR_CAMPAIGNS];
console.log(meta.type);     // 'collection'
console.log(meta.actions);  // [Action.LIST, Action.VIEW, ...]
console.log(meta.products); // [Product.QR, ...]
```

### Construct a principal (Retailer user)

```typescript
const principal: Principal = {
  userId: 'user-123',
  userLevel: UserLevel.RETAILER,
  userType: UserType.OWNER,
  retailerId: 'retailer-456',
  products: [Product.QR, Product.SIGNAGE],
};
```

### Construct a principal (Brand user — DealDesk)

```typescript
const brandPrincipal: Principal = {
  userId: 'user-789',
  userLevel: UserLevel.BRAND,
  userType: UserType.OWNER,
  brandId: 'brand-abc',
  retailerIds: ['retailer-456', 'retailer-789'],  // populated from Brand.Retailers[]
  products: [Product.BRAND_CENTER],
};
```

### Check permissions with Cerbos

```typescript
import { grpc } from '@cerbos/grpc';

const cerbos = new grpc.CerbosClient('cerbos:3593');

const result = await cerbos.checkResource({
  resource: {
    kind: Resource.DEALDESK_CAMPAIGNS,
    id: 'campaign-123',
    attributes: {
      retailerId: 'retailer-456',
    },
  },
  actions: [Action.VIEW, Action.UPDATE],
  principal: {
    id: brandPrincipal.userId,
    roles: [DerivedRole.BRAND_OWNER],
    attributes: {
      userLevel: brandPrincipal.userLevel,
      userType: brandPrincipal.userType,
      brandId: brandPrincipal.brandId,
      retailerIds: brandPrincipal.retailerIds,
      products: brandPrincipal.products,
    },
  },
});
```

---

## Troubleshooting

**Enums don't match the matrix**
Regenerate: `python3 scripts/generate_types.py --force`. Verify the matrix has the row(s) you expect. If a resource is in the matrix's resource-actions table but missing from the Product × Resource Matrix table (or vice versa), it will be silently skipped.

**Import errors — `Cannot find module '@conqrse/permission-types'`**
1. Verify install: `npm list @conqrse/permission-types`.
2. Check the consumer's `.npmrc` has `@conqrse:registry=https://npm.conqrse.com/`.
3. Check the package was published: `npm view @conqrse/permission-types --registry https://npm.conqrse.com/`.

**`409 Conflict — package already present`**
Bump the version and republish. Never overwrite a published version.

**`401 Unauthorized`**
Registry token missing/expired. Re-authenticate: `npm login --registry https://npm.conqrse.com/`.

**Consumer breaks at runtime after upgrade**
The enum value(s) the consumer used were removed or renamed. Update the consumer's code to use the new values, or roll back the package version. This is why removals warrant a major bump.

---

## Version History

- **1.5.0** — Added `ssp`, `trade`, `brand_center` products; `brand` UserLevel; 4 brand-tier roles (`brand_owner`, `brand_manager`, `brand_lead`, `brand_member`); 28 `dealdesk:*` resources + 1 legacy `dealdesk_brand:media-packages`.
- **1.4.0** — Version bump alongside CMS resource growth.
- **1.3.0** — Added `contents:landing_pages` resources.
- **1.2.0** — CMS product with 9 features.
- **1.1.0** — Added `products` array to `ResourceMeta` (aligns with Product × Resource Matrix).
- **1.0.3** — Fixed Next.js / Turbopack compatibility (added TypeScript module type declarations).
- **1.0.1** — Repository URL metadata fix.
- **1.0.0** — Initial release: 83 resources, 7 actions, 15 roles.

---

## Related Docs

- [`RESOURCES_ACTIONS_MATRIX.md`](./RESOURCES_ACTIONS_MATRIX.md) — Matrix source of truth
- [`POLICY_GENERATION.md`](./POLICY_GENERATION.md) — Cerbos policy generation (parallel to this package)
- [`CERBOS_STATUS.md`](./CERBOS_STATUS.md) — Deployment/coverage status
- [Cerbos Docs](https://docs.cerbos.dev/) — Upstream Cerbos documentation
