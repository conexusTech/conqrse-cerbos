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
| A — `@conqrse/permission-types` | ✅ Done — `1.6.0` (per-surface `RESOURCE_META`) |
| A — `@conqrse/api-types` | ✅ Done — `ssp/trade/brand_center` added; **umbrella `DEAL_DESK` removed** (`6.0.0`, breaking) |
| C — conqrse-admin wiring | ✅ C1 + C2 + C5 done (picker/label dropped `DEAL_DESK`, on api-types 6.0.0) |
| D — conqrse-api3 | ✅ Done — staging migrated + verified per-surface; umbrella removed (D1–D5). No prod backfill (Deal Desk not on prod) |

> **✅ RESOLVED (2026-07-16).** api-types `6.0.0` carries `ssp/trade/brand_center` and no longer
> ships `DEAL_DESK`. Staging's one umbrella retailer was migrated to per-surface and verified against
> the deployed Cerbos. The umbrella is fully removed across api3 + admin.

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
- [x] **Removed erroneous `DEAL_DESK='dealdesk'`** (2026-07-16) — deleted from both api-types copies, published `6.0.0` (breaking). Safe: audit showed only admin's picker referenced it; api3 gates via deployed per-surface policies, not the umbrella.

## B. conqrse-cerbos policies
- [x] Per-surface `dealdesk:*` policies (single / any-of-three / ssp-or-trade / base) — **Done**
- [x] Matrix + status docs re-marked per-surface; `required-all` deprecated — **Done**
- [x] Gating tests (allow/deny) pass; policies seeded to staging + production — **Done**
- [ ] Confirm the SU/agency product-bypass rule is intended for per-surface dealdesk (spec open item) — **Verify**

## C. conqrse-admin wiring  *(branch `develop`)*
- [x] **C1** Removed `RetailerProduct.DEAL_DESK` from `retailer/types.ts` (picker + label) (2026-07-16), on api-types `6.0.0`. Per-surface products (`ssp/trade/brand_center`) remain provisionable.
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
  - [x] **Campaign builder** (`campaigns/new/*`) — **Done** (gate at the source; downstream cascades)
    - [x] Details step: **Trade Fund** → `hasProduct(TRADE)` (`CampaignFlightBudget.showTradeFund`); **Brand link** → `hasProduct(BRAND_CENTER)` (`CampaignIdentity.showBrandLink`) — owner decision (2026-07-16) to gate the brand field
    - [x] Inventory step: line-item **mode/endpoint** options gated in `AddLineItemForm` (SSP→digital Screen/Stream, Trade→Physical; Playlist/Audio ungated) with a safe default. This is the true SSP/Trade discriminator (`DraftLineItem.mode`), not the digital-only inventory list.
    - [x] Creative step: rule-triggered creative is already data-driven (`isSSP = currentLI?.mode === 'SSP'`) → cascades from the mode gate; no redundant product gate added.
    - [x] Review step: `DigitalLineItems`/`PhysicalLineItems`/`TradeFundImpact` already render off `li.mode` + `draft.tradeFund` → cascades from the mode gate.
  - [x] **Retailer provisioning + build fix** (`retailer/types.ts`): added ssp/trade/brand_center to the product picker + label map (`Record<RetailerProduct>` was incomplete after api-types 5.15.0 — build-breaker caught by `tsc`). Enables SU/agency to provision per-surface products. DEAL_DESK umbrella retained (deferred to D).
  - _Verification: full-project `tsc --noEmit` clean + eslint clean. Live per-surface driving not run — the app is auth/backend-gated and the `PERMISSION_ENABLED=false` bypass returns empty `userProducts`, so runtime show-behavior needs a seeded retailer/backend._
  - [ ] **Campaign report**: SSP/Trade panels currently **data-gated** (`composition.hasSSP`), arguably correct; decide whether to also product-gate — pending
  - [ ] **Inventory dashboard**: no clean ssp/trade sub-section split in current layout; would need `InventoryBreakdown` restructure — left any-of-three for now
- [~] **C6** Menu `permissionKey`s resolve to real resources — **Partial**
  - [x] Dashboard + Footprint sidebar entries (`MenuItems.ts`)
  - [ ] Brand Portal menu (`BrandPortalMenuItems.ts`) uses bypass-only placeholder → follows real gate after C2
- [x] REVENUE→`DEALDESK_INVENTORY` (any-of-three), LOOP→`DEALDESK_SSP` (ssp-only) per spec §3 — **Done**
- [ ] Verify: `yarn lint` + `yarn build` clean; exercise `/api/permissions` for `trade`-only, `ssp`-only, `brand_center`-only retailers — **Pending**

## D. conqrse-api3 migration  *(branch `develop`)* — SCOPED 2026-07-16

