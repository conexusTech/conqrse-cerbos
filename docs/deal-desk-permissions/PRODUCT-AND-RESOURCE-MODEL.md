# Product & Resource Model

## 1. Products

### Add these (new)

| Enum value (proposed) | String | Gates |
|---|---|---|
| `SSP` | `ssp` | Programmatic supply surfaces |
| `TRADE` | `trade` | Physical trade surfaces |
| `BRAND_CENTER` | `brand_center` | Brand hub + brand portal |

Add to **both**:
- `RetailerProduct` in `@conqrse/api-types` (`data/_common.entity.ts`)
- `Product` in `@conqrse/permission-types` (`enums/product.enum.ts`)

Keep the string values identical across both enums (lowercase, matching the existing convention:
`qr`, `signage`, `connect`, …).

### Remove this (error)

- **`DEAL_DESK` / `dealDesk`** in `RetailerProduct` is a mistake introduced on a feature branch.
  Remove it. Only one usage in this repo: `src/app/components/shared/retailer/types.ts` (the enum
  list at ~line 17 and the label map at ~line 32) — drop both entries. Verify no API/back-end relies
  on a retailer having `dealDesk` in `products` before removing.

### Leave as-is

- **`signage`** is its own product for the existing Content/Signage surfaces (`contents:*`,
  `signages:*`). It does **not** gate Deal Desk. No change.
- All other existing products (`qr`, `connect`, `priceTags`, `product`, `landing`, `ppt`, `cms`,
  `compliance`) — unchanged.

### No base product

There is no umbrella product that unlocks the Deal Desk shell. Each surface gates on the specific
product it belongs to. (This is why removing `DEAL_DESK` is safe — nothing should depend on a
Deal-Desk-wide product.)

## 2. Resource IDs (the real ones)

These are the **interim** keys in `src/lib/permissions/deal-desk-resources.ts` (`DealDeskResource`),
used by `<CanI>` today. They are the strings to gate; when the platform team promotes them into the
SSoT `Resource` enum they become `Resource.DEAL_DESK_*` with `<namespace>:<resource>` + `:item` form.

Key format everywhere: `<resource>:<action>` (e.g. `deal_desk:trade_ledger:view`).

## 3. Resource → Product → Actions matrix

`✳` = the product that must be in `principal.attr.products` for the resource to be permitted.
Actions listed are those actually used by pages today (full set available: list/view/create/update/delete/export/import).

### SSP — gate on `ssp`

| Resource ID | Route | Actions used | Product |
|---|---|---|---|
| `deal_desk:dsp_blocks` | `/deal-desk/ssp/dsp-blocks`, `/[dspBlockId]` | view, create | `ssp` |
| `deal_desk:deals` | `/deal-desk/ssp/deals` | view, create | `ssp` |
| `deal_desk:waterfall_config` | `/deal-desk/ssp/waterfall-config` | view, update | `ssp` |
| `deal_desk:decision_log` | `/deal-desk/ssp/decision-log` | view | `ssp` |
| `deal_desk:queue_jobs` | `/deal-desk/ssp/jobs` | view | `ssp` |

### Trade — gate on `trade`

| Resource ID | Route | Actions used | Product |
|---|---|---|---|
| `deal_desk:trade_ledger` | `/deal-desk/trade-ledger`, `/[fundId]` | view, create, update | `trade` |
| `deal_desk:work_orders` | `/deal-desk/operations/work-orders` | view | `trade` |
| `deal_desk:compliance` | `/deal-desk/operations/compliance{,/monitoring,/verification}` | view | `trade` |
| `deal_desk:packages` | `/deal-desk/inventory/packages`, `/new` | view, create | `trade` |

> Note: packages pages currently gate on `deal_desk:inventory` in code, but Packages is a Trade
> concept — see the open decision below.

### Brand Center — gate on `brand_center`

| Resource ID | Route | Actions used | Product |
|---|---|---|---|
| `deal_desk:brands` | `/deal-desk/brands`, `/[id]` | view, create, update | `brand_center` |
| `deal_desk:hub_settings` | `/deal-desk/hub-settings` | view, update | `brand_center` |
| `deal_desk:brand_portal` | `(BrandPortalLayout)/portal/*` (home, inventory, campaigns, creative, trade-funds, reports) | view | `brand_center` |

> The Brand Portal is additionally guarded by `BrandPortalGuard` (only `userLevel === 'brand'` or an
> active "view as brand" preview). Vendor isolation (a brand user seeing only their own vendor's
> records) is a resource-attribute/back-end concern, not part of product gating.

### Shared / core + Footprint — **RESOLVED** (owner decision, 2026-07-15)

| Resource ID | Route | Gate | `RESOURCE_META.products` |
|---|---|---|---|
| `deal_desk:dashboard` | `/deal-desk` | any of the three | `[ssp, trade, brand_center]` |
| `deal_desk:campaigns` | `/deal-desk/campaigns/**` | any of the three | `[ssp, trade, brand_center]` |
| `deal_desk:inventory` | `/deal-desk/inventory{,/catalog}` | any of the three | `[ssp, trade, brand_center]` |
| `deal_desk:revenue` | dashboard revenue widgets | any of the three | `[ssp, trade, brand_center]` |
| `deal_desk:loop` | `/deal-desk/inventory/loop` | **SSP only** | `[ssp]` |
| `deal_desk:store_traffic` | `/deal-desk/inventory/traffic` | **SSP or Trade** | `[ssp, trade]` |
| `footprint:store_map` | Footprint multi-store map | **base — all retailers** | `[]` (no product gate) |
| `footprint:blueprint` | Footprint blueprint | **base — all retailers** | `[]` (no product gate) |

Gating semantics: a resource is permitted when the principal holds **any** product in its
`RESOURCE_META.products` list. So:
- **"any of the three"** → `products: [ssp, trade, brand_center]` → visible if the retailer has ssp OR
  trade OR brand_center (the shared campaign/inventory/dashboard shell that all three build on).
- **loop** → `[ssp]`; **store_traffic** → `[ssp, trade]`.
- **footprint store-map + blueprint** → **base**: empty `products` list = no product condition;
  every retailer sees them (policy allows all retailer roles, no product check).

> `packages` (`deal_desk:packages`) remains **Trade** (`[trade]`) per the Trade table above. Packages
> pages currently gate on `deal_desk:inventory` in code — the next round should split Packages onto
> its own `deal_desk:packages` gate so it follows `trade`, not the any-of-three inventory shell.

## 4. Roles (reference)

`principal.roles = [DerivedRole]`, derived from userLevel×userType in
`src/lib/cerbos/server/build-principal.ts`:

| userLevel | owner | admin | lead | member | collaborator |
|---|---|---|---|---|---|
| retailer | RETAILER_OWNER | RETAILER_MANAGER | TEAM_LEAD | STAFF_OPERATOR | GUEST_COLLABORATOR |
| su | ROOT_USER | PLATFORM_ADMINISTRATOR | PLATFORM_LEAD | PLATFORM_MEMBER | PLATFORM_COLLABORATOR |
| agency | AGENCY_OWNER | AGENCY_MANAGER | AGENCY_LEAD | AGENCY_MEMBER | AGENCY_COLLABORATOR |

Product gating is orthogonal to role: a policy typically grants an action to a set of roles **and**
requires the product (`'"trade" in P.attr.products'`). SU/agency conventionally bypass product checks
— confirm the exact bypass rule with the existing `conqrse-cerbos` policies.
