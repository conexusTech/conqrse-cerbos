# Implementation Hand-off (next round)

The change spans **three places**: the two SSoT packages, the `conqrse-cerbos` policy repo, and this
repo's wiring. Do them in this order — the enums must land before the wiring compiles.

## A. SSoT enum changes — `@conqrse/permission-types` + `@conqrse/api-types` (sibling packages)

1. **`@conqrse/api-types` → `data/_common.entity.ts` → `RetailerProduct`:**
   - Add `SSP = 'ssp'`, `TRADE = 'trade'`, `BRAND_CENTER = 'brand_center'`.
   - **Remove `DEAL_DESK`** (erroneous). Grep the API/back-end for any retailer seeded with
     `dealDesk` in `products` before removing.
2. **`@conqrse/permission-types` → `enums/product.enum.ts` → `Product`:** add the same three
   (`SSP`, `TRADE`, `BRAND_CENTER`). Keep string values identical to `RetailerProduct`.
3. **`@conqrse/permission-types` → `enums/resource.enum.ts` → `Resource`:** promote the interim
   Deal Desk keys into the enum using the `<namespace>:<resource>` (+ `:item` where an entity detail
   exists) convention. Suggested names (confirm against RESOURCES_ACTIONS_MATRIX):
   ```
   DEAL_DESK_DASHBOARD='deal_desk:dashboard'  DEAL_DESK_CAMPAIGNS='deal_desk:campaigns' (+:item)
   DEAL_DESK_INVENTORY='deal_desk:inventory'  DEAL_DESK_PACKAGES='deal_desk:packages'
   DEAL_DESK_LOOP='deal_desk:loop'            DEAL_DESK_STORE_TRAFFIC='deal_desk:store_traffic'
   DEAL_DESK_BRANDS='deal_desk:brands' (+:item)  DEAL_DESK_BRAND_PORTAL='deal_desk:brand_portal'
   DEAL_DESK_TRADE_LEDGER='deal_desk:trade_ledger' (+:item)  DEAL_DESK_HUB_SETTINGS='deal_desk:hub_settings'
   DEAL_DESK_WORK_ORDERS='deal_desk:work_orders'  DEAL_DESK_COMPLIANCE='deal_desk:compliance'
   DEAL_DESK_DSP_BLOCKS='deal_desk:dsp_blocks' (+:item)  DEAL_DESK_DEALS='deal_desk:deals'
   DEAL_DESK_WATERFALL_CONFIG='deal_desk:waterfall_config'  DEAL_DESK_DECISION_LOG='deal_desk:decision_log'
   DEAL_DESK_QUEUE_JOBS='deal_desk:queue_jobs'
   FOOTPRINTS_STORE_MAP='footprints:store_map'  FOOTPRINTS_BLUEPRINT='footprints:blueprint'
   ```
4. **`RESOURCE_META`** (in permission-types): add an entry per new resource:
   `{ type: 'collection' | 'item', actions: [...], products: [<gating product>] }`.
   Use the product from [PRODUCT-AND-RESOURCE-MODEL.md](./PRODUCT-AND-RESOURCE-MODEL.md) §3
   (ssp / trade / brand_center), and resolve the §3 open-decision rows first.
5. Version-bump + publish both packages; bump the versions in `conqrse-admin/package.json`; `yarn install`.

## B. `conqrse-cerbos` policy repo (sibling — not checked out here)

Mirror the existing policy style (see the `reports`/`footprints`/`contents` resource policies):

- One resource policy per new resource kind. Gate with the documented pattern
  `expr: '"<product>" in P.attr.products'` **plus** the role rules (which `DerivedRole`s get which
  actions). Confirm the **SU/agency product-bypass** convention from an existing policy and apply it.
