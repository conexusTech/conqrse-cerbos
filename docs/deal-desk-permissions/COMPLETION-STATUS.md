# Deal Desk Per-Surface Gating — Completion Tracker

Tracks implementation of the per-surface (`ssp` / `trade` / `brand_center`) Deal Desk
product-gating model against the spec in this folder (`README.md`,
`PRODUCT-AND-RESOURCE-MODEL.md`, `IN-VIEW-VISIBILITY.md`, `IMPLEMENTATION-HANDOFF.md`).

- **Baseline audit:** 2026-07-16
- **Status legend:** `[x]` done · `[~]` partial · `[ ]` not started
- Update the checkbox + the **Status** note in the same PR that changes the code, and cite evidence.

---

## Snapshot (2026-07-16)

| Area | State |
|---|---|
| B — conqrse-cerbos per-surface policies | ✅ Done & deployed (114/114, prod=staging) |
| A — `@conqrse/permission-types` | ✅ Done — published `1.6.0` (per-surface `RESOURCE_META`) |
| A — `@conqrse/api-types` | ✅ 3 products added & published (`5.15.0`); `DEAL_DESK` kept (deprecated) until api3 migrates (D) |
| C — conqrse-admin wiring | 🟡 C2 done (design decision); C5 in progress (foundation + dashboard); C1 deferred to D |
| D — conqrse-api3 | ❌ Not aligned — enforces the deprecated umbrella `dealdesk` product |

> **Root blocker:** `@conqrse/api-types` lacks `ssp/trade/brand_center` and still ships
> `DEAL_DESK='dealdesk'`. This blocks admin **C1** and the whole api3 migration (**D**).
> **Live risk:** api3 sends retailers' `products` into the *deployed per-surface* policies but
> retailers hold the umbrella `dealdesk` product → per-surface checks will DENY unless bypassed.

---

## A. SSoT packages

