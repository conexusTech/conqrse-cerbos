# Cerbos Action Plan — Digital Inventory Provisioning & SSP Mode

> **Status:** Cerbos repo IMPLEMENTED + verified · api3 partially implemented · admin blocked on package publish (see §8).
> **Author:** Claude (for Joe Lacerna) · **Date:** 2026-07-17
> **Sources:** `prd-digital-inventory-provisioning-ssp-mode.md`, `deal-desk-digital-inventory-gap-analysis.md`
> **Decisions applied (2026-07-17):** "retailer admin" = `retailer_owner` + `retailer_manager` (owner tier + retailer/`admin` user type, per `_derived_roles.yaml`); Deal Desk KVP tags gated by **extending existing tag policies** (not a new tag namespace); admin-only policies rendered via a **generator extension** (Option A); taxonomy-admin resource named **`contents:tags_taxonomy`**.
> **Scope:** authorization only — Cerbos policies + the enforcement wiring they require in `conqrse-api3` and `conqrse-admin`. The provisioning service, schemas, and calendar pipeline (PRD B1/B1b) are separate build work and are out of scope here except where a route needs an auth gate.

---

## 0. Where the requirements come from

The gap analysis carries **no** Cerbos requirements. The PRD names Cerbos gating in six places:

| PRD ref | Requirement |
|---|---|
| §4.8 (line 929) | Provisioning **sync** trigger → retailer-admin; provisioning **status** / per-unit reads → any retailer role with inventory read access |
| §6.4 (line 1467) | Tag **taxonomy administration** → retailer-admin; brand users excluded |
| §8.4 / §8.5 (lines 2349, 2378, 2390) | "Run sync" button → retailer-admin Cerbos action; module behind `hasProduct('ssp')` |
| §7.4 (line 1822) | Brand-audience redaction on `role === 'brand'` — BFF response shaping, **not** a policy change (inventory brand path already exists) |
| §9 (line 2634) | Activation routes Cerbos-checked per convention — covered by existing `dealdesk:campaigns` |
| §6 (whole) | `TagEntity` becomes the single KVP schema; consumed by Deal Desk search/routing |

Net new authorization surfaces: **(A) provisioning sync**, **(B) tag/taxonomy gating for Deal Desk**.

---

## 1. The generator constraint (central design decision)

Policies are generated from `docs/RESOURCES_ACTIONS_MATRIX.md` by `scripts/generate_policies.py`. Two hard limits:

- **Fixed action vocabulary:** `list, view, create, update, delete, export, import` only (`packages/permission-types/enums/action.enum.ts`). No `sync`/`provision`/`administer` verb — model new surfaces with standard CRUD verbs (sync trigger = `create`).
- **No admin-only product template.** The five renderer categories are `product_resource` (operator + collaborator blocks — includes `team_lead`, `staff_operator`), `dealdesk_resource` (retailer + collaborator + **brand** blocks — broadest), `product_settings` (owner/admin/lead, **no** collaborator/brand — but classifier requires a `settings:` name prefix), `admin_settings`, `user_settings`. None emits "product-gated, `retailer_owner`+`retailer_manager` only, no collaborator, no brand" for a `dealdesk:`/`contents:` resource.

**Decision (locked 2026-07-17): Option A — extend the generator.** Add an `admin_product_resource` category triggered by a matrix marker (e.g. an `admin-only` annotation column), reusing the `product_settings` role set (`root_user, platform_administrator, platform_lead, agency_owner, agency_manager, agency_lead, retailer_owner, retailer_manager`) with an `.exists()` product gate and `retailerId` check on `:item`. Keeps the matrix as SSoT and everything regenerable. ~30–50 lines in `PolicyRenderer` + classifier.

> **Admin gate = `retailer_owner` + `retailer_manager`** (locked). Owner is the tier above admin — an owner blocked from what a manager can do would be a defect. The `product_settings` role set already carries both, so no per-resource role override is needed.

---

## 2. Cerbos repo (`conqrse-cerbos`) — changes