> **Corrected understanding (supersedes the earlier "rewrite ~196 gates"):** api3 does **not** own
> Cerbos policies — it points `CERBOS_HOSTNAME` at the **deployed conqrse-cerbos policies (now
> per-surface)**; `docs/DEAL_DESK_CERBOS_POLICIES.md` is a reference map, not a deploy source. The
> guard passes the **subject retailer's `products` raw** into the principal. Verified: **every** api3
> `@RequirePermission('dealdesk:…')` kind already matches a deployed per-surface policy (exact list).
>
> ⇒ The per-surface gate is **already live** for api3. The only reason access isn't per-surface is that
> **retailers still hold the umbrella `dealdesk` product**, which the per-surface policies reject.
> **D is a data migration + cleanup, NOT a code rewrite.** No `@RequirePermission` change needed.

**Storage:** MongoDB/Mongoose; `retailer.entity.ts` `products: RetailerProduct[]`. No formal migration
runner found — the retailer backfill is a one-off script/DB op.

Steps (in order):
- [x] **D1 — Audit umbrella dependencies** (2026-07-16). Nothing in api3 code references `RetailerProduct.DEAL_DESK` or the bare `'dealdesk'` product beyond the (policy-side, per-surface) Cerbos gate — the enum member is defined but unused. In admin it appears only in the retailer provisioning picker/label (`retailer/types.ts`); the `DEAL_DESK_ENABLED` flag is a feature-rollout flag, not a per-retailer product check. ⇒ removal is code-safe once retailers are migrated.
- [x] **D2 — Backfill applied on STAGING** (2026-07-16) via `api3/scripts/deal-desk-backfill-products.ts --env .env --apply` (DB `conqrse-staging`). 1 retailer held `dealdesk` ("Video MP") → gained `ssp`+`trade`+`brand_center` (matched=1 modified=1). Dry-run default; prints target DB.
- [x] **D3 — Verified on STAGING** (2026-07-16) against the deployed Cerbos (`svc/cerbos` ns `staging`, `/api/check/resources`):
      - all-three principal → ALLOW ssp / trade-ledgers / brands / sites
      - ssp-only → ALLOW ssp, DENY trade-ledgers, DENY brands, ALLOW sites (base)
      - umbrella `dealdesk`-only → DENY ssp / trade-ledgers / brands, ALLOW sites (base)
      ⇒ per-surface gating confirmed live; umbrella grants nothing (⇒ D5 removal is safe).
- [x] **D4 — Docs updated** (2026-07-16): `api3/docs/DEAL_DESK_CERBOS_POLICIES.md` — superseded banner + conventions rows now per-surface; historical umbrella snippets flagged, pointing to the conqrse-cerbos SSoT.
- [x] **D5 — Umbrella removed** (2026-07-16): staging retailer `--remove-umbrella` (now per-surface only); `RetailerProduct.DEAL_DESK` removed from both api-types copies → published **`@conqrse/api-types@6.0.0`** (breaking); admin picker/label entries removed; admin + api3 on `^6.0.0`, `tsc` clean (admin) / prod build clean (api3, tests excluded). Completes **A2b + C1**.
- [x] **D6 — Done** (2026-07-17): api3's `@RequirePermission('dealdesk:…')` strings replaced with `@conqrse/permission-types` `Resource`/`Action` enums — 133 calls across 21 controllers, via a deterministic ts-morph codemod (`api3/scripts/deal-desk-adopt-permission-enums.ts`). `permission-types ^1.7.0` added as a runtime dep. `tsc` 0 errors; eslint clean on changed files. No behavior change (enum values == prior strings).

**Risk / ordering:** D2 is safe and reversible (additive). D5 is the only destructive step and must
follow a green D3. Keep `dealdesk` and the three products coexisting through the transition window.

---

## Status (updated 2026-07-16)
1. ✅ **A** (permission-types 1.6.0; api-types 5.15.0→6.0.0) · **B** (per-surface policies) · **C1/C2/C5** · **D1–D5**
2. ✅ Staging retailer migrated to per-surface + verified against deployed Cerbos; umbrella `DEAL_DESK` removed everywhere.
3. ✅ **D6** — api3 now uses `@conqrse/permission-types` `Resource`/`Action` enums in `@RequirePermission` (133 calls / 21 controllers).
4. ✅ **Housekeeping #1 (prettier)** — the 11 non-converted deal-desk controllers reformatted (`prettier`/`eslint --fix`); the deal-desk controllers dir now lints clean.
5. ℹ️ **#2 — api-types/api-sdk DTO drift (not Deal-Desk; informational).** `@conqrse/api-types` + generated `@conqrse/api-sdk` are regenerated & republished frequently (5.15→6.3 this session). Each regen can change DTO shapes; consumers written against older shapes — especially those using `as X` assertions — break when they install a newer version. Because the registry `latest` often lags source, a consumer bump jumps across accumulated changes at once, so drift errors appear together and unrelated to the bump's purpose. Instances this session (all resolved): admin `MediaPlayerChannelDetailClient` `ListResShape` casts (bridged `as unknown as`); api3 test files `MediaPlayerMonitoringDto.deviceId` / `BrandInventoryItemDto` / arg-count (fixed in later commits). **Current state: admin + api3 both `tsc` 0.** Mitigations: type against generated `*ListResDto` instead of `as` assertions; unify the list-wrapper type (`ListResShape` vs generated); publish api-types/api-sdk in lockstep + keep registry `latest` == source; add a consumer typecheck against latest api-types at publish time.