### A1 — `@conqrse/permission-types`
- [x] `Product` enum has `ssp`, `trade`, `brand_center` — **Done**
- [x] `Resource` enum has the `dealdesk:*` resources — **Done** (naming is `dealdesk:` not spec's `deal_desk:`; accepted)
- [x] `RESOURCE_META` per-surface products — **Done** (`generate_types.py`)
- [x] Version bump + publish — **Done** (`1.6.0` on npm.conqrse.com)
- [x] Bumped + installed in conqrse-admin — **Done** (`package.json ^1.6.0`)

### A2 — `@conqrse/api-types`  *(source: `conqrse-api3/packages/api-types`; two synced copies + `src/backend/entities/data/_common.entity.ts`)*
- [x] Add `SSP='ssp'`, `TRADE='trade'`, `BRAND_CENTER='brand_center'` to `RetailerProduct` (both copies) — **Done** (2026-07-16), bumped `5.14.0 → 5.15.0`
- [x] **Publish** `@conqrse/api-types@5.15.0` — **Done** (registry latest = 5.15.0)
- [x] Bump + install in conqrse-admin (`^5.15.0`, installed 5.15.0) **and** conqrse-api3 (`^5.15.0`, lockfile 5.15.0) — **Done**
- [x] Retire admin interim shim in `src/lib/available-products.ts` — **Done** (uses native `Object.values(RetailerProduct)`; removed dead `DEAL_DESK_PRODUCTS`)
- [ ] **Remove erroneous `DEAL_DESK='dealdesk'`** — **DEFERRED — blocked on D.** api3 still gates ~196 routes on the umbrella `["dealdesk"]`; removing now breaks it. Marked `@deprecated` in both copies; remove after api3 migrates off the umbrella.

## B. conqrse-cerbos policies
- [x] Per-surface `dealdesk:*` policies (single / any-of-three / ssp-or-trade / base) — **Done**
- [x] Matrix + status docs re-marked per-surface; `required-all` deprecated — **Done**
- [x] Gating tests (allow/deny) pass; policies seeded to staging + production — **Done**
- [ ] Confirm the SU/agency product-bypass rule is intended for per-surface dealdesk (spec open item) — **Verify**

## C. conqrse-admin wiring  *(branch `develop`)*
- [ ] **C1** Remove `RetailerProduct.DEAL_DESK` from `src/app/components/shared/retailer/types.ts:17,32` — **DEFERRED — coupled to D** (removing it from the picker stops provisioning the umbrella product api3 still requires)
- [x] **C2** Retire interim layer — **Done (design decision 2026-07-16)**
  - [x] `DealDeskResource.*` maps to real `Resource.DEALDESK_*` enums
  - [x] **BRAND_PORTAL kept intentionally** as a guarded surface (`BrandPortalGuard` + host caps + `CanI` grant), NOT a Cerbos resource; `PERMISSION_ENABLED=false` bypass retained by design. Header comment reframed from "interim" to intentional.
  - [x] **Mapping layer kept intentionally** (`deal-desk-resources.ts` semantic menu→resource map); full inline-delete rejected.
- [x] **C3** `DEAL_DESK_GLOBAL_PERMISSIONS` spread into `GLOBAL_PERMISSIONS` (`route.ts`) — **Done**
- [x] **C4** `ssp,trade,brand_center` in `NEXT_PUBLIC_AVAILABLE_RETAILER_PRODUCTS` (`.env`, `.env.production`, `.env.staging`) — **Done**
- [~] **C5** In-view section gating (`IN-VIEW-VISIBILITY.md`) — **In progress**
  - [x] Expose `userProducts` + `availableProducts` from `CerbosProvider` / `useCerbos()`
  - [x] Add `hasProduct(product)` helper over `userProducts`
  - [x] **Deal Desk dashboard**: Digital/Share-of-Play + Loop → `hasProduct(SSP)`; Physical/Placement → `hasProduct(TRADE)` (`DealDeskDashboardClient.tsx`)
  - [x] Brand Portal inventory tabs gate on real host capabilities (`BrowseInventoryClient.tsx`)
  - [x] **Demo-toggle pages** converted to `hasProduct` (localStorage toggle removed): `InventoryCatalog` (Digital→SSP, Physical→TRADE) + `CampaignScheduler` (digital media→SSP, physical→TRADE, floor-plan/conflicts→TRADE). Decision applied: **`digital` folded into SSP, `playlist`/audio no longer product-gated**.
  - [~] **Campaign builder** (`campaigns/new/*`) — **In progress**
    - [x] Details step: **Trade Fund** → `hasProduct(TRADE)` (`CampaignFlightBudget.showTradeFund`); **Brand link** → `hasProduct(BRAND_CENTER)` (`CampaignIdentity.showBrandLink`) — owner decision (2026-07-16) to gate the brand field
    - [ ] Inventory step (`InventorySearchClient`): ⚠️ **data-model finding** — this step is SSP/digital-only (endpoint types Screen/Stream/Audio + KVP targeting); there is **no physical-placement picker here**, so there's no clean digital-vs-physical split to gate, and gating the whole step behind SSP would break trade campaigns. Needs runtime tracing of how physical/Trade line items enter the builder before gating. **Recommend `/verify` or `/run`.**
    - [ ] Creative step (`CreativeUploadClient`): rule-triggered creative → SSP — pending (recommend runtime verification)
    - [ ] Review step (`CampaignReviewClient`): `DigitalLineItems`→SSP, `PhysicalLineItems`/`TradeFundImpact`→TRADE — pending; mind draft data-consistency (recommend runtime verification)
  - [ ] **Campaign report**: SSP/Trade panels currently **data-gated** (`composition.hasSSP`), arguably correct; decide whether to also product-gate — pending
  - [ ] **Inventory dashboard**: no clean ssp/trade sub-section split in current layout; would need `InventoryBreakdown` restructure — left any-of-three for now
- [~] **C6** Menu `permissionKey`s resolve to real resources — **Partial**
  - [x] Dashboard + Footprint sidebar entries (`MenuItems.ts`)
  - [ ] Brand Portal menu (`BrandPortalMenuItems.ts`) uses bypass-only placeholder → follows real gate after C2
- [x] REVENUE→`DEALDESK_INVENTORY` (any-of-three), LOOP→`DEALDESK_SSP` (ssp-only) per spec §3 — **Done**
- [ ] Verify: `yarn lint` + `yarn build` clean; exercise `/api/permissions` for `trade`-only, `ssp`-only, `brand_center`-only retailers — **Pending**

## D. conqrse-api3 migration  *(branch `develop`)*
> api3 has a complete Cerbos enforcement stack (client, guard, `@RequirePermission`, principal
> with `attr.products`, ~196 gated routes, ~30 Deal Desk controllers) but on the **deprecated
> single-`dealdesk`-umbrella-product** model. This is a substantial round of its own.
- [ ] Decide: migrate api3 to per-surface, or keep umbrella (needs product-owner call) — **Decision**
- [ ] Adopt `@conqrse/permission-types` (Resource/Action/Product) instead of hard-coded strings — **Not done**
- [ ] Move principal `products` to per-surface (`ssp/trade/brand_center`) once A2 lands — **Blocked on A2**
- [ ] Rewrite the ~196 `@RequirePermission('dealdesk:...')` gates to per-surface semantics — **Not done**
- [ ] Reconcile api3's `docs/DEAL_DESK_CERBOS_POLICIES.md` (umbrella) with conqrse-cerbos per-surface policies (single SSoT) — **Not done**
- [ ] Ensure retailers are (re)seeded with per-surface products, not umbrella `dealdesk` — **Not done**
- [ ] Verify end-to-end against deployed per-surface policies (no `PERMISSION_BYPASS`) — **Pending**

---

## Recommended order
1. **A2** — `@conqrse/api-types`: add the three products, remove `DEAL_DESK` (after verifying seed/back-end), publish. *Unblocks C1 + D.*
2. **C1 + C2** — admin cleanup (remove `DEAL_DESK`, retire interim layer + bypass, real `BRAND_PORTAL` resource).
3. **C5** — admin in-view `hasProduct()` gating.
4. **D** — api3 migration to per-surface (largest; its own PR/round) + retailer product re-seed.
5. **Verify** — B open item (SU/agency bypass), admin build/`/api/permissions`, api3 end-to-end.
