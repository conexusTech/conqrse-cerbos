# In-View Visibility

**Question:** once a retailer can open a *shared* Deal Desk page, what appears inside it based on
`ssp` / `trade` / `brand_center`?

## Mechanism (real model — two options)

The page-level gate is `<CanI resource="deal_desk:…" action="view">`. For *sub-sections within a
shared page*, there is no fine-grained resource yet. Two ways to gate them, in order of preference:

1. **Client product check (no new Cerbos resources).** `GET /api/permissions` already returns
   `userProducts` (the retailer's products) and `availableProducts`. A shared page can read these
   (via `CerbosProvider` / `useCerbos()`) and conditionally render a section, e.g.
   `hasProduct('ssp')`. Cheapest; use for pure show/hide of presentational sections.
2. **New sub-resource keys.** If a sub-section needs its own allow/deny (not just product presence)
   — e.g. role-restricted within the product — add a dedicated `deal_desk:*` resource and gate it
   with `<CanI>`. Heavier; use only when a product check isn't enough.

Hidden means **fully hidden**, never greyed-out.

## Campaign Builder / Campaign pages (`deal_desk:campaigns`, shared shell)

| Section | Show when | Suggested gate |
|---|---|---|
| Campaign details, review | always (page open) | page `<CanI deal_desk:campaigns>` |
| Digital / programmatic inventory + KVP targeting + takeover + share-of-play | `ssp` | product check `hasProduct('ssp')` |
| Physical placement inventory + trade-fund field | `trade` | product check `hasProduct('trade')` |
| Rule-triggered creative | `ssp` | product check |
| "Link to brand" / brand association | `brand_center` | product check |

With `ssp` + `trade` both present, the builder shows both inventory paths (unified planning).

## Campaign Report (`deal_desk:campaigns`, report route)

| Panel | Show when |
|---|---|
| Executive summary, proof-of-play | always |
| Digital / SSP performance panel | `ssp` |
| Physical / Trade performance panel | `trade` |
| Attribution (POS) | data-driven (not product-gated) |

## Inventory dashboard (`deal_desk:inventory`, shared)

| Section | Show when |
|---|---|
| Fill-rate / utilization cards | always |
| Share-of-play / takeover-impact widgets, loop visualizer | `ssp` |
| Packages, physical placement utilization | `trade` |

## Deal Desk dashboard (`deal_desk:dashboard`, shared)

Show SSP health tiles when `ssp`; trade compliance/fund tiles when `trade`; brand-relationship tiles
when `brand_center`. The shared campaign/revenue tiles show whenever the retailer has **any** of the
three products (the `deal_desk:dashboard`/`revenue` any-of-three gate — see
PRODUCT-AND-RESOURCE-MODEL.md §3). Footprint store-map / blueprint are base (all retailers).

## Brand Portal inventory tabs (`deal_desk:brand_portal`, brand user)

Tab visibility follows the **host retailer's** products (a brand only browses what the retailer sells):

| Tab | Show when |
|---|---|
| Calendar | always |
| Digital | host retailer has `ssp` |
| Physical, Packages | host retailer has `trade` |

## Note for the next round

If option 1 (client product check) is chosen, the shared pages need a small `hasProduct(x)` helper
over `userProducts` from `CerbosProvider`. Enumerate each shared page's sections against this table
during implementation and wrap them accordingly. None of this requires new Cerbos policies — only
the page-level `deal_desk:*` gates (and their product conditions) do.