- Update `docs/RESOURCES_ACTIONS_MATRIX.md` (build-resource.ts is "aligned" to it).
- Add policy tests (principals × products × expected effects), following the repo's test format.
- Validate: `cerbos compile --tests=… .` (use the repo's documented command).

> This hand-off intentionally does **not** ship policy YAML — per the product owner, policies are a
> separate round. Everything a policy author needs (resources, products, roles, actions, gating
> expression) is in the matrix docs.

## C. `conqrse-admin` wiring (this repo — after A lands)

1. **Remove the bad product usage:** delete the `RetailerProduct.DEAL_DESK` entries in
   `src/app/components/shared/retailer/types.ts` (~line 17 list, ~line 32 label map).
2. **Retire the interim layer** once `Resource.DEAL_DESK_*` exists:
   - Replace the `DealDeskResource.*` string usages at `<CanI>` call sites with `Resource.*`.
   - Delete `src/lib/permissions/deal-desk-resources.ts` and the `DEAL_DESK_INTERIM_PERMISSION_KEYS`
     import + grant block in `src/app/api/permissions/route.ts`.
3. **Wire real gating:** add each new Deal Desk resource to `GLOBAL_PERMISSIONS` in
   `src/app/api/permissions/route.ts`, following the existing rows:
   `{ kind: Resource.DEAL_DESK_X, action: Action.VIEW, products: RESOURCE_META[Resource.DEAL_DESK_X].products }`.
   Product gating then flows automatically (the route already sends `principal.attr.products`).
4. **Available products:** add `ssp,trade,brand_center` to `NEXT_PUBLIC_AVAILABLE_RETAILER_PRODUCTS`
   in the env(s) where they should be sellable (`src/lib/available-products.ts` reads it). Confirm
   they should appear in the SU/agency retailer-product pickers.
5. **In-view sections:** add a `hasProduct(p)` helper over `userProducts` (from `CerbosProvider`) and
   wrap shared-page sections per [IN-VIEW-VISIBILITY.md](./IN-VIEW-VISIBILITY.md).
6. **Menu:** confirm `MenuItems.ts` / `BrandPortalMenuItems.ts` `permissionKey`s resolve to the
   promoted resources so sidebar visibility follows the product gate.

## Decisions status

**Resolved (owner, 2026-07-15):**
1. ✅ **Shared/core + footprint → product mapping** — see PRODUCT-AND-RESOURCE-MODEL §3 (RESOLVED
   table): dashboard/campaigns/inventory/revenue = any-of-three `[ssp, trade, brand_center]`;
   loop = `[ssp]`; store_traffic = `[ssp, trade]`; `footprint:store_map` + `footprint:blueprint` =
   base (no product gate, all retailers).
2. ✅ **packages** stays Trade (`[trade]`); split it onto its own `deal_desk:packages` gate rather
   than the any-of-three `deal_desk:inventory` shell it currently rides on.
3. ✅ **Governing PRD** — `okf/prds/retailer-dashboard-product-gating.md` flipped to
   `status: accepted`. Note: it is dashboard-scoped; a **separate PRD should govern the Deal Desk
   surfaces** (don't expand the accepted PRD's scope, per OKF rules). Flip to `in-progress` in the PR
   that implements the code.

**Still open (confirm during policy authoring):**
- **SU/agency product bypass** — confirm the exact rule from the existing `conqrse-cerbos` policies
  (do SU/agency bypass the `"<product>" in P.attr.products` check as they do elsewhere?).

## Verification (next round)

- `@conqrse/*` packages: type-check + publish.
- `conqrse-cerbos`: `cerbos compile --tests` green.
- `conqrse-admin`: `yarn lint` + `yarn build` clean; then exercise `/api/permissions` with a retailer
  that has only `trade` → confirm trade surfaces resolve and ssp/brand surfaces are denied/hidden;
  repeat for `ssp`-only and `brand_center`-only; confirm brand-portal `BrandPortalGuard` still gates
  by `userLevel === 'brand'`.

## OKF concepts to read before implementing (all under `okf/`)

`business/product.md`, `models/product.md`, `business/{deal-desk,programmatic-ssp,trade-ledger}.md`,
`integrations/cerbos.md`, `models/cerbos-policy.md`, `api/permissions.md`,
`lib/cerbos-{build-principal,build-resource,check-permission}.md`, `pages/{deal-desk,settings-cerbos}.md`,
`playbooks/permission-denied.md`, and `prds/retailer-dashboard-product-gating.md`. Update the touched
concepts in the same PR and cite them (`OKF concepts read/updated:`), per the repo's OKF protocol.
