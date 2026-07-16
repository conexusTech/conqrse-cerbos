# Deal Desk / SSP / Trade / Brand Center — Product-Gating Hand-off

**Status:** Documentation only. No code or policy files are changed by this deliverable.
**Purpose:** Give a future agent (or engineer) everything needed to add `ssp`, `trade`, and
`brand_center` as retailer products and gate the Deal Desk surfaces by them — in a later round.
**Branch:** authored on `feat/deal-desk-permissions-v2` (off `develop`).

> ⚠️ A first pass lives in [`_archive-stale-v1/`](./_archive-stale-v1/). It was built against the
> **superseded** `conqrse-permissions-main` model and is wrong. Ignore it; it's kept only for history.

## Read these in order

| Doc | What it gives you |
|---|---|
| [PRODUCT-AND-RESOURCE-MODEL.md](./PRODUCT-AND-RESOURCE-MODEL.md) | The corrected product list, the real `deal_desk:*` resource IDs, and the resource→product→action matrix. |
| [IN-VIEW-VISIBILITY.md](./IN-VIEW-VISIBILITY.md) | What shows/hides *inside* shared Deal Desk pages per product. |
| [IMPLEMENTATION-HANDOFF.md](./IMPLEMENTATION-HANDOFF.md) | The exact change plan for the next round — every file/repo to touch + the `conqrse-cerbos` policy spec + open decisions + verification. |

## The corrected model (what's actually true on `develop`)

Permissions are enforced through a typed SSoT, not ad-hoc strings:

- **SSoT package `@conqrse/permission-types`** exports the `Resource`, `Action`, `Product`, and
  `DerivedRole` enums, plus `RESOURCE_META: Record<Resource, { type, actions[], products[] }>`.
- **Products** ride on `principal.attr.products` (from `retailer.products`, filtered by
  `AVAILABLE_RETAILER_PRODUCTS`) **and** `resource.attr.products`. Cerbos policies gate with
  `expr: '"<product>" in P.attr.products'` (this exact pattern is documented in
  `src/app/api/permissions/route.ts`).
- **Resource kinds** follow `<namespace>:<resource>` (collection) + `:item` (item), e.g.
  `qr:campaigns`, `contents:playlists`, `footprints:sites`.
- **Roles**: `principal.roles = [one DerivedRole]`. Retailer users map owner→`RETAILER_OWNER`,
  admin→`RETAILER_MANAGER`, lead→`TEAM_LEAD`, member→`STAFF_OPERATOR`, collaborator→`GUEST_COLLABORATOR`
  (SU→`ROOT_USER`/`PLATFORM_*`, agency→`AGENCY_*`). See `src/lib/cerbos/server/build-principal.ts`.
- **Actions**: `list, view, create, update, delete, export, import`.

### Product decisions locked in (from the product owner)

- **Add three new products**: `ssp`, `trade`, `brand_center` — to `RetailerProduct`
  (`@conqrse/api-types`) and `Product` (`@conqrse/permission-types`).
- **`signage` is its own product** (the existing Content/Signage surfaces — `contents:*`,
  `signages:*`). It is **not** a Deal Desk base gate.
- **There is no base product** for Deal Desk. The `DEAL_DESK` value currently in `RetailerProduct`
  is an **error introduced on a feature branch** and must be removed. Deal Desk sub-surfaces gate
  directly on `ssp` / `trade` / `brand_center`.

## The enforcement chain (so you know where gating happens)

```
<CanI resource="deal_desk:…" action="view">        ← src/components/auth/CanI.tsx (strict: undefined key = deny)
  → CerbosProvider (src/lib/context/CerbosProvider.tsx)
    → GET /api/permissions                          ← src/app/api/permissions/route.ts
      → checkBatchPermissions()                     ← src/lib/cerbos/server/check-permission.ts
        → buildPrincipal() + buildResource()        ← products onto principal.attr / resource.attr
          → Cerbos HTTP client                      ← evaluates policies from the conqrse-cerbos repo
```

**Two gaps that make this net-new work:**
1. Deal Desk resource IDs are **interim strings** in `src/lib/permissions/deal-desk-resources.ts`
   — not yet in the SSoT `Resource` enum, and only granted under the `PERMISSION_ENABLED=false` bypass
   (they're absent from `GLOBAL_PERMISSIONS`).
2. **No product-family gating exists for Deal Desk yet.** Today all `deal_desk:*` keys are treated
   uniformly. Gating them by `ssp`/`trade`/`brand_center` is the change this hand-off scopes.

The actual Cerbos policy YAML lives in the **`conqrse-cerbos` sibling repo** (not checked out here);
conqrse-admin only *enforces*. So the next round spans three places: the two SSoT packages, this repo's
wiring, and `conqrse-cerbos`. IMPLEMENTATION-HANDOFF.md lays out all three.