### 2.1 New resource: `dealdesk:inventory-provisioning` (admin-only)
- **Purpose:** gate the sync trigger (`POST .../inventory/provisioning/sync`).
- **Actions:** `create` (trigger sync/backfill). *Status* and *per-unit* reads stay on existing `dealdesk:inventory` `view` (already broad — satisfies "any retailer role with read access").
- **Product gate:** `ssp` (provisioning writes only exist for SSP retailers, PRD D7 / §4.8.1 `409 PRECONDITION_FAILED`).
- **Roles:** admin-only (Option A/B above).
- **Files:** `k8s/base/policies/resource_dealdesk_inventory-provisioning.yaml` (no `:item` — it's an action, not an entity).

### 2.2 New resource: `contents:tags_taxonomy` (+ `:item`) (admin-only)
- **Purpose:** gate taxonomy-key administration (`POST/PATCH/DELETE .../tags/taxonomy`). Taxonomy **reads** (rule-builder pickers, §6.7c) are broad → served by `contents:tags` `view`/`list`, not this resource.
- **Actions:** collection `create, update, delete` (+ `list, view` optional if we want an admin-only management list); item `update, delete`.
- **Product gate:** union — `compliance, priceTags, product, qr, signage, ssp, trade, brand_center` (one taxonomy serves all tiers).
- **Roles:** admin-only; **brand roles explicitly excluded** (PRD §6.4).
- **Files:** `resource_contents_tags_taxonomy.yaml`, `resource_contents_tags_taxonomy_item.yaml`.

### 2.3 Extend existing tag policies (per decision: extend, don't fork)
Add `ssp, trade, brand_center` as `required` (OR) to the product gate of:
- `contents:tags`, `contents:tags:item`
- `contents:tags_assignments`, `contents:tags_assignments:item`

Today these gate only on `compliance, priceTags, product, qr, signage`, so an SSP-only Deal Desk retailer cannot assign/read tags — this unblocks the entire B3 unified-KVP layer (zone/asset assignment via `contents:tags_assignments`). `TagModel.ZONE`/`ASSET` are api3 domain-enum values, invisible to Cerbos — no policy change for the new tiers beyond the product gate.

### 2.4 Mechanical steps (per `POLICY_GENERATION.md`)
1. Edit `RESOURCES_ACTIONS_MATRIX.md`: add rows to the **DealDesk** and **Content** resource-actions tables **and** the Product × Resource Matrix (new rows for 2.1/2.2; edit product cells for 2.3). If Option A: add the admin-only marker.
2. (Option A) implement the generator category + renderer; (Option B) hand-author the two admin YAMLs.
3. `python3 scripts/generate_policies.py --resource "<name>" --force` for each new/changed resource (or hand-write for B).
4. Add the new policy files to `k8s/base/kustomization.yaml` `configMapGenerator.files:` allowlist — **easy to forget; a policy not listed never reaches a cluster.**
5. `python3 scripts/generate_types.py --force` → regenerates `@conqrse/permission-types` (new `Resource` enum members + `RESOURCE_META` products).
6. Bump `packages/permission-types/package.json`; `cd packages/permission-types && npm run build`; publish to the private registry.
7. `cerbos compile k8s/base/policies/` + `make test`.
8. Add policy tests under `tests/` for: admin gets sync (`create`) allow; `team_lead`/`staff_operator`/`guest_collaborator`/brand get deny on sync; taxonomy write allow admin-only + brand deny; extended tag product gate allows an SSP-only retailer.

**Reading:** matrix, generator, `resource_dealdesk_inventory.yaml`, `resource_contents_tags*.yaml`, `kustomization.yaml`.
**Writing:** matrix rows; ≤3 new YAMLs; 4 edited YAMLs; generator (Option A); enums (regen); kustomization; tests.

---

## 3. `conqrse-api3` — enforcement wiring

Pattern: `@UseGuards(AuthenticationGuard, [DealDeskResourceGuard,] CerbosAuthorizationGuard)` + `@RequirePermission('<resource>', '<action>')`. Resources/actions are **string literals** here (this repo does **not** consume `@conqrse/permission-types`).

### 3.1 New provisioning controller
`src/backend/controllers/deal-desk/provisioning.controller.ts`, registered in `src/backend/backend.module.ts` (near `InventoryController`):
- `POST retailers/:retailer/inventory/provisioning/sync` → `@RequirePermission('dealdesk:inventory-provisioning', 'create')`
- `GET  retailers/:retailer/inventory/provisioning/status` → `@RequirePermission('dealdesk:inventory', 'view')`
- `GET  retailers/inventory/:endpointId/:zoneId` (per-unit read, §4.8.3) → `@RequirePermission('dealdesk:inventory', 'view')` — no `:retailer` param, so use the `@DealDeskResource` entity-hydration decorator to resolve the retailer.

> The service/logic behind these routes is PRD B1 build work — out of scope here; this plan only fixes the auth gates.

### 3.2 Cerbos-gate the existing `TagController` (net-new enforcement)
`src/backend/controllers/tag.controller.ts` is v1 with **only** `AuthenticationGuard` today — its routes are ungated. Add `CerbosAuthorizationGuard` + `@RequirePermission`:
- assign / lookup routes → `contents:tags_assignments` (`create` for assign, `view` for lookup)
- tag CRUD → `contents:tags` (`create/update/delete/view/list`)
- **new** taxonomy CRUD routes → `contents:tags_taxonomy` (`create/update/delete`); taxonomy reads → `contents:tags` `view`
- **Blocker to resolve:** `PUT retailers/tags/:id/assign` has no `:retailer` URL param. The guard reads `:retailer`/`:retailerId` only, so this route needs either a `:retailer` path segment, a `@DealDeskResource` hydration, or retailer resolution from the tag entity. Confirm the shape before wiring.

### 3.3 Versioning caveat (confirm)
Existing routes are `v1` under `@Controller('v1/deal-desk')` with param `:retailer`. The PRD specifies `v2` `/retailers/:retailerId/...`. The guard accepts either param name, but a `v2` prefix + dropping the `deal-desk` segment diverges from convention. Confirm intended versioning before adding routes.

**Reading:** `cerbos-authorization.guard.ts`, `require-permission.decorator.ts`, `deal-desk-resource.decorator.ts`, `inventory.controller.ts`, `tag.controller.ts`, `backend.module.ts`.
**Writing:** new `provisioning.controller.ts` + module registration; guard/decorator additions on `tag.controller.ts`.

---

## 4. `conqrse-admin` — FE gating

Server-side Cerbos runs once in `src/app/api/permissions/route.ts` (batch check); the client gates declaratively via `useCerbos()` + `<CanI>`. FE consumes the `Resource`/`Action` enums from `@conqrse/permission-types`.

1. **Bump `@conqrse/permission-types`** to the version published in §2.6 (new `Resource.DEALDESK_INVENTORY_PROVISIONING`, `Resource.CONTENTS_TAGS_TAXONOMY`).
2. **Map them** in `src/lib/permissions/deal-desk-resources.ts` (`DealDeskResource` map) and add to `DEAL_DESK_GLOBAL_PERMISSIONS` so `/api/permissions` batch-checks them.
3. **"Run sync" button** (Inventory Dashboard, §8.4/8.5): wrap in `<CanI resource={DealDeskResource.INVENTORY_PROVISIONING} action="create" retailerOnly>` **and** `hasProduct(RetailerProduct.SSP)`. Because the policy is admin-only, `<CanI>` correctly hides it from non-admins — the FE has no `userType` check, and none is needed.
4. **Taxonomy admin UI** (new section in Tag Manager): gate writes with `<CanI resource={TAG_TAXONOMY} action="create|update|delete" retailerOnly>`; reads via `contents:tags` `view`.
5. **Sellability funnel / SSP-mode zone panel:** gate with existing `dealdesk:inventory` `view` + `hasProduct(RetailerProduct.SSP)`.
6. **Menu entries** (`MenuItems.ts`) with matching `permissionKey` = `` `${resource}:${action}` `` + `retailerOnly`.

**Reading:** `deal-desk-resources.ts`, `api/permissions/route.ts`, `CanI.tsx`, `CerbosProvider.tsx`, `MenuItems.ts`, an existing SSP client (e.g. `DspBlocksClient.tsx`).
**Writing:** enum bump; `deal-desk-resources.ts` map + global-permissions; `<CanI>` wrappers on the sync button + taxonomy UI; menu entries.

---

## 5. Sequencing

| # | Repo | Step | Depends on |
|---|---|---|---|
| 1 | cerbos | Resolve §1 (Option A vs B) + owner-inclusion question | — |
| 2 | cerbos | Matrix rows + policies (2.1–2.3) + kustomization + tests | 1 |
| 3 | cerbos | Regen `@conqrse/permission-types`, version bump, publish | 2 |
| 4 | api3 | Gate `TagController`; add provisioning controller gates | 2 (string literals — needs only the policy names, not the npm pkg) |
| 5 | admin | Bump pkg, map resources, `<CanI>` gates, menu | 3 |

api3 (4) can start as soon as the resource names are frozen (2); it does not wait for the npm publish. FE (5) needs the published package.

---

## 6. Decisions

**Resolved 2026-07-17:**
1. ✅ Generator: **Option A — extend** with an `admin_product_resource` category. (§1)
2. ✅ Admin gate = **`retailer_owner` + `retailer_manager`**. (§1)
5. ✅ Taxonomy admin namespace = **`contents:tags_taxonomy`**. (§2.2)

**Still open (need api3/product input, don't block cerbos work):**
3. **API versioning/paths** — `v2` `/retailers/:retailerId` vs existing `v1/deal-desk` `:retailer`? (§3.3)
4. **`retailers/tags/:id/assign` retailer resolution** — how does the guard get the retailer for this param-less route? (§3.2)

---

## 8. Implementation status (2026-07-17)

**conqrse-cerbos — DONE & verified.**
- Generator extended: `required-admin` matrix marker → `admin_product_resource` category → owner/admin role set, no collaborator/brand (`scripts/generate_policies.py`, `scripts/generate_types.py`).
- Matrix: added `dealdesk:inventory-provisioning`, `contents:tags_taxonomy`(+`:item`); extended `contents:tags`/`contents:tags_assignments`(+items) product gates with `ssp, trade, brand_center`.
- Policies generated + added to `k8s/base/kustomization.yaml`. `cerbos compile` clean.
- `@conqrse/permission-types` regenerated, bumped **1.6.0 → 1.7.0**, built (dist has the new enums + `RESOURCE_META`). **Not published** (awaiting approval).
- Tests: 8 new cases in `tests/test-cases.json` (4 allow / 4 deny) — all pass against a local Cerbos. (Pre-existing 21 "Allow Scenarios" failures are an unrelated harness `resource:`-prefix format bug, untouched.)

**conqrse-api3 — partial.**
- `TagController` now runs `CerbosAuthorizationGuard`; gated the retailer-scoped routes: lookup → `contents:tags_assignments:view`, assign → `contents:tags_assignments:create` (renamed `:id`→`:retailerId`, it holds the retailer id), list → `contents:tags:list`, create → `contents:tags:create`, product-properties reads → `contents:tags:view`.
- **Not done (feature build / blocked):** `update`/`delete`/`findOne` key on the tag id — no retailer to resolve (D4); left ungated with a TODO (routes without `@RequirePermission` pass the guard through, so non-breaking). Provisioning + taxonomy controllers/services don't exist yet (B1/B3 build) — when built, gate with `dealdesk:inventory-provisioning:create` and `contents:tags_taxonomy:create|update|delete`.

**conqrse-admin — blocked.**
- Requires `@conqrse/permission-types@1.7.0` published + installed (currently 1.6.0; new enums absent) before any FE code can reference the new resources.
- Target UI surfaces ("Run sync", taxonomy admin, sellability funnel) are missing/stubs on `develop` (feature build) — nothing concrete to wrap in `<CanI>` yet.

## 7. TODO checklist

- [x] D1: generator Option A (extend); D2: owner + manager; D5: `contents:tags_taxonomy`
- [ ] D3: confirm API versioning; D4: assign-route retailer resolution (both api3-side, non-blocking for cerbos)
- [ ] cerbos: matrix rows (provisioning, taxonomy, extended tag products)
- [ ] cerbos: generator category (if A) / hand-authored YAMLs (if B)
- [ ] cerbos: 3 new + 4 edited policies; kustomization allowlist
- [ ] cerbos: regen permission-types, bump, build, publish; `cerbos compile` + tests
- [ ] api3: provisioning controller + gates; register in BackendModule
- [ ] api3: Cerbos-gate TagController (assign/lookup/CRUD/taxonomy)
- [ ] admin: bump pkg; map resources; `<CanI>` on sync + taxonomy; menu entries
