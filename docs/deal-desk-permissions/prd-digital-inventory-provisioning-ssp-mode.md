# PRD — Digital Inventory Provisioning & SSP Mode (Deal Desk Gap Closure)

## 1. How to Use This Document / Scope & Goals

> **Version:** 1.0
> **Last Updated:** July 2026
> **Author:** Jody Holmes
> **Status:** Engineering Handoff
> **Source Documents:** `deal-desk-digital-inventory-gap-analysis.md` (decision record, 2026-07-16), `prd-deal-desk-v2.md`, `phase-1-prd-backend-foundation.md`, `phase-2-prd-core-engine.md`, `phase-3-prd-frontend-integration.md`, `phase-4-prd-brand-portal-advanced-features.md`

### 1.1 How to use this document

**This is the authoritative document for the Digital Inventory Provisioning & SSP Mode build.** It supersedes any conflicting language in earlier docs — including the source PRD's §19 data model (layout attached directly to endpoint, channels as playlist-only constructs) and Phase 1 §3.14's "reference by ID, does not create" posture toward Cue entities, both of which this document explicitly amends. The companion documents (gap analysis, source PRD, phase PRDs, UI specs) are background context; engineering builds against this PRD. If something here is unclear or appears wrong, raise it back to product — do not silently fall back to another doc.

Every product decision in this document is **locked** (recorded 2026-07-16 in the gap analysis, D1–D9, plus two backend confirmations). This PRD expands those decisions into implementation-grade spec; it does not re-open them. §2 records each decision and its outcome so engineering can trace any requirement back to its authority.

Conventions follow the established phase-PRD contract: every entity, function, and endpoint is specified with purpose, TypeScript shape, behavior (representative pseudocode, not finished implementation), validation rules, and required tests. Phase 1 §2 conventions apply throughout (money in cents, percentages as decimals in [0, 1], durations in seconds, `retailerId` tenancy, soft-delete, Cognito auth, Avocado deployment). FE work follows Phase 3 §2 conventions (page/client separation, generated `cqQuery*`/`cqMutation*` hooks only, BFF proxy, queryKey-based cache invalidation).

Section map: §3 data model; §4 provisioning service; §5 SOV availability calendar and recalculation pipeline; §6 unified KVP tag architecture; §7 inventory search contract; §8 admin UI; §9 activation side effects; §10 acceptance criteria, test plan and sequencing; §11 glossary.

### 1.2 The problem this document closes

Engineering found that `inventory/search` returns empty for every retailer in production. Digital `InventoryUnit`s exist only as seeded test data — campaigns cannot be built end-to-end even where the physical footprint is fully configured. The canonical example: the "Video MP" estate has **854 stores and 66 players, and 0 sellable digital units**.

The gap analysis confirmed this is a spec gap, not a missed build:

1. **No PRD ever specified how a digital `InventoryUnit` or `TimeBudget` comes into existence.** Phase 1 §3.14 declared Endpoint/Store/Zone/Layout to be external Cue entities that Deal Desk "references by ID but does not create." Phase 2's inventory search reads exclusively from Deal Desk's own Mongo collections (`inventoryUnits`, `timeBudgets`, `rateCards`, `storeTraffic`). Nothing writes those collections, so search is empty by construction. Physical inventory got a production path (Blueprint/Onboarding CRUD); digital never did.
2. **Two systems of record, no bridge.** Cue owns the structural chain (Site → Endpoint → Channel → Layout → Zones, with full CRUD already in the API). Deal Desk owns the sellable ledger. The materialization contract between them fell between the two systems and no document claimed it.
3. **The source PRD's data model conflicts with the actual product model.** The word "channel" appears zero times in the Phase 1 and Phase 2 PRDs, and the source PRD attaches layouts directly to endpoints. The confirmed model (D1, §2.4) is channel-centric in both modes.
4. **The Deal Desk KVP layer was never connected to the platform's existing tag system**, and the tag system stops at the channel tier — zones cannot carry typed tags.

This document is the missing materialization contract, plus everything the confirmed concept model requires downstream of it: time-windowed share of voice (SOV) ledgers, the precomputed availability calendar, the unified tag architecture, the pinned search contract, the SSP-mode admin UI, and activation-time creative routing.

### 1.3 In Scope

Sections 3–9 of this document, in full:

1. **Data model** (§3) — `inventoryUnits` keyed on `(endpointId, zoneId)`, time-windowed `timeBudgets` (D8), `sovCalendars` (D9), booking-protection lock semantics, and amendments to existing entities.
2. **Digital Inventory Provisioning service** (§4) — derivation rule, lifecycle event handlers, SSP-activation backfill, P4 filler registration, invariant checks, and the provisioning API routes (`POST /v2/retailers/:retailerId/inventory/provisioning/sync`, `GET /v2/retailers/:retailerId/inventory/provisioning/status`). Closes gap-analysis build item B1.
3. **SOV availability calendar and recalculation pipeline** (§5) — the materialized per-unit calendar, the `sov-recalc` job on the Concourse queue, triggers, coalescing, and the full-rebuild admin job. Closes B1b.
4. **Unified KVP tag architecture** (§6) — one `TagEntity` schema for all tiers, `TagModel` extended with `ZONE` and `ASSET`, inheritance plus zone-local additive tags, static KVP contract, asset-tag migration. Closes B3.
5. **Inventory search contract** (§7) — the v2 layered contract (`POST /v2/retailers/:retailerId/inventory/search`: site scope → kvpRules → flight range → adDuration), calendar-backed reads, Campaign Builder Step 2 integration, removal of the `as never` cast and all hardcoded FE catalogs/constants. Closes B4 and resolves D6.
6. **Admin UI** (§8) — wiring the existing Cue chain components (endpoint→channel picker, channel/layout/zone editor, Tag Manager) to real hooks, the mode-adaptive SSP channel/zone view with SOV ledger panel and locked states, and the sellability funnel on the Inventory Dashboard. Closes B2 and B5, and fixes the two malformed tag-assign calls (gap analysis §4.1).
7. **Campaign activation side effects** (§9) — targeting resolution to a concrete endpoint set, creative pre-load via Cue content sync, waterfall hot-cache invalidation, per-endpoint sync status with retry, cancellation removal sync. Closes B6.
8. **PRD amendments** — this document *is* build item B7; §2 records the corrections to the source PRD and phase PRDs. The legacy Program/ProgramInventory system is explicitly deprecated (§2.6).

### 1.4 Out of Scope

| Feature | Disposition |
|---|---|
| Move/rebook flow for bookings on locked entities | Post-v1. v1 ships **clear-first**: release the blocking bookings, then edit/delete. The `409 BOOKINGS_EXIST` error contract (§3, §4) is designed so move/rebook slots in later without schema change. |
| Mixed-mode estates (per-endpoint or per-zone mode) | Post-v1. The SSP switch is **retailer-wide** (D7); the per-zone `sellable` flag stays in the schema for future mixed estates but has no v1 UI toggle beyond on/off within an SSP estate. |
| Dayparted SOV booking | Not planned as a booking concern. Bookings are a **constant % per flight** (D8); dayparting is a runtime-targeting concern handled by KVP rules and the waterfall, not the SOV ledger. |
| Scene live KVP values (real-time customer counts, demographic triggers) | Interface declared in the decide-time context bag (§6); activation is source-PRD Phase 7. |
| Accrual-based and Hybrid Trade Fund types | Trade Platform Phase 2 (requires POS integration). |

### 1.5 Done Means

- SSP package activation for a retailer materializes one `InventoryUnit` + one `TimeBudget` per `(endpointId, zoneId)` for every active endpoint carrying a channel, registers each zone's existing playlists as its P4 filler pool, and initializes its SOV calendar at 100% available — "854 stores / 66 players / 0 sellable units" becomes real, correct numbers with no seed data involved.
- Every lifecycle event in §4.4 (channel assigned/unassigned, layout attached/changed, zone added/edited/removed, endpoint retired, sellable toggled) keeps the sellable ledger in sync, and mutations that would invalidate active or future bookings are rejected with `409 BOOKINGS_EXIST` listing the blocking bookings.
- `POST /v2/retailers/:retailerId/inventory/search` implements the layered contract of §7, reads availability exclusively from `sovCalendars`, and the FE calls it through regenerated SDK hooks with no `as never` cast and no hardcoded metric constants.
- Booking commits validate transactionally against the authoritative `timeBudgets` bookings with optimistic version locking — never against the calendar — and staleness surfaces as the existing `409 OVERBOOKING` / `409 STALE_WRITE` treatments (Phase 3 §4.2).
- Effective KVPs resolve for every provisioned unit as site ∪ endpoint ∪ channel ∪ zone-local (most-specific tier wins), through the single `TagEntity` schema with `TagModel.ZONE` and `TagModel.ASSET`.
- The admin chain UI is fully wired (no stubbed arrays, no `setTimeout` saves), the channel detail view renders the SSP-mode SOV ledger variant when the retailer-wide switch is on, and the Inventory Dashboard sellability funnel makes any provisioning gap diagnosable in-product.
- Campaign Ready→Active resolves targeting to concrete endpoints, pushes creatives via Cue content sync with per-endpoint status and retry, and invalidates the waterfall hot cache.
- Acceptance gates in §10 pass; each build item's required tests are green.

---

## 2. Confirmed Concept Model & Architecture

Everything in this section was decided with product on 2026-07-16 and recorded in the gap analysis (§1.5, §3, §3.1). It is restated here as the normative model the rest of this document expands. Nothing here is open.

### 2.1 One structural chain, two content modes

The chain `Site → Endpoint → Channel → Layout → Zones` exists in **both** modes. The channel has two jobs the original source PRD conflated: **structure** (carrying the layout of zones — survives in both modes) and **content scheduling** (playlists — Cue mode only). SSP mode removes the *playlist/schedule* layer from zones; it does not remove the channel.

```
                        Endpoint → Channel → Layout → Zone
                                                        │
        ┌───────────────────────────────────────────────┴──────────────────────────────┐
        │ MODE 1 — Cue (existing)                MODE 2 — Deal Desk / SSP (new)         │
        │ Zone → Schedules → Playlists           Zone → SOV Loop (fixed loop clock)     │
        │ Retailer curates content order         Playlist layer removed from the zone   │
        │ Dynamic loop = playlist length         Campaigns book % share of voice (SOV)  │
        │                                        Waterfall (P1→P4) fills each loop      │
        │                                        iteration; filler takes the remainder  │
        └────────────────────────────────────────────────────────────────────────────────┘
```

Consequences engineering must hold onto:

- **The channel is never bypassed.** There is no "layout attached directly to endpoint" path in either mode. Source PRD §19 is amended accordingly (D1).
- **One channel serves many endpoints** (D2). The same zone definition on the same channel becomes one sellable unit *per endpoint carrying the channel*. The unit of uniqueness everywhere in this document — `inventoryUnits`, `timeBudgets`, `sovCalendars`, `rateCards`, bookings, calendar API paths — is **`(endpointId, zoneId)`**. zoneIds are stable for the life of a channel (Backend Confirmation #1, §2.5).
- **Playlists are demoted, not deleted.** On SSP activation, each zone's existing playlist schedules are registered as that zone's **P4 filler pool** (§4.3). Zero-content screens are impossible; the retailer's content investment is preserved.
- **The loop clock is endpoint-level.** One loop clock per endpoint per store (Backend Confirmation #2, §2.5). `loopDuration` lives at the endpoint; retailer defaults live in the SSP waterfall config; per-zone loop-duration overrides do not exist. Default changes never retroactively apply to endpoints with active bookings.

### 2.2 Booking layer vs. runtime layer

Two layers keep SSP mode honest. They share vocabulary but never share a write path:

| | Booking layer (sales time) | Runtime layer (playback time) |
|---|---|---|
| **Question answered** | "How much of this zone is sold for Aug 1–31?" | "What plays in *this* loop iteration, right now?" |
| **Data** | Each `(endpointId, zoneId)` unit carries a share of voice (SOV) ledger: `timeBudgets` bookings with `flightStart`/`flightEnd` and a constant share % per flight (D8) | Waterfall walks P1 → P4 each loop iteration; pacing nudges under-delivered campaigns so actual plays converge on booked share over the day |
| **Derived view** | `sovCalendars` — precomputed day-granularity availability (D9), recalculated via the `sov-recalc` job on the Concourse queue (§5) | Decision logs + proof-of-play (Phase 2, unchanged) |
| **Readers** | Inventory search (§7), SOV ledger UI (§8), Brand Portal calendar heatmap | Endpoint runtime, pacing engine |
| **Writers** | Booking engine only — commits validate transactionally against `timeBudgets.bookings[]` with optimistic version lock, **never** against the calendar | Waterfall/pacing only |

Availability over a window = `100% − max concurrent booked share over the requested interval`. Because bookings are a constant % per flight, availability is a step function that only changes at flight boundaries — which is what makes day-granularity calendar buckets sufficient (§5).

### 2.3 Campaign fan-out trace

One campaign spans many endpoints/zones. The tracked trace, end to end:

```
campaign
  → line items
    → per-zone bookings            (share % against that (endpointId, zoneId) unit's SOV ledger)
      → per-zone asset assignment  (creative variant matching the zone's dims/specs, via tag join — §6, §9)
        → runtime loop placements  (waterfall P1→P4 per loop iteration)
          → proof-of-play          (rolled up per (campaign, zone))
```

Sections downstream own the links: §4 makes the units exist, §5 makes availability readable, §7 makes them findable, §9 routes the creative, and Phase 2's runtime (unchanged) executes the loop.

### 2.4 Decisions locked 2026-07-16 (D1–D9)

| # | Decision | Outcome |
|---|---|---|
| **D1** | Canonical hierarchy | **Endpoint → Channel → Layout → Zones in both modes.** Channel carries structure always; playlists are its Cue-mode content role only. Source PRD §19 amended by this document. |
| **D2** | Channel : endpoint cardinality | **1 channel : many endpoints.** A zone in an endpoint is what makes a sellable unit unique — identity is `(endpointId, zoneId)`. Safe because zoneIds are stable for the life of a channel (Confirmation #1). |
| **D3** | Materialization strategy | **Sync job + lifecycle events** (§4). The retailer-wide SSP switch makes the per-zone `sellable` flag optional in v1 (everything sellable when SSP is on); the flag stays in the schema for future mixed estates. |
| **D4** | Zone-level KVPs | **Inheritance plus zone-local additive tags.** Effective KVPs = site ∪ endpoint ∪ channel ∪ zone-local; most-specific tier wins on key collision. Requires `TagModel.ZONE` (§6). |
| **D5** | Loop config ownership | **`loopDuration` is endpoint-level** — one loop clock per endpoint per store (Confirmation #2). Retailer defaults live in SSP waterfall config; per-zone loop-duration override dropped; defaults never retroactively apply to endpoints with active bookings (booking-protection lock, §3). |
| **D6** | Search contract | **v2 layered multi-dimensional filter:** (1) site scope (explicit `siteIds[]` or all sites), (2) kvpRules layered on top, (3) flight date range, (4) adDuration. Response = per-zone remaining SOV over the window, read from the calendar. Pin against SDK 5.11; remove the `as never` (§7). |
| **D7** | SSP-activation semantics | **SSP activation is the retailer-wide switch and the backfill trigger:** activation materializes `inventoryUnits` + `timeBudgets` for every endpoint-with-channel and registers zone playlists as the P4 filler pool (§4.2–4.3). |
| **D8** | Time-windowed TimeBudget | **Bookings carry `flightStart`/`flightEnd`; availability is computed per interval** (100% − max concurrent booked share), never stored as a scalar. Phase 1's scalar `totalShareBooked`/`availableShare` schema is superseded (§3). Lands before the provisioning service writes any documents. |
| **D9** | Precomputed availability | **A materialized per-unit SOV availability calendar** (`sovCalendars`, day-granularity buckets) is recalculated on the Concourse queue (`sov-recalc`) whenever a booking-affecting change lands, keyed to affected `(endpointId, zoneId)` units only. Search reads the calendar; **booking commits validate against the authoritative `timeBudgets` bookings transactionally, never the calendar** — staleness surfaces as `409 OVERBOOKING` (Phase 3 §4.2). The calendar is a derived view, always rebuildable from bookings (§5). |

### 2.5 Backend confirmations (both answered 2026-07-16)

**Confirmation #1 — zoneId stability.** *Is `zoneId` stable for the life of a channel, across `CreateChannelLayoutV1` clone-attach, layout edits, and re-saves?* **Answer: yes — zoneIds are stable for the life of a channel.** Everything downstream keys on `(endpointId, zoneId)` safely: `timeBudgets`, bookings, `sovCalendars`, `rateCards`. The clone-vs-link mechanics of `CreateChannelLayoutV1` remain an implementation detail with no schema impact. No zone-identity migration policy is needed in v1; layout swap and zone deletion on booked inventory are instead governed by the booking-protection lock (below).

**Confirmation #2 — loop clock topology.** *Can one multi-zone screen run different loop durations per zone?* **Answer: no — one loop clock per endpoint per store.** Loop boundaries stay aligned to preserve top-of-the-hour takeovers; takeover impact is absorbed in the guarantee buffer (consistent with the conservative guarantee math, source PRD §3.6). Per-zone loop-duration overrides are dropped from the product. Config changes on booked inventory are governed by the booking-protection lock.

**Booking-protection lock (normative, referenced throughout):** any entity whose mutation would invalidate a booking — zone geometry/deletion, layout swap or detach, channel unassignment, endpoint retirement, loop config — is **locked from edit and delete while it carries active or future bookings** (any booking with `flightEnd >= today`; past bookings never lock). Enforcement is at the API layer with a structured error: `409 BOOKINGS_EXIST`, with `details` listing the blocking campaigns/bookings, so the UI renders a locked state with a resolution path (§8). v1 resolution is **clear-first** (release the bookings, then edit); move/rebook is post-v1 (§1.4).

### 2.6 System-of-record split, and how this PRD bridges it

| Concern | System of record | Owned entities |
|---|---|---|
| **Structure** | **Cue** | Site, Endpoint (MediaPlayer), Channel, Layout, Zone, per-zone Schedules/Playlists, device pairing |
| **Sellable ledger** | **Deal Desk** | `inventoryUnits`, `timeBudgets`, `sovCalendars`, `rateCards`, bookings, campaigns, proof-of-play rollups |
| **Tags** | **Shared, one schema** | `TagEntity`/`TagModel` (extended with `ZONE`, `ASSET`) — assigned against Cue entities and assets, consumed by Deal Desk search, decide-time context, and creative routing (§6) |

The root cause of the production gap was that both PRD lineages said "reference by ID, don't create" and no document owned the step from a Cue zone to a sellable Deal Desk unit. This PRD is that bridge, in four contracts:

1. **Derivation contract** (§4): for every active endpoint with a channel, for every zone in the channel's layout, Deal Desk upserts exactly one `InventoryUnit` + one `TimeBudget` keyed `(endpointId, zoneId)`. Cue remains the only writer of structure; the provisioning service is the only writer of derived units.
2. **Synchronization contract** (§4.3–4.4): Cue structural lifecycle events drive upserts/deactivations; the SSP-activation backfill (`POST /v2/retailers/:retailerId/inventory/provisioning/sync`) materializes the existing footprint and is re-runnable as a manual repair trigger, with `GET /v2/retailers/:retailerId/inventory/provisioning/status` exposing sync health.
3. **Identity contract** (§3): `(endpointId, zoneId)` is the join key both systems agree on, guaranteed by zoneId stability (Confirmation #1). No Deal Desk entity ever invents its own identity for a Cue structure.
4. **Protection contract** (§2.5, §3): the booking-protection lock is Deal Desk's veto over Cue structural mutations that would strand bookings — enforced at the API layer via `409 BOOKINGS_EXIST`.

**Deprecation:** the legacy Program/ProgramInventory system (`POST /v1/retailers/{retailer}/programs/inventory/search`, `ProgramPlayStats.guaranteedPlays`) is the unused ancestor of this design. It is **explicitly deprecated** — no new callers, no UI wiring; removal is scheduled after §7's search contract ships. There is exactly one inventory system.

---

## 3. Data Model & Entities

This section is the schema contract for the gap-closure build. It amends and extends Phase 1 §3 — where a shape below conflicts with Phase 1 (notably TimeBudget, per D8), **this section supersedes it**. Behavior that consumes these entities lives elsewhere: derivation and lifecycle events in §4, the recalculation pipeline in §5, tag semantics and taxonomy governance in §6, the search read path in §7.

Phase 1 conventions carry forward unchanged: one collection per top-level entity; every collection carries `retailerId`, `createdAt`, `updatedAt`, `deletedAt: Date | null` (soft delete); money in integer cents; **percentages as decimals in [0, 1]**; durations in integer seconds; ObjectIds serialized as hex strings at the API boundary.

Four collections are touched by this build: `inventoryUnits` (extended), `timeBudgets` (**reshaped** per D8), `sovCalendars` (**new**, per D9), and `rateCards` (unchanged shape; consumes the identity contract in §3.1). The tag system (`TagEntity` / `TagModel`) is extended, not replaced.

---

### 3.1 The (endpointId, zoneId) Identity Contract

**The unit of digital sellability is the pair `(endpointId, zoneId)`.** This is the D2 decision made durable: one channel serves many endpoints; the channel's layout defines zones once; each zone becomes one sellable unit *per endpoint carrying that channel*. The same `zoneId` therefore legitimately appears on many InventoryUnits — uniqueness is always the pair, never the zoneId alone.

**Stability guarantee (Backend Confirmation #1, answered 2026-07-16):** zoneIds are stable for the life of a channel. No supported operation — layout attach, zone edit, channel re-save — regenerates them. Everything downstream keys on the pair on the strength of this guarantee:

| Collection | Keyed by |
|---|---|
| `inventoryUnits` (`screen_zone_slot`) | `(endpointId, zoneId)` — unique |
| `timeBudgets` | `(endpointId, zoneId)` — unique, 1:1 with the unit |
| `sovCalendars` | `(endpointId, zoneId, month)` — unique |
| `rateCards` (zone rows in the endpoint upsert) | `zoneId` within an endpoint |
| Bookings, proof-of-play rollups | `(campaignId, endpointId, zoneId)` |

**Contract rules:**

1. Any operation that would destroy or replace a zoneId while the pair carries active or future bookings is refused with `409 BOOKINGS_EXIST` (§3.7). Layout swap and channel unassignment are the dangerous cases; both are covered by the booking-protection lock.
2. `zoneId` and `endpointId` are Cue-owned identifiers. Deal Desk never mints them; the provisioning service (§4) copies them verbatim.
3. `stream_slot` and `audio_slot` units have no zone — their identity is `endpointId` alone (see §3.2). The pair contract applies to `screen_zone_slot` only.
4. The physical-zone naming collision is out of this contract's scope: Blueprint floor-plan zones (Phase 1 §3.16) are a different entity that happens to share the word "zone." Every `zoneId` in this document is a screen-layout zone.

---

### 3.2 InventoryUnit — Digital Types

**Collection:** `inventoryUnits`
**Supersedes:** Phase 1 §3.3 digital variants (`screen_zone_slot`, `stream_slot`, `audio_slot`, `takeover_slot`). `physical_placement` is untouched.
**Purpose:** The atomic, searchable, bookable thing. Digital units are **derived, never hand-created** — the provisioning service (§4) is the only writer. The extensions below add the fields derivation needs: channel lineage, denormalized store context, the sellable flag, and provenance.

```ts
interface InventoryUnitBase {
  _id: string;
  retailerId: string;
  type: InventoryType;
  storeId: string;
  active: boolean;              // false = deactivated by lifecycle event (§4.4)
  tags: string[];               // LEGACY free-string tags; typed KVPs live in TagEntity (§3.5, §6)
  createdAt: Date;
  updatedAt: Date;
  deletedAt: Date | null;
}

/** Fields shared by all derived digital units. */
interface DigitalUnitFields {
  sellable: boolean;            // default TRUE under retailer-wide SSP (D3);
                                // kept in schema for future mixed estates
  storeTier: string | null;     // denormalized from Store at provisioning time
  provenance: {
    provisionedAt: Date;        // first materialization (backfill or event)
    lastSyncedAt: Date;         // last upsert by the provisioning service
    source: 'ssp_activation_backfill' | 'lifecycle_event' | 'manual_sync';
  };
}

interface ScreenZoneSlot extends InventoryUnitBase, DigitalUnitFields {
  type: 'screen_zone_slot';
  endpointId: string;           // Cue MediaPlayer id
  zoneId: string;               // Cue MediaPlayerZone id — stable (§3.1)
  channelId: string;            // denormalized: the channel assigning this zone
  layoutId: string;             // denormalized: the channel's layout
  zoneName: string;             // denormalized from the zone
  zoneWeight: number;           // [0, 1] share of screen real estate
  visibilityFactor: number;     // [0, 1]; Phase 1 §4.4 unchanged
}

interface StreamSlot extends InventoryUnitBase, DigitalUnitFields {
  type: 'stream_slot';
  endpointId: string;           // logical stream endpoint (MediaPlayerType → stream)
  appName: string;              // e.g. "digital_price_tag"
}

interface AudioSlot extends InventoryUnitBase, DigitalUnitFields {
  type: 'audio_slot';
  endpointId: string;           // store overhead audio system
}

interface TakeoverSlot extends InventoryUnitBase, DigitalUnitFields {
  type: 'takeover_slot';
  scope: 'all_stores_all_endpoints';  // network-wide; storeId = retailer sentinel
}

type DigitalInventoryUnit = ScreenZoneSlot | StreamSlot | AudioSlot | TakeoverSlot;
```

**Denormalization rules.** `channelId`, `layoutId`, `zoneName`, `zoneWeight`, `storeId`, `storeTier` are copies, refreshed by the provisioning service on every upsert (`lastSyncedAt` bumps). They exist so inventory search (§7) never joins into Cue. Cue remains the source of truth for all of them; a drift between copy and source is resolved by re-sync (§4.7), never by editing the unit directly.

**Indexes:**

- `{ retailerId: 1, type: 1, storeId: 1 }` — primary search scope
- `{ retailerId: 1, endpointId: 1, zoneId: 1 }` — **unique**, partial filter `{ type: 'screen_zone_slot' }`; the identity contract (§3.1) enforced at the storage layer
- `{ retailerId: 1, endpointId: 1 }` — unique, partial filter `{ type: { $in: ['stream_slot', 'audio_slot'] } }`
- `{ retailerId: 1, channelId: 1 }` — lifecycle fan-out (channel unassigned/layout changed → all affected units)
- `{ retailerId: 1, type: 1, sellable: 1, active: 1 }` — search pre-filter

**Validation:**

- `zoneWeight ∈ [0, 1]`; Σ `zoneWeight` across units sharing `(channelId, layoutId)` on one endpoint ≤ 1.0 (provisioning invariant, §4.6)
- `sellable` defaults to `true` when the retailer's SSP package is active; the flag is writable only via the sellable-toggle lifecycle event (§4.4), not general PATCH
- A `screen_zone_slot` may not be created without `channelId` — a zone with no channel assignment is not inventory
- **A digital unit must never be searchable without its TimeBudget.** Provisioning writes the TimeBudget in the same transaction as the unit (§4.2); search treats a missing TimeBudget as `active: false` and logs it (defensive; fixes the Phase 2 §3.5.1 null-deref risk)

---

### 3.3 TimeBudget — Time-Windowed SOV Ledger (supersedes Phase 1 §3.4, per D8)

**Collection:** `timeBudgets`
**Purpose:** The authoritative share-of-voice (SOV) ledger for one `(endpointId, zoneId)`. Phase 1's scalar `totalShareBooked` / `availableShare` fields are **removed** — a scalar cannot answer "share remaining Aug 1–31" and wrongly blocks non-overlapping bookings. Availability is a *function over a date interval*, computed from `bookings[]`. This document is what booking commits validate against transactionally; the calendar (§3.4) is only a read-optimized projection of it.

```ts
interface TimeBudget {
  _id: string;
  retailerId: string;
  endpointId: string;
  zoneId: string;
  storeId: string;                  // denormalized

  // Loop config — resolved at provisioning time (§3.6), denormalized here.
  // INVARIANT: identical across every TimeBudget on the same endpoint
  // (one loop clock per endpoint per store, D5 / Backend Confirmation #2).
  loopDuration: number;             // seconds; retailer default 120
  retailerReservedSeconds: number;  // default 30
  sellableSecondsPerLoop: number;   // = loopDuration - retailerReservedSeconds
  atomicUnit: 5;                    // immutable
  loopsPerDay: number;              // recomputed on takeover/hours changes (§5)

  bookings: TimeBudgetBooking[];    // the authoritative ledger

  version: number;                  // optimistic lock; every write increments;
                                    // mismatch on commit → 409 STALE_WRITE
  createdAt: Date;
  updatedAt: Date;
  deletedAt: Date | null;
}

interface TimeBudgetBooking {
  bookingId: string;                // stable id for release/move (post-v1) targeting
  campaignId: string;
  lineItemId: string;
  flightStart: string;              // ISO date (whole-day granularity, D8)
  flightEnd: string;                // ISO date, inclusive
  adDuration: number;               // seconds
  shareOfVoice: number;             // (0, 1]; CONSTANT for the whole flight (D8)
  playsPerDay: number;              // computed at booking time (Phase 1 §4.1 math)
  categoryExclusive: boolean;
  category: string | null;
  bookedAt: Date;
}
```

#### 3.3.1 Availability is a function: `availableShare(from, to)`

Because every booking holds a **constant share for its whole flight** (D8), the booked-share curve over time is a step function that only changes value at flight boundaries. Max concurrency over `[from, to]` therefore occurs at `from` or at some overlapping booking's `flightStart` — those are the only candidate points that need evaluating.

```
availableShare(tb: TimeBudget, from: Date, to: Date): number
  overlapping = tb.bookings where b.flightStart <= to AND b.flightEnd >= from
  if overlapping is empty: return 1.0

  candidatePoints = { from } ∪ { max(b.flightStart, from) for b in overlapping }

  maxBooked = 0
  for p in candidatePoints:
    bookedAtP = Σ b.shareOfVoice for b in overlapping
                 where b.flightStart <= p AND b.flightEnd >= p
    maxBooked = max(maxBooked, bookedAtP)

  return round4(1.0 - maxBooked)     // clamp to [0, 1]
```

This is a **pure domain function** (Phase 1 §2.1 conventions): no I/O, unit-tested in isolation, and reused by the booking engine, the calendar recompute job (§5), and any admin read path. Complexity is O(n²) in overlapping bookings per zone — n is small (bounded by the 100% cap over atomic 5% units); do not prematurely optimize.

#### 3.3.2 Interval-evaluated commit checks

The booking engine's two guards both evaluate **over the requested flight interval**, never against a scalar:

```
canBook(tb, req): Result
  // 1. 100%-cap check over the interval
  if availableShare(tb, req.flightStart, req.flightEnd) < req.shareOfVoice:
    return REJECT(409 OVERBOOKING,
      details: { requested: req.shareOfVoice,
                 available: availableShare(tb, req.flightStart, req.flightEnd) })

  // 2. Category exclusivity over the interval — two bookings conflict only
  //    when their flights actually overlap in time
  conflicts = tb.bookings where flightsOverlap(b, req)
                AND b.category == req.category
                AND (b.categoryExclusive OR req.categoryExclusive)
  if conflicts not empty:
    return REJECT(409 CATEGORY_EXCLUSIVITY_CONFLICT,
      details: { conflictingCampaignIds: conflicts.map(campaignId) })

  return OK
```

Commits run `canBook` inside a transaction that re-reads the TimeBudget, checks `version`, appends the booking, and increments `version`. A version mismatch is `409 STALE_WRITE` (Phase 3 §4.2 treatment). Search-time staleness (§3.4) can never double-sell because commits never read the calendar — the consistency rule is stated in full in §5.

**Indexes:**

- `{ retailerId: 1, endpointId: 1, zoneId: 1 }` — **unique**
- `{ 'bookings.campaignId': 1 }` — cancellation cascade
- `{ retailerId: 1, 'bookings.flightEnd': 1 }` — active-booking predicate scans (§3.7)

**Validation:**

- `sellableSecondsPerLoop === loopDuration - retailerReservedSeconds`
- `flightStart <= flightEnd` per booking; `shareOfVoice ∈ (0, 1]`, multiple of the atomic share step
- `availableShare(tb, s, e) >= 0` for every booking sub-interval (invariant: the ledger never encodes an overbook; enforce in the repository write helper, not just at API validation)
- `adDuration` a positive multiple of `atomicUnit`
- Loop fields writable only through the provisioning/config path (§3.6, §4) and only when the booking-protection lock (§3.7) permits

---

### 3.4 sovCalendars — Derived Availability View (new, per D9)

**Collection:** `sovCalendars`
**Purpose:** Precomputed day-granularity availability so inventory search (§7) is a pure read. **This collection is a derived view — never source of truth.** It is always rebuildable from `timeBudgets.bookings[]`; recompute reads the source and overwrites, making the job idempotent and self-healing. No write path anywhere in the system may treat a calendar value as authoritative — booking commits validate against the TimeBudget only (§3.3.2).

One document per `(endpointId, zoneId)` per calendar month. Day granularity suffices because bookings are constant % per whole-day flight (D8): the step function only changes at flight boundaries, and a day bucket captures it exactly.

```ts
interface SovCalendar {
  _id: string;
  retailerId: string;
  endpointId: string;
  zoneId: string;
  month: string;                    // "2026-08" (UTC calendar month)

  days: {
    // key "01".."31"; only days present in the month
    [day: string]: {
      bookedShare: number;          // max concurrent booked share that day, [0, 1]
      availableShare: number;       // = 1 - bookedShare
    };
  };

  loopsPerDay: number;              // denormalized from the TimeBudget at recompute;
                                    // lets search derive plays/guarantees/impressions
                                    // at read time without a second fetch
  version: number;                  // monotonic; recompute stamps the TimeBudget
                                    // version it was built from
  recomputedAt: Date;

  createdAt: Date;
  updatedAt: Date;
  deletedAt: Date | null;           // tombstoned when the unit is retired (§4.4)
}
```

**Write path:** exclusively the `sov-recalc` job on the Concourse queue (§5). Triggers, coalescing, retry, and the full-rebuild admin job are §5's contract. Provisioning initializes a unit's current-month-forward calendars at 100% available (§4.2).

**Read paths:** inventory search (§7) reads `days` buckets over the requested flight window and takes the min `availableShare`; the Brand Portal Calendar month-view heatmap and the Admin UI SOV ledger panel (§8) read the buckets directly. Plays / guaranteed plays / impressions per search row derive at read time from the bucket + `loopsPerDay` + rate card + traffic — only booked/available share is precomputed.

**Indexes:**

- `{ retailerId: 1, endpointId: 1, zoneId: 1, month: 1 }` — **unique**
- `{ retailerId: 1, month: 1 }` — retailer-wide month reads (heatmaps, funnel)

**Validation:**

- `availableShare === 1 - bookedShare` per bucket (±0.0001)
- `month` matches `^\d{4}-\d{2}$`; `days` keys valid for that month
- Staleness guard: search responses include `recomputedAt`; a calendar older than the configured staleness SLO (§5) is served but flagged in telemetry — never blocks the read

---

### 3.5 TagEntity / TagModel Extensions (per D4; full architecture in §6)

The platform's retailer-scoped typed tag system is the **single KVP schema** for this build — no third tag system. This subsection defines the schema-level deltas; taxonomy governance, migration of the legacy asset-tag endpoints, and consumer wiring are §6. Tag APIs extend the existing `/v1/retailers/tags/*` surface.

```ts
// Existing enum, extended. Values follow the established kebab-case convention.
enum TagModel {
  SITE            = 'site',
  PLAYLIST_CONFIG = 'playlist-config',
  MEDIA_PLAYER    = 'media-player',
  CHANNEL         = 'channel',
  ZONE            = 'zone',            // NEW — zone-local additive tags (D4)
  ASSET           = 'asset',           // NEW — unifies the legacy asset-tag system (§6)
}

// TagEntity is unchanged: retailer-scoped, typed key/value.
interface TagEntity {
  id: string;
  retailerId: string;
  key: string;                         // taxonomy-governed (§6)
  value: string;
  type: 'string' | 'number' | 'boolean' | 'enum';
  createdAt: Date;
  updatedAt: Date;
}

// Assignment shape — the existing AssignTags contract, now accepting the new models.
interface AssignTagDto {
  assignIds: string[];                 // target entity ids: zoneIds for model=zone,
                                       // asset ids for model=asset
  model: TagModel;
  value: string;                       // tag id being assigned
}
```

`MediaPlayerZoneEntity.tags` (bare `string[]`) is deprecated by this change; §6 defines its migration. The two malformed production assign calls (gap analysis §4.1) are fixed as part of §8's wiring pass.

#### 3.5.1 Effective-KVP computation (definition)

The effective KVP set of a zone — the thing search filters, the decide-time context bag, and activation-time asset routing all evaluate against — is defined once, in §6.5: the union of the site, endpoint, channel, and zone-local tag tiers plus entity-derived keys, with the most specific tier winning on key collision (zone > channel > endpoint > site).

Zone-local tags are *additive* — they exist to differentiate zones on one endpoint (canonical case: a GPU endpoint split into two zones, one tagged `brand_content = 'AMD'`, the other `brand_content = 'NVIDIA'`; same endpoint, different targetable inventory). Static keys the rule grammar assumes (`store_id`, `region`, `store_tier`, `zone_type`, `endpoint_type`, `screen_orientation`) must resolve for every provisioned unit — some derive from entities, some from tags; the resolution table is §6. Where the computation runs (materialized vs. resolved at read) is a §6/§7 decision; this definition is the contract either way.

---

### 3.6 Loop Configuration Placement (per D5)

**One loop clock per endpoint per store** (Backend Confirmation #2). `loopDuration` is an **endpoint-level** value; per-zone loop-duration overrides are dropped from the model entirely. Loop boundaries stay aligned to preserve top-of-the-hour takeovers; takeover impact is absorbed in the conservative guarantee buffer (source PRD §3.6 math, unchanged).

**Where config lives:**

```ts
// Retailer defaults — a block inside the existing SSP waterfall config document.
interface SspWaterfallConfig /* extended */ {
  // ...existing waterfall fields...
  loopDefaults: {
    loopDuration: number;             // default 120
    retailerReservedSeconds: number;  // default 30
    atomicUnit: 5;                    // immutable, network-wide
  };
  // Sparse per-endpoint overrides; absent = defaults apply.
  endpointLoopOverrides?: {
    [endpointId: string]: {
      loopDuration?: number;
      retailerReservedSeconds?: number;
    };
  };
}
```

**Resolution and denormalization:** at provisioning time (§4), the service resolves `override ?? retailerDefault` per endpoint and denormalizes the resolved values onto every TimeBudget for that endpoint's zones. Invariant: all TimeBudgets sharing an `endpointId` carry identical loop values.

**Change semantics (the rules that matter):**

1. **Retailer default changes never retroactively apply** to endpoints whose zones carry active or future bookings. The change takes effect for newly provisioned endpoints and for booking-free endpoints on next sync; booked endpoints keep their denormalized values.
2. **Per-endpoint override changes on a booked endpoint are refused** with `409 BOOKINGS_EXIST` (§3.7) — changing `loopDuration` or `retailerReservedSeconds` silently alters `loopsPerDay`, duration fits, and every booked campaign's plays/day and guarantees. Clear the bookings first (v1 resolution).
3. Any accepted loop change on a provisioned endpoint enqueues `sov-recalc` for all of its `(endpointId, zoneId)` units (§5) and re-runs guarantee validation (§4).

---

### 3.7 Booking-Protection Lock (data-layer rule)

Confirmed 2026-07-16: **any entity whose mutation would invalidate a booking is locked from edit and delete while it carries active or future bookings.** This is enforced at the API layer as a data-layer rule, uniformly, before any mutation-specific logic runs. §8 specifies the corresponding locked-state UI.

**The active-booking predicate:**

```
hasActiveBookings(scope): boolean
  // scope resolves to a set of (endpointId, zoneId) pairs — see table below
  return EXISTS booking in timeBudgets[scope].bookings
         where booking.flightEnd >= today          // UTC date, inclusive
// Past bookings (flightEnd < today) never lock anything.
```

**What locks, and what scope it resolves to:**

| Mutation attempted | Scope checked |
|---|---|
| Zone geometry edit / zone delete | that `(endpointId, zoneId)` for every endpoint carrying the channel |
| Layout swap or detach from a channel | every `(endpointId, zoneId)` under the channel |
| Channel unassignment from an endpoint | every `(endpointId, zoneId)` on that endpoint |
| Endpoint retirement / deletion | every `(endpointId, zoneId)` on that endpoint |
| Loop config change (endpoint override or applicable default) | every `(endpointId, zoneId)` on the affected endpoint(s) |
| `InventoryUnit` deactivate/delete via lifecycle event | that unit's pair |

**The error envelope** (Phase 1 §6.1 shape; new code `BOOKINGS_EXIST`):

```ts
{
  error: {
    code: 'BOOKINGS_EXIST',
    message: 'This <entity> carries active or future bookings and cannot be modified.',
    details: {
      entity: 'zone' | 'layout' | 'channel' | 'endpoint' | 'loop_config' | 'inventory_unit',
      entityId: string,
      blockingBookings: Array<{
        bookingId: string;
        campaignId: string;
        campaignName: string;        // denormalized for direct UI rendering
        lineItemId: string;
        endpointId: string;
        zoneId: string;
        shareOfVoice: number;
        flightStart: string;         // ISO date
        flightEnd: string;           // ISO date
      }>;
    };
    requestId: string;
  }
}
```

`blockingBookings` is capped at 50 entries with a `details.totalBlocking` count when truncated — the UI needs enough to render a resolution list, not the full estate.

**Resolution path:** v1 ships **clear-first** — release the blocking bookings (through the booking engine's release flow, which recomputes the ledger and enqueues `sov-recalc`), then retry the mutation. A **move/rebook flow** (migrate bookings to another zone, preserving flight and share) is explicitly post-v1; `bookingId` exists in the ledger now so that flow needs no schema change later.

`BOOKINGS_EXIST` is new. `OVERBOOKING` and `STALE_WRITE` are existing codes with existing UI treatments (Phase 3 §4.2) — this build adds emitters (§3.3.2), not new handling.

---

### 3.8 Required Tests (data layer)

Unit — pure domain functions:

1. `availableShare(from, to)`: empty ledger → 1.0; single booking inside window; booking partially overlapping window start/end; two non-overlapping bookings in the window (must NOT sum — returns 1 − max, proving the D8 fix); two overlapping bookings (must sum at the overlap); booking exactly at window boundary dates (inclusive `flightEnd`); result clamped and rounded to 4 dp.
2. `canBook`: overbook rejected over the interval with correct `details.requested/available`; non-overlapping same-zone bookings totaling > 100% accepted (scalar model would have wrongly rejected); category exclusivity rejects only when flights overlap AND either side is exclusive; conflicting campaign ids surfaced.
3. `hasActiveBookings`: booking ending today locks (inclusive); booking ending yesterday does not; scope expansion per §3.7 table (channel scope hits every carrying endpoint).
4. `effectiveKvps`: union across four tiers; zone > channel > endpoint > site on key collision; zone-local additive case (two zones, one endpoint, distinct `brand_content`).

Integration — schema + storage:

5. `(endpointId, zoneId)` unique index rejects duplicate `screen_zone_slot`; same `zoneId` on two different endpoints accepted (D2 cardinality).
6. TimeBudget optimistic lock: concurrent commit with stale `version` → `409 STALE_WRITE`; winner's booking persisted, `version` incremented once per write.
7. Booking commit transactionality: `canBook` + append + version bump atomic; induced mid-transaction failure leaves ledger unchanged.
8. sovCalendars rebuild idempotency: recompute twice from the same TimeBudget → identical `days`; hand-corrupt a bucket, recompute → self-heals; `availableShare === 1 - bookedShare` invariant on every bucket.
9. Calendar is never consulted at commit: force-stale a calendar to show availability, attempt an overbooking commit → `409 OVERBOOKING` from the TimeBudget check (proves the D9 consistency rule).
10. Loop config: default change skips booked endpoints and applies to unbooked ones on sync; override change on booked endpoint → `409 BOOKINGS_EXIST`; all TimeBudgets on one endpoint carry identical loop values after provisioning.
11. `BOOKINGS_EXIST` envelope: `details.blockingBookings` shape, 50-entry cap with `totalBlocking`, correct scope resolution for each mutation row in §3.7.
12. TagModel extensions: `AssignTags` with `model: 'zone'` and `model: 'asset'` round-trips through `/v1/retailers/tags/*`; existing four models unaffected.
13. Provisioning invariants (asserted here, exercised in §4's tests): unit never written without its TimeBudget; Σ `zoneWeight` ≤ 1.0 per (channel, layout, endpoint).

---

## 4. Digital Inventory Provisioning Service

**Module:** `workflows/provisioning/`
**Build item:** B1 (with the B1b calendar pipeline specified in §5)
**Source decisions:** D1 (channel-centric hierarchy), D2 (`(endpointId, zoneId)` identity), D3 (sync job + lifecycle events + sellable flag), D5 (endpoint-level loop clock), D7 (SSP activation = backfill trigger), D8 (time-windowed TimeBudget), plus Backend Confirmations #1 (zoneIds are stable for the life of a channel) and #2 (one loop clock per endpoint per store).
**Purpose:** The materialization bridge from Cue's structural chain (Site → Endpoint → Channel → Layout → Zones, per §2) to Deal Desk's sellable collections (`inventoryUnits`, `timeBudgets`, per §3). This service is the single writer of digital documents in those collections. Nothing else creates, deactivates, or re-keys a digital `InventoryUnit` — the booking engine mutates a TimeBudget's `bookings[]`, but the *existence* of every digital unit and its budget is owned here.

The provisioning service is a **derived-state materializer**: Cue remains the system of record for structure; Deal Desk's sellable collections are a projection of that structure. Every write this service performs must be reproducible from a full walk of the Cue chain (see §4.7). It never invents structure, never edits Cue entities, and — because of the booking-protection lock (§4.5) — never has to migrate a booked unit.

### 4.1 Position in the Architecture

```
Cue (system of record for structure)
  Site → Endpoint → Channel → Layout → Zones
        │
        │  lifecycle events (§4.4)  +  SSP-activation backfill (§4.3)
        ▼
workflows/provisioning/            ◄── the only writer of digital units
  ├── derivation.ts                # zone → InventoryUnit + TimeBudget upsert (§4.2)
  ├── backfill.ts                  # estate walk on SSP activation (§4.3)
  ├── lifecycle.ts                 # event handlers (§4.4)
  ├── sync.ts                      # full re-sync / drift repair (§4.7)
  └── invariants.ts                # §4.6 checks (pure functions)
        │
        ▼
inventoryUnits + timeBudgets (Deal Desk, per §3)
        │
        ├──► sov-recalc jobs on the Concourse queue → sovCalendars (§5)
        └──► inventory search reads (§7)
```

Two consumers depend on provisioning having run: the SOV availability calendar (§5) initializes only for units this service materializes, and inventory search (§7) returns only units whose invariants (§4.6) hold. The Admin UI's sellability funnel (§8) visualizes each stage of this pipeline.

### 4.2 Derivation Rule

**The rule, in one sentence:** for every **active endpoint** with an **assigned channel**, for every **zone** in that channel's **layout**, upsert one `InventoryUnit` and one `TimeBudget`, both keyed `(endpointId, zoneId)`.

Because one channel serves many endpoints (D2), a single zone definition fans out into one sellable unit *per endpoint carrying the channel*. A "Video MP" channel with a 3-zone layout assigned to 66 players materializes 198 units. zoneIds are stable for the life of a channel (Backend Confirmation #1), so `(endpointId, zoneId)` is a durable identity — every downstream document (TimeBudget, bookings, sovCalendars, rateCards) keys on it.

#### 4.2.1 Unit Type Mapping by MediaPlayerType

| `MediaPlayerType` | Unit derivation | `unitType` |
|---|---|---|
| Screen (display endpoint) | One unit per zone in the channel's layout | `screen_zone_slot` |
| Stream | One unit per zone (stream channels carry a single-zone layout; the derivation rule is unchanged) | `stream_slot` |
| Audio | One unit per zone (single-zone layout) | `audio_slot` |

The derivation loop is identical for all three types — stream and audio endpoints simply resolve to their slot type via `MediaPlayerType` instead of `screen_zone_slot`. No special-case code path: if a stream channel ever carries a multi-zone layout, the rule still holds.

#### 4.2.2 Loop Configuration (per D5)

`loopDuration` is **endpoint-level — one loop clock per endpoint per store**. There is no per-zone loop-duration override; the zone-level view of loop config is read-only (§8).

- On unit creation, the TimeBudget's loop config is snapshotted from the **retailer defaults in the SSP waterfall config** (`loopDuration`, `retailerReservedSeconds`, `atomicUnit`), applied at the endpoint level.
- **Retailer default changes never retroactively apply to endpoints with active bookings.** Changing the retailer default re-stamps loop config only on endpoints whose zones all carry zero active/future bookings; booked endpoints keep their snapshotted config until bookings are cleared (booking-protection lock, §4.5). Endpoints re-stamped by a default change enqueue `sov-recalc` for their units (§5) because `loopsPerDay` changed.

#### 4.2.3 Public API

```ts
interface ProvisionKey {
  endpointId: string;
  zoneId: string;
}

interface ProvisionResult {
  provisioned: ProvisionKey[];    // created or reactivated
  updated: ProvisionKey[];        // denormalized fields refreshed
  deactivated: ProvisionKey[];    // tombstoned (no active/future bookings)
  blocked: {                      // structural change collided with the lock
    key: ProvisionKey;
    code: 'BOOKINGS_EXIST';
    blockingBookings: { campaignId: string; lineItemId: string; flightStart: string; flightEnd: string }[];
  }[];
  invariantViolations: InvariantViolation[];   // §4.6 — logged, unit left unsearchable
}

export class ProvisioningWorkflow {
  /** Derive + upsert units for one endpoint (used by lifecycle events). */
  async provisionEndpoint(retailerId: string, endpointId: string): Promise<ProvisionResult>;

  /** Fan-out: derive + upsert units for every endpoint carrying a channel (channel/layout/zone events). */
  async provisionChannel(retailerId: string, channelId: string): Promise<ProvisionResult>;

  /** SSP-activation backfill — walks the whole estate (§4.3). */
  async backfillRetailer(retailerId: string, trigger: 'ssp_activation' | 'manual'): Promise<SyncRun>;

  /** Full re-sync / drift repair (§4.7). Same walk as backfill; diff semantics. */
  async syncRetailer(retailerId: string, opts?: { dryRun?: boolean }): Promise<SyncRun>;

  /** Deactivate units for a structural removal. Throws BookingsExistError if any unit is locked. */
  async deactivateUnits(retailerId: string, keys: ProvisionKey[], reason: DeactivationReason): Promise<ProvisionResult>;
}
```

#### 4.2.4 Derivation Algorithm

```
provisionEndpoint(retailerId, endpointId):
  endpoint = cue.getEndpoint(endpointId)
  if endpoint.status !== 'active' or endpoint.channel == null:
    return deactivateUnits(allUnitsFor(endpointId), reason: 'no_channel_or_inactive')

  channel = cue.getChannel(endpoint.channel)
  layout  = cue.getLayout(channel.layout)          // null → endpoint has no sellable zones yet
  zones   = layout ? cue.getZones(layout.id) : []

  assertInvariant_zoneWeightSum(zones)             // §4.6 I-1: Σ zoneWeight ≤ 1.0 — violation logs,
                                                   // marks affected units unsearchable, does not throw

  desired = zones.map(z => key(endpointId, z.id))
  actual  = repo.getActiveUnits({ endpointId })

  for zone in zones:
    unit = repo.upsertInventoryUnit({              // upsert on unique (endpointId, zoneId) — §4.6 I-2
      retailerId, endpointId, zoneId: zone.id,
      unitType: unitTypeFor(endpoint.mediaPlayerType),    // §4.2.1
      channelId: channel.id, layoutId: layout.id,
      zoneName: zone.name, zoneWeight: zone.weight,
      // denormalized store context (refreshed on every provision pass):
      siteId, storeName, storeTier, region,
      sellable: true,                              // D3: default sellable=true on SSP retailers;
                                                   // flag kept in schema for future mixed estates
      status: 'active'
    })
    tb = repo.upsertTimeBudget({                   // §4.6 I-3: TimeBudget before searchable
      retailerId, endpointId, zoneId: zone.id,
      loopConfig: endpointLoopConfig(endpoint),    // §4.2.2 — endpoint-level clock
      bookings: preserveExisting()                 // upsert NEVER touches bookings[]
    })
    if unit.wasCreated or unit.wasReactivated:
      enqueue('sov-recalc', { keys: [key], reason: 'unit_provisioned' })   // calendar init at 100% — §5

  stranded = actual − desired                      // zones no longer in the layout
  deactivateUnits(stranded, reason: 'zone_removed')   // lock-checked — §4.5

  emit telemetry per §4.9
```

**Upsert semantics.** Re-provisioning an existing `(endpointId, zoneId)` refreshes denormalized fields (`zoneName`, `zoneWeight`, store context, `channelId`/`layoutId`) and reactivates a tombstoned unit; it **never** resets the TimeBudget's `bookings[]`, never regenerates identity, and never re-initializes an existing calendar. Running the derivation twice is a no-op the second time (§4.7).

### 4.3 SSP-Activation Backfill Job

**Trigger:** the **retailer-wide SSP switch** (D7). SSP purchase flips the entire estate — no mixed estates in v1 — and activation is the backfill trigger. This is the job that turns "854 stores / 66 players / 0 sellable units" into real numbers.

The backfill does three things, in order, per zone:

1. **Materializes** `InventoryUnit` + `TimeBudget` for every active endpoint-with-channel across the whole estate (the §4.2 derivation, estate-wide).
2. **Registers the P4 filler pool:** each zone's existing playlist schedules are registered as that zone's P4 filler pool. Playlists stop being the primary content layer and become the waterfall's fallback — they are **not deleted**. The filler pool guarantees **no zone can go dark**: whenever no campaign wins a loop slot, the zone's former playlist content plays. The retailer's content investment is preserved by construction.

   **Retailer default filler (fallback for playlist-less zones):** a zone with no playlist schedules at activation registers an **empty pool** and falls back to the **retailer default filler** — the retailer-level P4 configuration already defined in the SSP waterfall config (`fallbackChain.p4FillerPoolMode: 'all_retailer_content' | 'specific_playlist'` + `p4FillerPlaylistId`, Phase 4 §5.1). The waterfall's P4 resolution order is therefore: **zone filler pool → retailer default filler**. A retailer with neither configured surfaces as a warning in the sellability funnel (§8) — the only configuration under which a zone could go dark, and it is made visible before it can happen.
3. **Initializes availability at 100%:** enqueues a `sov-recalc` job on the Concourse queue per provisioned unit; the recalc pipeline (§5) writes the initial `sovCalendars` buckets at `availableShare = 1.0`.

#### 4.3.1 Algorithm

```
backfillRetailer(retailerId, trigger):
  run = createSyncRun({ retailerId, trigger, status: 'running' })   // §4.7.2

  sites = cue.getSites(retailerId)
  for site in sites:                                   // batched: 50 endpoints per batch,
    for endpoint in cue.getEndpoints(site.id):         // checkpoint after each batch (resumable)
      if endpoint.status !== 'active': run.skipped++; continue
      if endpoint.channel == null:    run.noChannel++; continue    // surfaces in funnel — §8

      result = provisionEndpoint(retailerId, endpoint.id)          // §4.2.4
      run.accumulate(result)

      for zone in zonesOf(endpoint):                   // P4 filler registration — idempotent
        schedules = cue.getZoneSchedules(zone.id)      // the zone's existing playlist schedules
        registerFillerPool(retailerId, endpoint.id, zone.id, {
          source: 'legacy_playlists',
          scheduleIds: schedules.map(s => s.id)
        })
        emit 'inventory.filler_pool_registered'

  enqueue('sov-recalc', coalescedKeys(run.provisioned), reason: 'backfill')   // §5 batching rules
  run.status = 'completed'; run.completedAt = now
  emit 'provisioning.backfill_completed'
```

#### 4.3.2 Backfill Semantics

| Property | Behavior |
|---|---|
| Idempotency | Re-running the backfill upserts — existing units refresh, no duplicates (unique index, §4.6 I-2), existing filler registrations and calendars are untouched. Safe to re-trigger at any time. |
| Resumability | Progress checkpointed per endpoint batch in the `SyncRun` record; a crashed run resumes from the last checkpoint rather than restarting the walk. |
| Concurrency | One backfill/sync run per retailer at a time — a second trigger while `status: 'running'` returns the in-flight run (`202`, §4.8.1). |
| Duration | Estate walk is O(endpoints). Target: 1,000 endpoints × 3 zones provisioned in < 5 minutes. The Concourse queue absorbs the calendar-init fan-out — backfill completion does not wait on recalc completion. |
| Partial estates | Endpoints without a channel are counted (`noChannel`), skipped, and surfaced in the sellability funnel (§8) — they are the retailer's to-do list, not an error. |
| Bookings | A backfill can never collide with the booking-protection lock — it only creates/refreshes, never deactivates structure. Deactivation happens only via lifecycle events (§4.4) and sync-diff (§4.7), both lock-checked. |

### 4.4 Lifecycle Events (Incremental Sync)

After backfill, provisioning stays in sync via lifecycle events emitted by the Cue admin surface (the wired chain UI, §8). Every event handler is a thin wrapper over the §4.2 derivation plus the lock check (§4.5).

**Fan-out rule:** channel-, layout-, and zone-level events multiply across every endpoint carrying the channel (D2). A zone edit on a channel assigned to 66 endpoints touches 66 units.

| # | Event | Provisioning action | Calendar action (§5) | Lock interaction (§4.5) |
|---|---|---|---|---|
| E1 | **Channel assigned to endpoint** | `provisionEndpoint`: upsert one unit + TimeBudget per zone in the channel's layout | Enqueue `sov-recalc` per new key → initialize at 100% | None — creation only |
| E2 | **Channel unassigned from endpoint** | Deactivate all `(endpointId, *)` units for that channel's zones; tombstone (soft, `status: 'retired'`) | Tombstone calendars for affected keys | **Blocked** (`409 BOOKINGS_EXIST`) if any affected unit carries an active/future booking |
| E3 | **Layout attached to channel** (first layout) | `provisionChannel`: fan-out E1 derivation to every carrying endpoint | Initialize at 100% per new key | None — creation only |
| E4 | **Layout changed on channel** (swap) | Diff old zones vs. new zones per carrying endpoint: new zones provision; removed zones deactivate. zoneIds are stable (Confirmation #1), so surviving zones keep identity and bookings | New keys initialize at 100%; removed keys tombstone | **Blocked** if any removed zone's unit carries an active/future booking on any carrying endpoint |
| E5 | **Zone added to layout** | Provision the new `(endpointId, zoneId)` on every carrying endpoint; re-check I-1 (Σ zoneWeight) | Initialize at 100% per key | None — creation only. I-1 violation marks the layout's units unsearchable until weights are fixed |
| E6 | **Zone edited** (name, weight, geometry, zone-local tags) | Refresh denormalized fields on every carrying endpoint's unit. Tag edits route through §6 (no unit write). Weight change re-checks I-1 | Weight/geometry edits: no calendar impact (SOV is share-based). No recalc | **Geometry and weight edits blocked** while any carrying endpoint's unit is booked; name and tag edits are never blocked |
| E7 | **Zone removed from layout** | Deactivate `(endpointId, zoneId)` on every carrying endpoint; tombstone | Tombstone calendars | **Blocked** if any carrying endpoint's unit carries an active/future booking |
| E8 | **Endpoint retired/deleted** | Deactivate all units for the endpoint | Tombstone calendars for all endpoint keys | **Blocked** if any of the endpoint's units carries an active/future booking |
| E9 | **Sellable flag toggled** (unit or channel scope) | Set `sellable` on the unit(s). Unit remains provisioned; `sellable: false` removes it from search results (§7) only | No calendar change — bookings and availability persist across toggles | Toggling to `false` with active bookings is **allowed** (existing bookings deliver; unit just stops being newly bookable) |
| E10 | **Retailer loop-config default changed** | Re-stamp loop config on endpoints with zero active/future bookings only (§4.2.2) | Enqueue `sov-recalc` for re-stamped endpoints' keys (`loopsPerDay` changed) | Booked endpoints keep snapshotted config — never re-stamped |

**Tombstoning.** Deactivation is always soft: `status: 'retired'`, `retiredAt`, `retiredReason` on the unit; the TimeBudget and its (necessarily past-only) bookings are retained for reporting/proof-of-play joins; the calendar is tombstoned per §5. Reactivation (e.g., channel re-assigned) flips the same document back to `active` — identity is never re-minted, per Confirmation #1.

**Delivery.** Events ride the same platform event bus as Phase 2 (§2.3 conventions there apply: at-least-once delivery, handlers idempotent — which the §4.2 upsert guarantees). Missed or dropped events are healed by the full re-sync (§4.7); the sync is the safety net, events are the fast path.

### 4.5 Interaction with the Booking-Protection Lock

The booking-protection lock is defined once, platform-wide: **entities carrying active/future bookings (any booking with `flightEnd >= today`) are locked from edit and delete.** Past bookings never lock. v1 resolution is **clear-first** — release the bookings, then perform the structural change; a move/rebook flow is post-v1.

**Enforcement point: the Cue structural-mutation API layer, before the mutation lands** — not inside the provisioning service. The consequence is the design guarantee this section depends on:

> **The provisioning service never has to migrate booked units.** By the time a structural change (zone delete, layout swap, channel unassignment, endpoint retirement, geometry/weight edit, loop-config change) reaches a provisioning lifecycle handler, the lock has already proven that no affected unit carries an active or future booking. Provisioning therefore has exactly two write shapes — upsert and tombstone — and zero migration logic.

```
assertNoActiveBookings(keys: ProvisionKey[]):
  blocking = timeBudgets.aggregate(
    match:  { key in keys },
    unwind: bookings,
    match:  { bookings.flightEnd >= startOfToday() },
    project: { key, campaignId, lineItemId, flightStart, flightEnd }
  )
  if blocking.length > 0:
    throw BookingsExistError({
      status: 409,
      code: 'BOOKINGS_EXIST',
      details: { blockingBookings: blocking }    // UI renders locked state + resolution path — §8
    })
```

| Contract point | Specification |
|---|---|
| Error shape | `409` with the Phase 1 §6.1 error envelope; `code: 'BOOKINGS_EXIST'`; `details.blockingBookings[]` lists `{ campaignId, lineItemId, flightStart, flightEnd, endpointId, zoneId }` so the UI can render the locked state with the blocking campaigns and a clear-bookings resolution path (§8). |
| Scope of the check | The **full fan-out set**: a channel-level mutation checks every `(endpointId, zoneId)` across every carrying endpoint. One booked unit on one endpoint locks the channel-level structural change for all. |
| Race window | The lock check and the structural mutation execute in the same transaction as the Cue write (or, where Cue writes are not co-transactional, the provisioning handler re-runs `assertNoActiveBookings` before tombstoning and aborts with the same 409 — the belt to the API layer's suspenders). |
| Not locked | Creation-only events (E1/E3/E5), name/tag edits (E6 partial), sellable toggles (E9), and rate-card/traffic attachment are never blocked. |
| Related codes | `BOOKINGS_EXIST` is new (this PRD). `OVERBOOKING` and `STALE_WRITE` are existing codes with existing UI treatments (Phase 3 §4.2); they belong to the booking commit path (§5), not to provisioning. |

### 4.6 Invariants

Checked in `workflows/provisioning/invariants.ts` (pure functions), enforced at the points listed. A violated invariant never silently drops data — it logs, emits telemetry, and marks affected units unsearchable until repaired.

| # | Invariant | Enforcement | On violation |
|---|---|---|---|
| I-1 | **Σ `zoneWeight` ≤ 1.0 per layout** | Checked on every derivation pass and on zone add/edit (E5/E6); also validated at the Cue zone-editor API boundary | Units of the offending layout set `searchable: false`; `provisioning.invariant_violated` telemetry; funnel (§8) surfaces the layout |
| I-2 | **`(endpointId, zoneId)` uniqueness** | Unique compound Mongo index on `inventoryUnits` and on `timeBudgets`; all writes are upserts against that key | Duplicate write is structurally impossible; an index-violation error is a bug, alerting immediately |
| I-3 | **TimeBudget must exist before a unit is searchable** | Derivation writes the TimeBudget in the same pass as the unit; search (§7) additionally inner-joins on TimeBudget existence | A unit without a TimeBudget is invisible to search (fixes the gap analysis §4.2 null-deref risk); sync repair (§4.7) recreates it |
| I-4 | **Calendar exists for every searchable unit** | `sov-recalc` enqueued on every provision; search reads the calendar (§5) | Missing calendar → unit excluded from results until recalc lands; drift detected by sync |
| I-5 | **A provisioned unit's structural fields match Cue** | Full re-sync diff (§4.7) | Drift counted, repaired by re-derivation, reported in `SyncRun.drift` |

### 4.7 Idempotency & Full Re-Sync

Every provisioning write path is idempotent by construction: derivation is a pure function of the Cue chain, and writes are keyed upserts. This yields the operational property that **the entire digital inventory estate is rebuildable from a single command** — provisioning state is derived, never precious. (The same property holds one layer down for calendars, §5.)

#### 4.7.1 Re-Sync Semantics

`syncRetailer` runs the identical estate walk as the backfill (§4.3.1) and then a **diff phase**:

```
syncRetailer(retailerId, opts):
  desired = walkCueChain(retailerId)                       // set of ProvisionKey + derived fields
  actual  = repo.getActiveUnits({ retailerId })

  toCreate    = desired − actual                           // upsert (provision)
  toRefresh   = desired ∩ actual where fieldsDiffer        // upsert (drift repair, I-5)
  toTombstone = actual − desired                           // orphans: structure gone from Cue

  if opts.dryRun: return report(toCreate, toRefresh, toTombstone)   // no writes

  provision(toCreate ∪ toRefresh)                          // §4.2.4
  for key in toTombstone:
    if hasActiveBookings(key):                             // lock check — §4.5
      report as blocked (BOOKINGS_EXIST) — never auto-release a booking
    else:
      tombstone(key)
```

**Orphans with bookings are reported, never force-tombstoned.** If Cue structure vanished out-of-band (a missed lock, a direct DB edit), the sync surfaces the conflict in the `SyncRun` report and the funnel (§8) for human resolution — automated booking release is out of scope for v1, consistent with clear-first.

`sov-recalc` is enqueued for created/reactivated/tombstoned keys only; unchanged units generate no queue traffic.

#### 4.7.2 `SyncRun` Record

One document per backfill/sync execution (stored in `provisioningSyncRuns`), and the payload behind the status route (§4.8.2):

```ts
interface SyncRun {
  id: string;
  retailerId: string;
  trigger: 'ssp_activation' | 'manual' | 'scheduled';
  status: 'running' | 'completed' | 'failed';
  dryRun: boolean;
  startedAt: string;
  completedAt: string | null;
  checkpoint: { siteId: string; endpointBatch: number } | null;   // resumability — §4.3.2
  counts: {
    sitesWalked: number;
    endpointsWalked: number;
    endpointsSkippedInactive: number;
    endpointsWithoutChannel: number;      // funnel input — §8
    unitsProvisioned: number;             // created or reactivated
    unitsRefreshed: number;               // drift repairs
    unitsTombstoned: number;
    fillerPoolsRegistered: number;
    blocked: number;                      // BOOKINGS_EXIST collisions (sync-diff only)
    invariantViolations: number;
  };
  blockedDetails: { endpointId: string; zoneId: string; campaignIds: string[] }[];
  error: string | null;
}
```

### 4.8 API Routes

All routes are retailer-scoped (Cognito JWT + tenancy per Phase 1 §2.4). The sync trigger (§4.8.1) is Cerbos-gated to the retailer admin role; the reads (§4.8.2–§4.8.3) are available to any retailer role with inventory read access.

#### 4.8.1 `POST /v2/retailers/:retailerId/inventory/provisioning/sync`

Manual trigger for the backfill/full re-sync. The SSP-activation flow calls the same workflow internally (`trigger: 'ssp_activation'`); this route exists for repair, re-runs, and pre-activation dry runs.

```ts
interface ProvisioningSyncRequest {
  dryRun?: boolean;        // default false — dry run walks + diffs, writes nothing
}

// 202 Accepted (async job pattern, Phase 4 §2.3)
interface ProvisioningSyncResponse {
  syncRunId: string;
  status: 'running';
  statusUrl: string;       // → §4.8.2
}
```

| Condition | Response |
|---|---|
| Sync already running for this retailer | `202` with the in-flight `syncRunId` (idempotent trigger — no second run starts) |
| Retailer has no SSP package active and `dryRun` is false | `409 PRECONDITION_FAILED` — provisioning writes only exist for SSP retailers (D7); dry run is allowed pre-activation to preview the estate |

#### 4.8.2 `GET /v2/retailers/:retailerId/inventory/provisioning/status`

Returns the latest `SyncRun` (§4.7.2) plus current estate rollups — the data source for the sellability funnel (§8):

```ts
interface ProvisioningStatusResponse {
  latestRun: SyncRun | null;
  estate: {
    activeUnits: number;
    sellableUnits: number;         // active ∧ sellable ∧ invariants hold (I-1..I-4)
    unsearchableUnits: number;     // invariant violations — with per-invariant breakdown
    endpointsWithoutChannel: number;
    lastEventProcessedAt: string | null;   // lifecycle-sync freshness
  };
}
```

#### 4.8.3 `GET /v2/retailers/inventory/:endpointId/:zoneId`

The **per-unit read** — the single source for every surface that renders one sellable unit's full state: the SSP-mode zone panel's SOV ledger (§8.2.3), the zone tag editor's inherited-KVP chips (§8.3), and the sellability funnel's drill-down (§8.4). No consumer assembles this from separate list queries, and no separate bookings or effective-KVP endpoint exists.

```ts
interface InventoryUnitDetailResponse {
  unit: InventoryUnit;                    // §3.2 — includes sellable flag, provenance, loop-config snapshot
  bookings: TimeBudgetBooking[];          // active + future only (flightEnd >= today); ?includePast=true for history
  locked: boolean;                        // booking-protection state (§3.7); true when any active/future booking exists
  effectiveKvps: {                        // §6.5 — computed server-side, never client-side
    key: string;
    value: unknown;
    source: 'zone' | 'channel' | 'endpoint' | 'site' | 'derived';
    shadowed?: boolean;                   // true on an inherited entry overridden by a more specific tier
  }[];
  fillerPool: { source: 'legacy_playlists'; scheduleIds: string[] } | null;   // §4.3; null → retailer default filler applies
}
```

Generated hook: `cqQueryInventoryUnitControllerFindOneV2`. Returns `404` for a never-provisioned `(endpointId, zoneId)`; returns the tombstoned unit with `unit.active: false` for retired units (consumers render the retired state, not a 404). Calendar day-buckets are **not** embedded here — they come from the calendar read (§5.7); the two reads compose in the zone panel.

### 4.9 Telemetry & Observability

Events use `entity.action` form (Phase 3 §4.5 convention):

| Event | Fired when | Key properties |
|---|---|---|
| `inventory.unit_provisioned` | Unit created or reactivated | `endpointId`, `zoneId`, `unitType`, `trigger` (event name / backfill / sync) |
| `inventory.unit_deactivated` | Unit tombstoned | `endpointId`, `zoneId`, `reason` |
| `inventory.filler_pool_registered` | Zone's playlists registered as P4 filler (§4.3) | `endpointId`, `zoneId`, `scheduleCount` |
| `provisioning.sync_started` / `provisioning.sync_completed` / `provisioning.sync_failed` | SyncRun lifecycle | `syncRunId`, `trigger`, `dryRun`, full `counts` on completion |
| `provisioning.backfill_completed` | SSP-activation backfill finishes | `retailerId`, `counts` — the "854 stores → N units" moment |
| `provisioning.mutation_blocked` | A structural change hit the lock | `endpointId`, `zoneId`, `code: 'BOOKINGS_EXIST'`, `blockingCampaignCount` |
| `provisioning.invariant_violated` | Any I-1..I-5 violation | `invariant`, `layoutId`/`endpointId`/`zoneId` |

Operational metrics (platform observability stack):

| Metric | Type | Alert |
|---|---|---|
| `provisioning.sync.duration_ms` | histogram, per run | > 10 min for < 5,000-endpoint estates |
| `provisioning.units.active` / `.sellable` gauge per retailer | gauge | `sellable == 0` on an SSP-active retailer with > 0 endpoints-with-channel — the exact failure mode that triggered this PRD |
| `provisioning.event_lag_ms` | histogram (event emitted → handler completed) | p99 > 60s |
| `provisioning.drift.count` | gauge, from latest sync diff | > 0 sustained across two scheduled syncs |
| `provisioning.blocked.count` | counter | Informational — expected during clear-first workflows |

### 4.10 Required Tests

**Derivation (§4.2)**

1. Active endpoint + channel + 3-zone layout → exactly 3 `InventoryUnit` + 3 `TimeBudget` documents, keyed `(endpointId, zoneId)`, `unitType: 'screen_zone_slot'`, loop config snapshotted from retailer defaults at endpoint level.
2. One channel assigned to 2 endpoints → 2 units per zone (fan-out), distinct `endpointId`, identical `zoneId` — D2 identity holds.
3. Stream and audio endpoints derive `stream_slot` / `audio_slot` via `MediaPlayerType`; derivation loop unchanged.
4. Re-running derivation on an unchanged endpoint → zero writes beyond `updatedAt`; `bookings[]` untouched; no duplicate `sov-recalc` enqueued (idempotency).
5. Endpoint with channel but no layout → zero units, zero errors; endpoint counted for the funnel.
6. Retailer loop-config default change → unbooked endpoints re-stamped + `sov-recalc` enqueued; endpoint with one active booking keeps snapshotted config (E10).

**Backfill (§4.3)**

7. **Activate SSP on a seeded Cue estate (M sites, N endpoints-with-channel, Z zones each) → exactly N×Z units materialize**, every unit has a TimeBudget, `sov-recalc` enqueued per unit, calendars initialize at 100% (asserted via §5 pipeline), `provisioning.backfill_completed` fires with matching counts.
8. Every zone with pre-existing playlist schedules has a registered P4 filler pool referencing those schedule IDs; zones with no playlists register an empty pool without error.
9. Kill the backfill mid-run → re-trigger resumes from checkpoint; final counts equal an uninterrupted run; no duplicate units.
10. Re-run backfill on an already-backfilled estate → all upserts, zero new documents, filler pools and calendars untouched.
11. Second sync trigger while one is running → `202` returns the in-flight `syncRunId`; only one run executes.

**Lifecycle events (§4.4)**

12. **Unassign a channel from an endpoint with no bookings → that endpoint's units deactivate** (`status: 'retired'`), calendars tombstone, other endpoints carrying the channel are untouched.
13. Zone added to a live channel's layout → new unit provisions on every carrying endpoint; calendar initializes at 100%.
14. Layout swap where zoneIds persist → surviving zones keep unit identity and (past) bookings; removed zones tombstone; added zones provision.
15. Zone weight edit pushing Σ zoneWeight > 1.0 → I-1 violation: layout's units become unsearchable, telemetry fires, search (§7) excludes them.
16. Sellable toggled off on a unit with an active booking → allowed; unit vanishes from search; booking and calendar unaffected; toggle back on restores searchability.
17. Endpoint retired with only past bookings (`flightEnd < today`) → deactivation proceeds; past bookings never lock.

**Booking-protection lock (§4.5)**

18. **Attempt zone delete while any carrying endpoint's unit has an active booking → `409 BOOKINGS_EXIST`** with `details.blockingBookings` listing campaign, line item, flight, and unit key; zone, units, TimeBudgets, and calendars all unchanged.
19. Channel-level unassignment where 1 of 66 endpoints carries a booked unit → entire operation blocked with the one blocking unit identified (full fan-out check).
20. Booking with `flightEnd = today` locks; `flightEnd = yesterday` does not (boundary).
21. Clear-first flow: release the blocking booking, retry the same structural mutation → succeeds.

**Re-sync & invariants (§4.6–§4.7)**

22. Manually corrupt a unit's denormalized `zoneName` → sync detects drift (I-5), repairs it, `SyncRun.counts.unitsRefreshed = 1`.
23. Delete a TimeBudget out-of-band → unit excluded from search (I-3); sync recreates the TimeBudget with empty `bookings[]`.
24. Cue zone deleted out-of-band while its unit carries an active booking → sync reports the orphan as blocked, does **not** tombstone, does **not** release the booking.
25. `dryRun: true` → full diff report, zero writes, zero queue jobs.
26. Duplicate provision race (two concurrent handlers, same key) → unique index (I-2) forces single document; second write degrades to upsert-refresh.

---

## 5. SOV Availability Calendar & Recalculation Pipeline

### 5.1 Purpose & Position in the Architecture

Per D9, inventory availability is **precomputed, not computed at search time**. The `sovCalendars` collection (schema in §3) is a materialized, per-unit, day-granularity view of booked vs. available share of voice (SOV). Inventory search (§7) is a **pure read** of this view: it never walks `timeBudgets.bookings` across candidate units, never fans out per-zone availability math at query time, and never blocks on recomputation. A search over 854 stores touches only indexed calendar documents.

The calendar is a **derived view, never a source of truth**. It is always rebuildable from the authoritative `timeBudgets.bookings[]` (§3, D8). Anything that can write a booking-affecting change enqueues a recalculation; the recompute reads the source and overwrites the derived view.

Two properties keep this design honest:

1. **Correctness does not depend on the calendar.** Booking commits validate transactionally against `timeBudgets.bookings` — see the consistency rule in §5.2. Calendar staleness degrades search freshness, never booking integrity.
2. **The pipeline is self-healing.** Recompute is a full overwrite from source (§5.5), so a lost event, a crashed worker, or a bug in an earlier recompute is repaired by the next recompute or by the full-rebuild job (§5.6). There are no incremental deltas to drift.

Day granularity is sufficient because bookings are constant % per whole-day flights (D8): booked share is a **step function that only changes value at flight boundaries**. Dayparting is a runtime-targeting concern, not a booking concern, and never appears in this pipeline.

The same day buckets feed three consumers:

| Consumer | Access path | Section |
|---|---|---|
| Inventory search (Campaign Builder Step 2) | Server-side read during `POST /v2/retailers/:retailerId/inventory/search` | §7 |
| Zone calendar view / Brand Portal Calendar-tab heatmap | `GET /v2/retailers/inventory/:endpointId/:zoneId/calendar?from=&to=` (§5.7) | §7, §8 |
| SSP-mode zone panel (SOV ledger, booked vs. available for a date range) | Same calendar read API | §8 |

### 5.2 The Consistency Rule (Non-Negotiable Contract)

> **⚠️ CONSISTENCY RULE — this is a contract, not a guideline. Any implementation that violates either half is wrong, regardless of tests passing.**
>
> 1. **Searches read `sovCalendars`. Only searches and display surfaces read `sovCalendars`.**
> 2. **Booking commits NEVER read the calendar.** A commit validates against the authoritative `timeBudgets.bookings[]` **transactionally, under the optimistic version lock** on the TimeBudget document (§3): re-read the document, evaluate the 100%-cap and category-exclusivity checks over the booking's flight interval against `bookings[]`, and write the new booking with a version-guarded update. A concurrent write in the gap fails the version guard and surfaces as `409 STALE_WRITE`; an interval that no longer fits surfaces as `409 OVERBOOKING`. Both use the existing Phase 3 §4.2 error treatments — no new UX is introduced.
>
> **Consequence:** staleness between a booking-affecting event and its recompute **cannot double-sell inventory**. The worst case is cosmetic — search shows share that is no longer available (or hides share that has been freed) for the seconds until `sov-recalc` lands. The user who acts on a stale search result hits the `OVERBOOKING` treatment at commit, which is exactly the drift path Phase 3 §4.2 already specifies for the search→commit gap. Do not "fix" a stale-search bug by making the commit path read the calendar, and do not "optimize" the commit path by trusting a fresh-looking calendar. The calendar has no role in the transaction.

Error codes on the commit path (all pre-existing semantics):

| Code | HTTP | Meaning here |
|---|---|---|
| `OVERBOOKING` | 409 | Requested share does not fit within 100% − max concurrent booked share over the flight interval, evaluated against `timeBudgets.bookings[]` at commit time. `details.requested`, `details.available`. |
| `STALE_WRITE` | 409 | Optimistic version guard failed — another commit landed between read and write. Client refetches and retries per Phase 3 §4.2. |
| `BOOKINGS_EXIST` | 409 | Not a commit error — the booking-protection lock (§3, §4) rejecting a structural mutation on a unit carrying active/future bookings. Listed here because lock enforcement reads the same authoritative `bookings[]`, never the calendar. |

### 5.3 The `sov-recalc` Job (Concourse Queue)

All recalculation runs as job type **`sov-recalc`** on **the Concourse queue**. Nothing recomputes inline in a request path.

**Payload:**

```ts
interface SovRecalcPayload {
  retailerId: string;

  // Exactly one of the two targeting forms:
  unitKeys?: Array<{ endpointId: string; zoneId: string }>;  // explicit units
  campaignId?: string;                                        // expand to every unit the campaign books

  // Which months to recompute. Omitted ⇒ derive from the affected
  // bookings' flight ranges (min flightStart .. max flightEnd), clamped
  // to [currentMonth .. currentMonth + horizonMonths].
  months?: string[];        // e.g. ['2026-08', '2026-09']

  reason: SovRecalcReason;  // trigger matrix row, for metrics/tracing (§5.4)
  enqueuedAt: string;       // ISO 8601
}

type SovRecalcReason =
  | 'booking_created' | 'booking_changed' | 'booking_released'
  | 'flight_dates_changed' | 'loop_config_changed'
  | 'takeover_booked' | 'takeover_released'
  | 'unit_provisioned' | 'unit_retired'
  | 'rebuild';
```

`campaignId` expansion happens in the worker, not the producer: the worker resolves the campaign's line items → per-zone bookings → distinct `(endpointId, zoneId)` keys. This keeps producers (booking engine, campaign lifecycle) free of fan-out logic and means an expansion always sees the campaign's *current* bookings.

**Coalescing:** duplicate work units are merged, not queued twice. The dedupe key is `(retailerId, endpointId, zoneId, month)`. If a `sov-recalc` job for a key is already pending (queued, not yet started), enqueueing the same key is a no-op. A key currently *executing* is re-enqueued (the running recompute may have read `bookings[]` before the new change landed). Rapid-fire changes to one zone — e.g., a planner adjusting share sliders — therefore collapse to at most two recomputes: the running one and one pending.

**Retry:** exponential backoff — 1s, 4s, 16s, 64s, then park in the dead-letter set with an alert (`sov_recalc.dead_lettered` metric, §5.9). A dead-lettered key is repaired by the next natural trigger on that unit or by the full-rebuild job (§5.6); it never blocks bookings (§5.2).

**Idempotency (the core guarantee):** the recompute for a `(unit, month)` **reads the authoritative `timeBudgets.bookings[]` and overwrites the calendar document wholesale**. It never applies incremental deltas (`bookedShare += x`), never reads the previous calendar values as input, and never depends on event ordering or exactly-once delivery. Running the same job zero-extra, once, or five times converges on the same document. This is what makes the pipeline self-healing: at-least-once delivery from Concourse is sufficient, and any corruption is one recompute away from correct.

**Concurrency:** per-key serialization — at most one executing recompute per `(retailerId, endpointId, zoneId)` at a time (Concourse partition key). Distinct units recompute in parallel up to the worker pool size.

### 5.4 Trigger Matrix

Every producer below enqueues `sov-recalc` **after** its own transaction commits (post-commit hook / outbox — never inside the transaction, so a queue outage cannot fail a booking).

| # | Trigger | Producer | Payload targeting | Fan-out size | Notes |
|---|---|---|---|---|---|
| 1 | Booking created | Booking engine (Phase 2), on successful commit | `unitKeys` = the booked unit(s) | 1–n zones in the line item | Includes bookings created via Brand Portal booking-request approval. |
| 2 | Booking changed (share % or per-booking flight edit) | Booking engine | `unitKeys` = affected unit(s) | small | Months derived from the union of old and new flight ranges. |
| 3 | Booking released (cancel, campaign cancellation, clear-first flow of the booking-protection lock) | Booking engine / campaign lifecycle | `unitKeys` or `campaignId` | small–medium | The clear-first resolution path (§4, §8) releases then recomputes — the locked entity becomes editable only after the release commit, not after the recompute. |
| 4 | Campaign flight-date change | Campaign lifecycle (Phase 2) | `campaignId` (worker expands) | every unit the campaign books | Months = union of old and new flight ranges. |
| 5 | Loop-config change (`loopDuration`, `retailerReservedSeconds` on an endpoint) | Endpoint config API | `unitKeys` = every zone on the endpoint | zones-per-endpoint | Changes `loopsPerDay` / sellable seconds, which the calendar denormalizes. Permitted only when the endpoint carries no active/future bookings (booking-protection lock, §4) — so in practice this recomputes empty or past-only calendars. Retailer-level default changes never retroactively apply to endpoints with active bookings and therefore trigger nothing for them. |
| 6 | **Takeover booked / released** | Booking engine | `unitKeys` = **every zone at every affected store** | **the large fan-out** — potentially thousands of units | MUST be batched: the producer chunks unit keys into batches of `SOV_RECALC_BATCH_SIZE` (default 200 units/job, §5.8) and enqueues one job per chunk. Coalescing still applies per key. |
| 7 | Unit provisioned | Provisioning service (§4), on upsert of a new `(endpointId, zoneId)` | `unitKeys` = the new unit(s) | 1–n | Initializes the calendar at 100% available across the horizon. SSP-activation backfill (§4) provisions in bulk and enqueues in the same batched form as row 6. |
| 8 | Unit retired | Provisioning service (§4) | `unitKeys` | small | Recompute tombstones the calendar (`status: 'retired'`, §5.5) so search excludes it without a join against `inventoryUnits`. |

No other writer may touch `sovCalendars`. In particular: the search path (§7), the calendar read API (§5.7), and the admin UI (§8) are read-only against this collection.

### 5.5 Recompute Algorithm

Booked share per unit is a **step function over time whose breakpoints are flight boundaries**. The recompute evaluates that step function once per breakpoint interval, then projects it onto day buckets grouped by month — it does not loop day-by-day over bookings.

Inputs (all read fresh at execution time — never from the payload, never from the old calendar):

- `timeBudget` for `(endpointId, zoneId)` — authoritative `bookings[]`, each `{ campaignId, lineItemId, share, flightStart, flightEnd, priority, status }`; loop config denormalized fields.
- `inventoryUnit` for `(endpointId, zoneId)` — `status` (active/retired), `sellable` flag.
- Endpoint-level loop config — `loopDuration`, `retailerReservedSeconds` (D5: one clock per endpoint; retailer defaults resolved at provisioning, §4).

```
sovRecalc.execute(retailerId, endpointId, zoneId, months):
  unit       = inventoryUnits.findOne({ retailerId, endpointId, zoneId })
  timeBudget = timeBudgets.findOne({ retailerId, endpointId, zoneId })

  if unit == null or unit.status == 'retired':
    // Tombstone: overwrite every requested month as retired, 0 available.
    for month in months: upsertCalendar(month, { status: 'retired', days: {} })
    return

  if timeBudget == null:
    // Invariant violation (§4: TimeBudget must exist before a unit is searchable).
    emit metric sov_recalc.missing_time_budget; mark calendar status 'blocked'; return

  active = timeBudget.bookings.filter(b => b.status in ('confirmed', 'active'))
           // draft/proposed bookings do not consume SOV; released/expired are excluded

  // 1. Step function: breakpoints are flight boundaries.
  //    flightEnd is inclusive (whole-day flights, D8), so the step drops
  //    the day AFTER flightEnd.
  breakpoints = sortedUnique(
      active.flatMap(b => [b.flightStart, dayAfter(b.flightEnd)]))

  // 2. Evaluate booked share once per interval between breakpoints.
  //    bookedShare(interval) = Σ share of bookings whose flight covers the interval.
  //    (Sum is correct — the commit-time cap check (§5.2) guarantees the sum of
  //    concurrent confirmed shares never exceeds 1.0.)
  intervals = []   // [{ from, toExclusive, bookedShare }]
  for each consecutive pair (t1, t2) in breakpoints:
    covering = active.filter(b => b.flightStart <= t1 && dayAfter(b.flightEnd) >= t2)
    intervals.push({ from: t1, toExclusive: t2,
                     bookedShare: sum(covering.map(b => b.share)) })
  // Days outside every interval have bookedShare = 0.

  // 3. Project onto day buckets, grouped by month; build full replacement docs.
  loopsPerDay = computeLoopsPerDay(endpoint.loopDuration)       // e.g. 86400 / 120 = 720
  for month in months:
    days = {}
    for day in daysOf(month):
      booked = stepValueAt(intervals, day)                       // 0 if uncovered
      days[day] = { bookedShare: booked, availableShare: round4(1.0 - booked) }

    sovCalendars.replaceOne(
      { retailerId, endpointId, zoneId, month },
      { retailerId, endpointId, zoneId, month, days,
        loopsPerDay,
        sellableSecondsPerLoop: endpoint.loopDuration - endpoint.retailerReservedSeconds,
        status: unit.sellable ? 'active' : 'unsellable',
        version: previous.version + 1, recomputedAt: now() },
      { upsert: true })

  emit telemetry 'sov_calendar.recomputed' { endpointId, zoneId, months, reason }
```

Rules the implementation must honor:

- **Shares are decimals in [0, 1]** (Phase 1 §2.2 convention). `availableShare` is clamped to `[0, 1]` after rounding; a transiently over-committed source (should be impossible per §5.2, but the recompute must not trust it) clamps to 0 and emits `sov_recalc.overcommit_detected` rather than writing a negative.
- **Whole-document replace, never `$set` on individual days.** Partial day updates are the incremental-delta anti-pattern §5.3 forbids.
- **Horizon:** default recompute horizon is `currentMonth` through `currentMonth + 18` months (`SOV_CALENDAR_HORIZON_MONTHS`, retailer-configurable in SSP waterfall config). Bookings beyond the horizon are recomputed when the horizon rolls forward (monthly cron enqueues `reason: 'rebuild'` for the newly in-horizon month across all units).
- **Past months are immutable:** months strictly before `currentMonth` are skipped (proof-of-play, not the calendar, is the record of what actually delivered).
- **Takeovers** appear in the calendar only through their booked share like any other booking. Takeover *impact on guarantees* is read-time math (§5.8) using the existing Phase 1 takeover-impact utility — it is not baked into the buckets.

### 5.6 Full-Rebuild Admin Job

**Purpose:** (a) **backfill** — populate calendars for the entire estate when SSP activation materializes units (§4), and for horizon roll-forward; (b) **repair** — converge the derived view after dead-lettered jobs, worker crashes mid-fan-out, schema migrations, or any suspected drift.

**Invocation:**

- Automatically by the SSP-activation backfill (§4) after unit/TimeBudget materialization completes.
- Manually via `POST /v2/retailers/:retailerId/inventory/provisioning/sync` with `{ "rebuildCalendars": true }` (the same admin trigger route defined in §4; scope may be narrowed with optional `endpointIds[]`).
- Monthly horizon-roll cron (§5.5).

**Behavior:**

```
fullRebuild.run(retailerId, scope?):
  units = inventoryUnits.find({ retailerId, ...scopeFilter })   // includes retired (to tombstone)
  chunks = chunk(units, SOV_RECALC_BATCH_SIZE)                  // default 200
  for chunk in chunks:
    enqueue('sov-recalc', { retailerId, unitKeys: chunk.keys(),
                            months: fullHorizon(), reason: 'rebuild' })
  // Sweep: any sovCalendars doc whose (endpointId, zoneId) has no
  // corresponding inventoryUnit is tombstoned (orphan cleanup).
```

The rebuild is **just the normal recompute at estate scale** — same job type, same idempotent overwrite, same coalescing. It requires no lock and no downtime: because commits never read the calendar (§5.2), a rebuild running during business hours cannot corrupt a booking; searches served mid-rebuild are at worst as stale as they were before the rebuild started.

Progress is observable via `GET /v2/retailers/:retailerId/inventory/provisioning/status` (§4), which includes `calendarRebuild: { state, unitsTotal, unitsRecomputed, startedAt, finishedAt }`.

### 5.7 Calendar Read API

```
GET /v2/retailers/inventory/:endpointId/:zoneId/calendar?from=YYYY-MM-DD&to=YYYY-MM-DD
```

Read-only projection of the unit's calendar over `[from, to]` (max range 18 months; `from` defaults to today, `to` to `from` + 3 months). Response:

```ts
interface SovCalendarResponse {
  endpointId: string;
  zoneId: string;
  status: 'active' | 'unsellable' | 'retired' | 'blocked';
  loopsPerDay: number;
  sellableSecondsPerLoop: number;
  days: Array<{
    date: string;             // YYYY-MM-DD
    bookedShare: number;      // [0,1]
    availableShare: number;   // [0,1]
  }>;
  recomputedAt: string;       // oldest recomputedAt among months spanned — staleness signal
}
```

Consumers: the SSP-mode zone panel's SOV ledger and date-range availability (§8), the sellability funnel drill-down (§8), and the Brand Portal Calendar-tab month-view heatmap (Phase 4 Brand Portal, Browse Inventory) — all render directly from `days[]` with no additional math for the share display. Play/impression enrichment, where a surface needs it, follows §5.8.

### 5.8 Read-Time Math Boundary

**Only booked/available share is precomputed.** Everything a search row or calendar surface shows beyond share is derived **per row, at read time**, from cheap in-process math:

| Value | Derivation (at read) | Source of factors |
|---|---|---|
| Plays/day at share *s* | `floor(loopsPerDay × s)` | `loopsPerDay` from the calendar doc |
| Guaranteed plays over flight | conservative-guarantee utility (Phase 1 §4) over the flight's day buckets, incl. takeover impact | calendar buckets + guarantee buffer config |
| Impressions | plays × per-type impression formula × store traffic | rate card + `storeTraffic` |
| Rate / cost | rate card resolution at the requested share and duration | `rateCards` |

Rationale: these values depend on **request context** (ad duration, candidate share level, flight window) that cannot be precomputed without a combinatorial calendar, and they reuse the Phase 1 pure-function utilities — keeping the math single-source with the booking engine and killing the FE-hardcoded guarantee/impression constants (§7). The FE receives all of these server-computed in the search response (§7) and never re-derives them.

The boundary is strict in both directions: do **not** move plays/impressions into the calendar buckets (bloats recompute and stales on every rate-card/traffic edit), and do **not** move share math out to read time (that reintroduces the query-time fan-out D9 exists to eliminate).

### 5.9 Performance Targets, Metrics & Telemetry

| Surface | Target |
|---|---|
| `sov-recalc` single-unit recompute (full 18-month horizon) | p95 < 250ms |
| Event → calendar updated (single-unit trigger, healthy queue) | p95 < 5s |
| Takeover fan-out (1,000 units, batched at `SOV_RECALC_BATCH_SIZE` = 200) | complete < 60s |
| Full estate rebuild (10,000 units) | complete < 15 min, zero impact on commit latency |
| Calendar read (`GET .../calendar`, 3-month window) | p99 < 100ms |
| Search read of calendar buckets (per §7 search, 500 candidate units) | adds p99 < 150ms to the search budget |

**Operational metrics** (gauges/counters, Concourse + service): `sov_recalc.queue_depth`, `sov_recalc.jobs_completed`, `sov_recalc.jobs_coalesced`, `sov_recalc.retries`, `sov_recalc.dead_lettered` (alert > 0), `sov_recalc.recompute_duration_ms`, `sov_recalc.staleness_seconds` (enqueuedAt → recomputedAt), `sov_recalc.overcommit_detected` (alert > 0 — indicates a §5.2 violation upstream), `sov_recalc.missing_time_budget` (alert > 0 — §4 invariant breach).

**Telemetry events** (`entity.action` form, Phase 3 §4.5 convention):

```
sov_calendar.recomputed          { endpointId, zoneId, months, reason, durationMs }
sov_calendar.rebuild_started     { retailerId, unitsTotal, trigger }
sov_calendar.rebuild_completed   { retailerId, unitsRecomputed, durationMs }
sov_calendar.read                { endpointId, zoneId, rangeDays, surface }
booking.commit_conflict          { code: 'OVERBOOKING' | 'STALE_WRITE', endpointId, zoneId, requestedShare, availableShare }
```

`booking.commit_conflict` volume is the health signal for the whole design: a sustained rise means calendar staleness is leaking into user-visible commit failures — investigate queue depth before touching the contract in §5.2.

### 5.10 Required Tests

**Unit — recompute algorithm (§5.5):**

1. Zero bookings → every day `availableShare = 1.0`.
2. One booking at 60%, Aug 5–20 → buckets show 0.60 booked inside the flight (inclusive both ends), 0 outside; step drops on Aug 21.
3. Overlapping bookings 60% + 30% (overlapping flights) → 0.90 booked only on the overlap days; correct steps at all four boundaries.
4. Flight spanning a month boundary → both month documents correct; no gap or double-count at the seam.
5. Draft/proposed and released bookings excluded from booked share.
6. Retired unit → tombstoned calendar (`status: 'retired'`); missing TimeBudget → `blocked` + metric, no throw (guards defect §4-risk: no null-deref).
7. Over-committed source data (bookings summing > 1.0 injected directly) → clamps to 0 available, emits `overcommit_detected`, never writes negative share.
8. Idempotency: running the identical job 3× yields byte-identical `days` and monotonically increasing `version`; recompute output independent of prior calendar contents (corrupt the calendar doc, recompute, verify repaired).

**Integration — pipeline & consistency rule:**

9. **Two bookings on non-overlapping flights, each at 60% on the same unit, both commit successfully** (D8: windowed availability — the scalar model would wrongly block the second); calendar shows 0.60 in each window, 1.0 between them.
10. **Concurrent commits racing for the last 40% on the same unit and overlapping window → exactly one succeeds; the other receives `409 OVERBOOKING` (or `409 STALE_WRITE` on the version guard) — never both succeed, never a negative availability.** Assert the calendar converges to the winner's state after recompute.
11. Booking commit succeeds while the queue is **paused** (stale calendar) — proves commits don't read the calendar; search then shows stale availability; a commit attempted from that stale result gets `409 OVERBOOKING` with Phase 3 §4.2 payload shape (`details.requested`, `details.available`).
12. Trigger matrix coverage: each row in §5.4 fires exactly the expected unit keys and months (booking create/change/release; campaign flight-date change expands via `campaignId`; loop-config change on an unbooked endpoint; unit provision initializes at 100%; unit retire tombstones).
13. Takeover booked at a store with N endpoints × M zones → all N×M unit keys enqueued in batches of ≤ `SOV_RECALC_BATCH_SIZE`; duplicate keys within the burst coalesce (assert `jobs_coalesced` > 0 when the same takeover is edited twice quickly).
14. **Kill the queue worker mid-fan-out (takeover across 1,000 units, worker killed at ~50%) → run the full-rebuild job → every unit's calendar matches a from-scratch recompute of its `timeBudgets.bookings[]`.** Also assert the orphan sweep removes calendar docs for units deleted during the outage.
15. Retry/backoff: a recompute failing transiently (injected DB error) retries on the 1s/4s/16s/64s schedule and succeeds; a permanently failing key dead-letters and alerts, while bookings on that unit continue to commit normally.
16. Enqueue is post-commit: force the queue producer to throw → the booking transaction still commits and the booking is durable; the calendar repairs on the next trigger or rebuild.
17. Calendar read API: range clamping, defaults, 18-month cap, `recomputedAt` reflects the oldest spanned month, retired unit returns `status: 'retired'` with empty enrichment.
18. Read-time math boundary: search response plays/guarantees/impressions change when rate card or traffic changes **without** any recompute having run (proves they are not baked into buckets); share values do **not** change until a booking event triggers recompute.

---

## 6. Unified KVP Tag Architecture

Tags are the connective tissue of this build: they drive inventory search filtering (§7), decide-time targeting evaluation, the KVP rule builder (§8), and creative-to-zone routing at activation (§9). This section makes `TagEntity` the single tag schema for the entire platform, extends it to the two missing tiers (`ZONE`, `ASSET`), defines the inheritance model that produces each zone's effective KVP set, and pins the static KVP contract the rule grammar depends on.

### 6.1 The Problem: Two Disjoint Tag Schemas (and a Third Waiting to Happen)

Today the platform carries two unrelated tag systems:

| System | Shape | Covers | Assign / lookup |
|---|---|---|---|
| **`TagEntity`** (retailer-scoped, typed) | `{ key, value, type }` with a `TagModel` discriminator | Sites, media players (endpoints), channels, playlist configs | `AssignTags` (`AssignTagDto { assignIds, model, value }`), `LookupTags` reverse search |
| **Playlist-asset tags** (separate endpoints) | Untyped key/value pairs via `tag-keys`, `tag-keys/{key}/values`, `{id}/tags` (`useAssetTags` on the FE) | Playlist assets only | Its own assign surface; no reverse lookup compatible with `LookupTags` |

Two additional gaps compound this:

1. **`TagModel` stops at channel.** There is no `ZONE` member, and `MediaPlayerZoneEntity.tags` is a bare `string[]` — untyped, unscoped, invisible to `LookupTags`. Zone-level targeting keys the rule grammar already assumes (`zone_type`, zone-differentiating brand tags) have no home.
2. **Deal Desk's KVP layer is connected to neither.** The rule grammar and the Campaign Builder's rule builder were specified against an abstract KVP taxonomy; the FE ships a hardcoded `KVP_KEYS` array with no link to what retailers have actually tagged.

The inventory provisioning work needs tags at every tier (site, endpoint, channel, zone) **and** on creative assets (for routing, §9). Building a third schema for that — or extending the asset-tag system sideways — would leave three disjoint systems where a campaign's targeting rules, a zone's identity, and an asset's routing metadata each speak a different dialect.

**Decision (B3, locked 2026-07-16): `TagEntity` is the single tag architecture.** Everything else migrates onto it or is adapted into it. No new tag schema is introduced by this build.

### 6.2 TagEntity as the Single Schema

**Purpose:** one retailer-scoped, typed, taxonomized key/value tag system serving all five tiers: site, endpoint, channel, zone, asset.

**Shape** (existing entity, extended — canonical storage per §3):

```ts
enum TagModel {
  SITE = 'site',                       // existing
  MEDIA_PLAYER = 'media-player',       // existing (endpoint tier)
  CHANNEL = 'channel',                 // existing
  PLAYLIST_CONFIG = 'playlist-config', // existing
  ZONE = 'zone',                       // NEW — B3
  ASSET = 'asset',                     // NEW — B3 (absorbs playlist-asset tags)
}

interface TagEntity {
  id: string;
  retailerId: string;          // all tags are retailer-scoped
  key: string;                 // taxonomy key, e.g. 'brand_content'
  value: string;               // e.g. 'AMD'
  type: TagValueType;          // 'string' | 'number' | 'boolean' | 'enum'
  createdAt: string;
  updatedAt: string;
  deletedAt: string | null;
}

interface TagAssignment {
  tagId: string;
  model: TagModel;             // which tier the target lives in
  targetId: string;            // siteId | endpointId | channelId | zoneId | assetId
  retailerId: string;
  assignedAt: string;
}

// Existing DTO — unchanged shape; ZONE and ASSET become legal `model` values
interface AssignTagDto {
  assignIds: string[];         // target entity ids
  model: TagModel;
  value: string;               // tag id (or key:value per current backend semantics — confirm against SDK 5.11)
}
```

**Invariants:**

- A tag assignment's `model` must match the actual entity type of every id in `assignIds`. The backend rejects mismatches with `400` (this is exactly the class of bug in §6.10).
- `(retailerId, key, value)` is unique per tag document; assignment is many-to-many.
- `MediaPlayerZoneEntity.tags: string[]` is **deprecated as a source of truth**. During migration it may be dual-written as a denormalized cache of the zone's tag values; the reverse index (`LookupTags`) reads only `TagAssignment`.
- No tier gets a bespoke schema. If a future tier needs tags (e.g., campaign-level labels), it gets a new `TagModel` member, not a new system.

### 6.3 Asset-Tag Migration: Adapter + Deprecation Window

Playlist-asset tags move onto `TagEntity` under `TagModel.ASSET`. Because production asset-tag data and call sites exist, migration is a two-phase adapter, not a cutover:

**Phase A — Adapter (ships with B3):**

1. One-time backfill job: read every existing asset tag (`tag-keys`, `tag-keys/{key}/values`, per-asset `{id}/tags`), upsert equivalent `TagEntity` docs (`type` inferred; defaults to `'string'`) and `TagAssignment` rows with `model: ASSET`. Idempotent — keyed on `(retailerId, key, value, assetId)`.
2. The legacy asset-tag endpoints stay up but become a **thin adapter** over the unified store: reads translate `TagEntity`/`TagAssignment` back into the legacy response shape; writes write through to the unified store only. There is no dual source of truth after backfill — legacy endpoints are views.
3. Legacy responses gain a `Deprecation` header and a `Sunset` date; every hit fires `tag.legacy_asset_api.called` (§6.9) so remaining call sites are enumerable from telemetry, not guesswork.

**Phase B — Deprecation window (one release cycle minimum):**

4. FE call sites (`useAssetTags` and friends) are rewritten against `/v1/retailers/tags/*` with `model=asset`.
5. When telemetry shows zero legacy traffic for 14 consecutive days, the legacy routes are removed. Removal is a deliberate release note, not a silent delete.

The legacy Program/ProgramInventory tag usage is **not** migrated — that system is deprecated wholesale (B7; §10 sequencing).

### 6.4 Taxonomy Governance

Free-form keys make the rule builder, search filters, and routing joins unreliable. B3 introduces a governed, retailer-scoped taxonomy over the existing tag store.

**Shape:**

```ts
interface TagTaxonomyKey {
  id: string;
  retailerId: string;
  key: string;                        // canonical snake_case, e.g. 'brand_content'
  label: string;                      // display name for pickers
  valueType: 'string' | 'number' | 'boolean' | 'enum';
  allowedValues?: string[];           // required when valueType === 'enum'
  applicableModels: TagModel[];       // which tiers may carry this key
  origin: 'system' | 'retailer';     // system keys are the static contract (§6.6) — not deletable
  createdAt: string;
  updatedAt: string;
  deletedAt: string | null;
}
```

**Governance rules:**

| Concern | Rule |
|---|---|
| Scope | Taxonomy is per retailer. No cross-retailer key sharing in v1. |
| Who administers | Retailer admins (and Conqrse platform admins) via the Tag Manager (§8). Cerbos-gated to the retailer-admin role; brand users never see taxonomy administration. |
| Key creation | Assigning a tag with an unknown key is rejected (`400 UNKNOWN_TAG_KEY`) unless the caller has taxonomy-admin rights and passes `createKey: true`. No silent key proliferation. |
| Value validation | `enum` keys reject values outside `allowedValues`; `number`/`boolean` keys validate coercion at assign time. |
| System keys | The static-contract keys (§6.6) are seeded per retailer with `origin: 'system'` at SSP activation (§4 backfill). They cannot be deleted or retyped; retailers may extend `allowedValues` where marked extensible. |
| Deletion | Deleting a taxonomy key requires zero live assignments (or an explicit cascade with confirmation in the Tag Manager). Soft-delete per platform convention. |

### 6.5 Inheritance + Zone-Local Additive Tags (Effective KVP Computation)

Per D4, a zone's targetable identity is the union of every tier above it plus its own local tags:

```
effectiveKvps(zone, endpoint) =
    tags(site of endpoint)
  ∪ tags(endpoint)
  ∪ tags(channel assigned to endpoint)
  ∪ tags(zone)                      // zone-local, additive
  ∪ entityDerivedKvps(...)          // §6.6 — computed, not stored as tags
```

**Collision rule:** most specific tier wins — `zone > channel > endpoint > site`. Collisions are per **key**: a zone-local `region` would shadow the site's `region` for that zone only. Entity-derived keys (§6.6) are computed last and cannot be shadowed by tags — `store_id` always means the actual store.

**Behavior:**

```
computeEffectiveKvps(endpointId, zoneId):
  site     = siteOf(endpointId)
  channel  = channelOf(endpointId)          // per D1/D2: endpoint → channel → layout → zones
  kvps = {}
  for tier in [site, endpoint, channel, zone]:        // ascending specificity
    for (key, value) in tagsOf(tier):
      kvps[key] = value                                // later tier overwrites = most-specific wins
  kvps = merge(kvps, entityDerivedKvps(endpointId, zoneId))  // derived keys always win
  assertStaticContractResolved(kvps)                   // §6.6 — provisioning invariant
  return kvps
```

The computed set is denormalized onto the provisioned `InventoryUnit` (field defined in §3) so search (§7) filters without a five-way join. The Digital Inventory Provisioning Service (§4) recomputes and rewrites the denormalized set whenever a tag lifecycle event lands on any tier in the zone's chain (tag assigned/unassigned/edited on the site, endpoint, channel, or zone). Tag mutations are **not** covered by the booking-protection lock — they change targeting metadata, never booked SOV — and therefore never enqueue `sov-recalc`; they only refresh the unit's effective KVP set and the search index.

**Canonical example — the GPU endpoint (D4):**

One endpoint in the electronics department runs a two-zone layout: the left zone merchandises AMD, the right zone NVIDIA. Same site, same endpoint, same channel — the zones are the only differentiator:

| Tier | Tags |
|---|---|
| Site `store-042` | `region = 'northeast'`, `store_tier = 'flagship'` |
| Endpoint `ep-gpu-01` | `department = 'electronics'` |
| Channel `ch-gpu-wall` | `content_program = 'gpu-wall'` |
| Zone `z-left` (zone-local) | `brand_content = 'AMD'` |
| Zone `z-right` (zone-local) | `brand_content = 'NVIDIA'` |

Effective KVPs for `(ep-gpu-01, z-left)` include `brand_content = 'AMD'`; for `(ep-gpu-01, z-right)`, `brand_content = 'NVIDIA'`. A campaign rule `brand_content = 'NVIDIA'` matches exactly one of the two sellable units on that endpoint — one endpoint, two independently targetable, independently bookable inventory units. This is the load-bearing case for `TagModel.ZONE`: without zone-local tags these two units are indistinguishable to search, booking, and routing.

### 6.6 The Static KVP Contract

The rule grammar (source PRD) already assumes these keys exist on every unit. Every provisioned `(endpointId, zoneId)` unit **must resolve all six** — this is a provisioning invariant enforced by §4 (units failing it are flagged in the sellability funnel, §8, rather than silently searchable with holes).

| Key | Source | Derivation |
|---|---|---|
| `store_id` | **Entity-derived** | `endpoint.siteId` — never a tag; cannot be shadowed |
| `region` | **Tag** (site tier) | Seeded system taxonomy key; retailer assigns per site |
| `store_tier` | **Entity-derived, tag fallback** | From the site/store entity's tier field where populated; else site-tier tag |
| `zone_type` | **Entity-derived** | `MediaPlayerZoneEntity.type` (`standard` \| `take-over`) |
| `endpoint_type` | **Entity-derived** | `MediaPlayerType` (video / stream / audio slot mapping per §4) |
| `screen_orientation` | **Tag** (endpoint tier) | Seeded system taxonomy key (`enum: landscape | portrait`); assigned per endpoint |

Entity-derived keys are computed by `entityDerivedKvps()` at provisioning/recompute time and injected into the effective set (§6.5); they are not stored as `TagEntity` rows. Tag-sourced keys are ordinary taxonomy keys with `origin: 'system'`.

**Naming collision note (gap analysis §3):** `zone_type` refers to the *screen-layout* zone (`standard`/`take-over`). The physical Blueprint floor-plan "zone" is a different entity; any key referring to it (e.g., `product_category_in_zone`) must be defined against the physical zone the endpoint is pinned in, and is out of scope for the static contract in v1. See Glossary (§11).

### 6.7 Consumers of the Unified Tag System

| Consumer | How it reads tags | Spec |
|---|---|---|
| **(a) Inventory search filtering** | `kvpRules` in the v2 search request evaluate against each unit's denormalized effective KVP set, layered on top of the site scope. | §7 |
| **(b) Decide-time KVP context bag** | The waterfall's `/v2/ssp/decide` slot context carries the zone's effective KVPs so P1/P2 targeting rules and Phase 4 rule-triggered creative evaluate against the same values search matched on. Same computation, same denormalized source — search-time and decide-time targeting cannot drift. | §9 |
| **(c) KVP rule-builder pickers** | The Campaign Builder's rule builder replaces the hardcoded `KVP_KEYS` array with a live taxonomy lookup: key picker = `GET /v1/retailers/tags/taxonomy` (filtered to `applicableModels` relevant to inventory tiers); value picker = `allowedValues` for enum keys, distinct-value lookup otherwise. Retailers can only build rules against keys that actually exist in their estate. | §8 |
| **(d) Activation asset routing** | Creative assets carry `ASSET`-tier tags in the **same schema** as zone tags. Routing at activation is a join — `assetTags ⋈ zoneEffectiveKvps` on matching key/value — not a translation between two tag dialects. The GPU example completes here: the AMD creative (`brand_content = 'AMD'` asset tag) routes to the AMD zone and only that zone. | §9 |

### 6.8 API Additions

All routes extend the existing `/v1/retailers/tags/*` surface. No new tag namespace.

| Method & Route | Purpose | Notes |
|---|---|---|
| `POST /v1/retailers/tags/assign` | Existing `AssignTags` | `model` now accepts `zone` and `asset`. Backend validates `model` matches target entity type (`400 TAG_MODEL_MISMATCH`). |
| `POST /v1/retailers/tags/lookup` | Existing `LookupTags` reverse search | Extended to index `ZONE` and `ASSET` assignments. |
| `GET /v1/retailers/tags` | List tags | New filters: `model`, `key`. |
| `GET /v1/retailers/tags/taxonomy` | List taxonomy keys | Filters: `model` (applicability), `origin`. Powers rule-builder pickers (§6.7c). |
| `POST /v1/retailers/tags/taxonomy` | Create taxonomy key | Taxonomy-admin gated (§6.4). |
| `PATCH /v1/retailers/tags/taxonomy/:keyId` | Edit label / extend `allowedValues` | System keys: `allowedValues` extension only where marked extensible. |
| `DELETE /v1/retailers/tags/taxonomy/:keyId` | Soft-delete key | Rejected with `409` + live-assignment count unless cascade confirmed. |
| `GET /v1/retailers/tags/keys/:key/values` | Distinct values in use for a key | Value-picker source for non-enum keys. |
| *(legacy)* `GET/POST .../tag-keys*`, `.../{id}/tags` | Asset-tag adapter | Reads/writes translated onto the unified store; `Deprecation` + `Sunset` headers; removed per §6.3 Phase B. |

**Validation summary:** unknown key → `400 UNKNOWN_TAG_KEY`; enum value out of range → `400 INVALID_TAG_VALUE`; model/entity mismatch → `400 TAG_MODEL_MISMATCH`; all writes retailer-scoped by auth middleware.

**Effective-KVP reads:** there is no standalone effective-KVP route on the tag surface. The computed set (§6.5) is denormalized onto the `InventoryUnit` and served by the per-unit read `GET /v2/retailers/inventory/:endpointId/:zoneId` (§4.8.3), whose `effectiveKvps[]` entries carry per-key `source` tier and `shadowed` flags.

### 6.9 Production Defects to Fix (Gap Analysis §4.1)

Two wired production tag-assign call sites are malformed (flagged PLAUSIBLE from client-side evidence; confirm against backend behavior before filing, then fix in the B2 wiring pass, §8):

1. **`MediaPlayerDetailClient.tsx:285-287` (master)** — sends `model: 'MediaPlayer'` where the `TagModel` enum value is `'media-player'`, cast through `as any`. Fix: use the enum member; remove the cast. The new `400 TAG_MODEL_MISMATCH` validation (§6.8) turns this class of bug into a loud failure instead of a silent no-op.
2. **`MediaPlayerChannelDetailClient.tsx:673-676` (master)** — calls `AssignTags` with the **channel id in the tag-id path slot** and a `{tags}` body that does not match `AssignTagDto { assignIds, model, value }`. Fix: channel id belongs in `assignIds`, tag id in its own slot, body per DTO.

Both fixes land with regression tests (§6.11) and are prerequisites for trusting `LookupTags` results in search (§7) and routing (§9).

### 6.10 Telemetry

Events in `entity.action` form (Phase 3 §4.5 conventions):

```
tag.assigned                 { model, key, targetCount, retailerId }
tag.unassigned               { model, key, targetCount, retailerId }
tag.taxonomy.key_created     { key, valueType, origin }
tag.taxonomy.key_updated     { key, change }
tag.taxonomy.key_deleted     { key, liveAssignments }
tag.effective_kvps.recomputed{ endpointId, zoneId, trigger }   // fired by §4 on tag lifecycle events
tag.legacy_asset_api.called  { route, retailerId }             // §6.3 sunset gauge — target: zero for 14 days
tag.assign.rejected          { code, model, key }              // UNKNOWN_TAG_KEY | INVALID_TAG_VALUE | TAG_MODEL_MISMATCH
```

### 6.11 Required Tests

**Schema & assignment**

- Assign/lookup round-trip for every `TagModel` including `ZONE` and `ASSET`.
- `TAG_MODEL_MISMATCH`: assigning with `model: 'channel'` against a zone id → `400`.
- Enum value outside `allowedValues` → `400 INVALID_TAG_VALUE`; unknown key without taxonomy-admin → `400 UNKNOWN_TAG_KEY`.
- `LookupTags` reverse search returns zone and asset assignments alongside existing tiers.

**Migration adapter**

- Backfill idempotency: running the asset-tag backfill twice produces no duplicate `TagEntity`/`TagAssignment` rows.
- Legacy `{id}/tags` read returns the legacy shape sourced from the unified store; legacy write lands in the unified store and is visible via `GET /v1/retailers/tags?model=asset`.
- Legacy responses carry `Deprecation` and `Sunset` headers; each hit emits `tag.legacy_asset_api.called`.

**Effective KVP computation**

- GPU-endpoint canonical case: two zones on one endpoint with distinct `brand_content` zone-local tags produce two distinct effective sets; a `brand_content = 'NVIDIA'` rule matches exactly one `(endpointId, zoneId)` unit.
- Collision precedence: zone-local `region` shadows site `region` for that zone only; sibling zones on the same endpoint keep the site value.
- Entity-derived keys cannot be shadowed: a rogue `store_id` tag on any tier does not displace the derived `store_id`.
- Static contract enforcement: a provisioned unit missing `screen_orientation` fails `assertStaticContractResolved` and is flagged (not searchable-with-holes) — asserts §4 invariant wiring.
- Tag change on a channel triggers effective-KVP recompute (`tag.effective_kvps.recomputed`) for every `(endpointId, zoneId)` unit under every endpoint carrying that channel (D2 1:many fan-out) — and enqueues **no** `sov-recalc` job.

**Consumer integration**

- Rule-builder key picker renders taxonomy keys, not the removed `KVP_KEYS` constant (assert the constant is deleted, not orphaned).
- Search `kvpRules` filter matches against denormalized effective KVPs (integration with §7 contract tests).
- Asset-routing join: asset tagged `brand_content = 'AMD'` resolves to exactly the AMD zone in the canonical example (integration with §9).

**Regression (production defects, §6.9)**

- Endpoint tag assign sends enum `'media-player'`; typecheck passes without `as any`.
- Channel tag assign sends `AssignTagDto { assignIds: [channelId], model: 'channel', value: tagId }` with ids in the correct slots.

---

## 7. Inventory Search Contract & Campaign Builder Integration

This section pins the v2 inventory search contract (D6, resolved 2026-07-16) and specifies the frontend integration that replaces the current unverified wiring. Today the FE calls `InventoryControllerSearch` with `{ filters: {}, page, pageSize } as never` — the cast exists because the local SDK (4.19.0) has no `InventoryController` types and the contract was never pinned. This section is the single source of truth for the request and response shapes. The SDK is regenerated from this contract, the `as never` cast is removed, and contract tests pin the schema so drift is caught at CI, not at runtime.

**Route:** `POST /v2/retailers/:retailerId/inventory/search`

Search is a **pure read**. It consumes the provisioned inventory (§4), the precomputed SOV availability calendar (§5), effective KVP sets (§6), rate cards, and store traffic. It never mutates state and never recomputes availability across the estate at query time (§7.5). Booking commits are a separate, transactional operation (Phase 2 booking engine) — see §7.8 for the consistency and error model.

### 7.1 Request Contract — the Layered Multi-Dimensional Filter

The request is **layered**: each dimension narrows the result set produced by the dimension above it. The layering is not cosmetic — it is the evaluation order the server executes and the order the Campaign Builder Step 2 filter panel presents (§7.7).

| Layer | Dimension | Semantics |
|---|---|---|
| 1 | **Site scope** | Explicit `siteIds[]` or `allSites: true`. The first dimension the planner picks. Every subsequent layer evaluates only zones belonging to endpoints at in-scope sites. |
| 2 | **KVP rules** | Layered within the site scope. Evaluated against each zone's **effective KVP set** (site ∪ endpoint ∪ channel ∪ zone-local, most-specific tier wins — §6). |
| 3 | **Flight date range** | The availability window. Remaining SOV is computed over exactly this window (§7.3). |
| 4 | **Ad duration** | Line-item context. Drives duration-fit filtering and the plays/guarantee math (§7.3). |

```ts
/** POST /v2/retailers/:retailerId/inventory/search — request body */
interface InventorySearchRequestV2 {
  // ── Layer 1: site scope (exactly one of the two must be set) ──
  siteIds?: string[];            // explicit site selection; non-empty when present
  allSites?: boolean;            // true = entire estate; mutually exclusive with siteIds

  // ── Layer 2: KVP rules, evaluated within the site scope ──
  // Grammar and evaluation semantics are owned by §6; the request embeds the
  // same rule shape the rule builder produces. Omitted/empty = no KVP filtering.
  kvpRules?: KvpRuleSet;

  // ── Layer 3: flight date range (availability window) ──
  flightStart: string;           // ISO 8601 date (day granularity, inclusive)
  flightEnd: string;             // ISO 8601 date (day granularity, inclusive); >= flightStart

  // ── Layer 4: ad duration (line-item context) ──
  adDurationSeconds: number;     // integer seconds; must be a positive multiple of
                                 // the retailer's atomicUnit (SSP waterfall config)

  // ── Optional narrowing ──
  inventoryTypes?: InventoryUnitType[]; // e.g. ['screen_zone_slot']; default = all digital types (§3)
  candidateShares?: number[];    // decimals in (0, 1]; share levels to compute metrics at.
                                 // Default: server-side ladder from SSP waterfall config
                                 // (atomic share steps, e.g. [0.05, 0.10, 0.15, 0.20, 0.25, 0.50]).
  minAvailableShare?: number;    // decimal in [0, 1]; drop zones whose remaining SOV
                                 // over the window is below this. Default 0 (return all, incl. sold out).

  // ── Pagination & sort ──
  page: number;                  // 1-based
  pageSize: number;              // max 100
  sort?: 'availableShare:desc' | 'availableShare:asc'
       | 'estimatedImpressions:desc' | 'rate:asc' | 'storeName:asc';
}

/** KVP rule shape — canonical grammar defined in §6; embedded here for the wire contract. */
type KvpOperator = 'eq' | 'neq' | 'in' | 'nin' | 'exists' | 'not_exists';

interface KvpCondition {
  key: string;                   // taxonomy key (§6), e.g. 'store_tier', 'brand_content', 'zone_type'
  op: KvpOperator;
  value?: string | string[];     // absent for exists / not_exists
}

interface KvpRuleGroup {
  logic: 'and' | 'or';
  conditions: KvpCondition[];
}

interface KvpRuleSet {
  logic: 'and' | 'or';           // combinator across groups
  groups: KvpRuleGroup[];
}
```

**Validation rules (400 on violation, standard error envelope):**

1. Exactly one of `siteIds` (non-empty) or `allSites: true` is present. Both or neither → `VALIDATION_ERROR`.
2. `flightEnd >= flightStart`; window length capped at 366 days.
3. `adDurationSeconds > 0` and a multiple of the retailer's `atomicUnit`; otherwise `VALIDATION_ERROR` with the valid step in `details`.
4. Every `kvpRules` key must exist in the retailer's tag taxonomy (§6). Unknown keys → `VALIDATION_ERROR` listing the offending keys (protects against FE/taxonomy drift).
5. `candidateShares` entries are decimals in (0, 1] per the platform percentage convention (Phase 1 §2.2); values are snapped down to the atomic share step.
6. Endpoint requires the retailer's SSP package (existing package-gating middleware); without it → `403`.

### 7.2 Response Contract — Per-Zone Rows

The response is a paginated list of **zones** — the sellable unit keyed `(endpointId, zoneId)` (D2). All metrics are **server-computed**; the FE renders them verbatim and performs no availability, guarantee, or impression math of its own (§7.6).

```ts
/** POST /v2/retailers/:retailerId/inventory/search — response body */
interface InventorySearchResponseV2 {
  items: InventorySearchZoneRow[];
  page: number;
  pageSize: number;
  totalItems: number;
  totalPages: number;

  /** Echo of the resolved query context — lets the FE display what the server actually evaluated. */
  resolved: {
    siteCount: number;               // sites in scope after layer 1
    flightStart: string;
    flightEnd: string;
    adDurationSeconds: number;
    candidateShares: number[];       // the ladder actually used (request override or server default)
    guaranteePct: number;            // retailer SSP waterfall config — replaces FE GUARANTEE_PCT constant
    deliveryBufferPct: number;       // conservative-guarantee buffer (source PRD §3.6)
  };
}

interface InventorySearchZoneRow {
  // ── Identity ──
  endpointId: string;
  zoneId: string;                    // stable for the life of the channel (Backend Confirmation #1)
  storeId: string;                   // siteId of the endpoint's store
  storeName: string;
  endpointName: string;
  channelId: string;
  channelName: string;
  zoneName: string;
  zoneType: 'standard' | 'take-over';
  inventoryType: InventoryUnitType;  // §3

  // ── Loop config (endpoint-level clock, D5) ──
  loop: {
    loopDurationSeconds: number;     // endpoint-level (one clock per endpoint per store)
    retailerReservedSeconds: number;
    sellableSecondsPerLoop: number;  // loopDuration − retailerReserved
    atomicUnitSeconds: number;
    loopsPerDay: number;             // from the unit's sovCalendars documents (§5)
    adSlotsPerLoop: number;          // floor(sellableSecondsPerLoop / adDurationSeconds), for the requested duration
    durationFits: boolean;           // adDurationSeconds <= sellableSecondsPerLoop
  };

  // ── Remaining SOV over the requested window (read from sovCalendars, §5) ──
  availability: {
    availableShare: number;          // decimal [0,1] — MIN availableShare across all day buckets in [flightStart, flightEnd]
    bookedShare: number;             // decimal [0,1] — MAX bookedShare across the same buckets (= 1 − availableShare)
    soldOutDays: number;             // count of buckets in the window with availableShare === 0
    calendarVersion: number;         // version of the newest sovCalendars doc read — echoed for drift diagnostics
    recomputedAt: string;            // ISO 8601 — oldest recomputedAt among buckets read
  };

  // ── Plays & guarantees at candidate share levels (server-computed, §7.3) ──
  shareLevels: ShareLevelMetrics[];

  // ── Estimated impressions basis ──
  traffic: {
    avgDailyTraffic: number;         // from storeTraffic for the window (or store default)
    visibilityFactor: number;        // decimal (0,1] — zone visibility weight (zoneWeight-derived, §3)
    impressionsPerPlay: number;      // avgDailyTraffic-derived per-play impressions — replaces FE IMPRESSIONS_PER_PLAY constant
  };

  // ── Rate card leaves (resolved for this (endpointId, zoneId), §3) ──
  rate: {
    rateCardId: string | null;       // null = zone not yet priced (still returned; funnel surfaces it, §8)
    model: 'cpm' | 'flat_per_day' | 'flat_per_flight';
    cpmCents?: number;               // when model === 'cpm'
    flatCents?: number;              // when model is flat_*
    currency: string;                // ISO 4217
  };
}

interface ShareLevelMetrics {
  share: number;                     // decimal (0,1] — candidate share level
  bookable: boolean;                 // share <= availability.availableShare (over the whole window)
  playsPerDay: number;               // floor(loopsPerDay × share) — see §7.3
  totalPlays: number;                // playsPerDay × flightDays
  guaranteedPlaysPerDay: number;     // floor(playsPerDay × guaranteePct × deliveryBufferPct) — conservative guarantee
  guaranteedTotalPlays: number;      // guaranteedPlaysPerDay × flightDays
  estimatedImpressionsPerDay: number;// round(playsPerDay × impressionsPerPlay)
  estimatedTotalImpressions: number;
  estimatedCostCents?: number;       // rate applied to guaranteed impressions/plays; absent when rateCardId is null
}
```

**Row inclusion rules:**

- Only **provisioned, active, sellable** units (§4) at in-scope sites appear. Units missing their TimeBudget are excluded and counted in a `provisioningWarnings` log metric — never a throw (fixes the Phase 2 §3.5.1 null-deref risk).
- Zones with `availableShare === 0` are included by default (rendered "sold out" in the FE) unless `minAvailableShare` excludes them.
- Zones where `durationFits === false` are included with `shareLevels: []` and `loop.durationFits: false` — the FE renders "ad too long for this zone's loop" rather than silently hiding inventory.

### 7.3 Server-Side Metric Derivation

All read-time math is per-row and cheap (§5 precomputes only booked/available share; everything else derives at read time from the day buckets + `loopsPerDay` + rate card + traffic):

```
flightDays        = daysInclusive(flightStart, flightEnd)
availableShare    = min(bucket.availableShare for bucket in sovCalendars buckets over window)   // §5
playsPerDay(s)    = floor(loopsPerDay × s)
guaranteed(s)     = floor(playsPerDay(s) × guaranteePct × deliveryBufferPct)    // floor-rounded — never over-promise
impressions(s)    = round(playsPerDay(s) × impressionsPerPlay)
  where impressionsPerPlay = f(avgDailyTraffic, visibilityFactor)               // Phase 1 §4 impression math, per inventory type
```

`guaranteePct` and `deliveryBufferPct` come from the retailer's SSP waterfall config — they are **response-echoed** (`resolved.*`) so the FE can label the guarantee basis, but the FE never re-derives guaranteed plays from them. Floor-rounding at every integer step is deliberate: guarantees are conservative by construction (source PRD §3.6; takeover impact is absorbed in this buffer per D5).

### 7.4 Brand-Audience Redaction

The endpoint accepts `?audience=brand`, injected by the BFF when `req.user.role === 'brand'`. The server returns the redacted shape — SOV internals (`availability.*`, `shareLevels[].bookable`, booked-share fields) and rate card details (`rate.cpmCents`, `rate.flatCents`, rate model) are stripped; brands receive availability as a boolean and deal-price only. The redaction rules, field list, and brand-portal rendering are owned by **Phase 4 §6.3** and are not re-specified here; this contract adds no new redacted fields beyond mapping Phase 4's list onto the v2 shape. Contract tests (§7.9) assert the redacted shape for `audience=brand`.

### 7.5 Backend Behavior

**The search reads `sovCalendars` only. It never computes availability across the estate at query time** (D9). The TimeBudget's `bookings[]` array is touched exclusively by booking commits (Phase 2 booking engine) — never by search.

```
searchInventory(retailerId, req):
  assertSspPackage(retailerId)                                  // package gating
  validate(req)                                                 // §7.1 rules

  // Layer 1 — site scope
  siteIds = req.allSites ? allActiveSiteIds(retailerId) : req.siteIds

  // Candidate units: provisioned, active, sellable, in-scope, type-matched
  units = inventoryUnits.find({
    retailerId, status: 'active', sellable: true,
    storeId: { $in: siteIds },
    inventoryType: { $in: req.inventoryTypes ?? ALL_DIGITAL_TYPES },
  })                                                            // indexed: (retailerId, storeId, status)

  // Layer 2 — KVP rules against each zone's EFFECTIVE KVP set (§6)
  units = units.filter(u => evaluateKvpRules(req.kvpRules, effectiveKvps(u)))
  // effectiveKvps resolution + caching strategy is owned by §6.
  // Implementation note: prefer precomputed effective-KVP snapshots on the unit
  // (§6) over N per-row tag lookups.

  // Layer 3 — availability window, read from the calendar (§5)
  months = monthsCovering(req.flightStart, req.flightEnd)
  calendars = sovCalendars.find({ retailerId,
    unitKey: { $in: units.map(u => [u.endpointId, u.zoneId]) },
    month: { $in: months } })                                   // one batched read, indexed (retailerId, endpointId, zoneId, month)

  rows = units.map(u =>
    buildRow(u, bucketsFor(u, calendars, req.flightStart, req.flightEnd),
             rateCardLeaf(u), trafficFor(u.storeId, window), req))   // §7.3 math

  rows = rows.filter(r => r.availability.availableShare >= (req.minAvailableShare ?? 0))
  return paginate(sort(rows, req.sort), req.page, req.pageSize)
```

**Missing-bucket policy:** a unit with no `sovCalendars` document for a month in the window is treated as **100% available for that month** only if the unit was provisioned after the last full rebuild; otherwise the row is served with `availableShare` computed from the buckets that exist and a `sov_calendar.bucket_missing` metric is emitted so §5's repair job can be triggered. Missing buckets never cause a 500.

**Performance budget:** p95 ≤ 800 ms for `allSites: true` on a 1,000-store / 5,000-unit estate. The query plan above is two indexed batch reads plus per-row arithmetic — no aggregation across bookings, no per-row round trips.

### 7.6 Frontend Integration (Campaign Builder Step 2)

**Route:** `/deal-desk/campaigns/[id]/builder` Step 2 — `CampaignBuilderClient.tsx` (wizard state in the existing Zustand builder store, per Phase 3 §2.4).

**APIs consumed:**
- `InventoryControllerSearchV2` — the contract above (`cqMutationInventoryControllerSearchV2`; POST-as-search, invoked imperatively on filter apply, not on keystroke)
- `SiteControllerFindAll` — site picker options (replaces the hardcoded `STORES` catalog)
- `LineItemControllerFindAll` (campaign-scoped) — line-item context (replaces the hardcoded `LINE_ITEMS` catalog)
- `TagControllerTaxonomy` (§6) — KVP rule builder key/value pickers (replaces the hardcoded `KVP_KEYS` array)

**Integration work items (all required — this is the D6 closure):**

1. **Remove the `as never` cast.** Regenerate `@conqrse/api-sdk` from the pinned v2 contract; the FE compiles against real request/response types. Any remaining `as never` / `as any` on inventory calls is a CI lint failure (add the ESLint restriction scoped to `src/**/deal-desk/**`).
2. **Delete hardcoded catalogs.** `LINE_ITEMS` and `STORES` constants are removed; both come from the APIs above. The builder must render correctly for a retailer whose catalogs differ in size and shape from the mock data.
3. **Delete FE metric constants.** `IMPRESSIONS_PER_PLAY` and `GUARANTEE_PCT` are removed. Plays, guaranteed plays, impressions, and cost render from `shareLevels[]` and `resolved.*` verbatim — the math is single-source on the server (§7.3). The share slider snaps to `resolved.candidateShares`; intermediate values interpolate display-only and are re-fetched on release.
4. **Send the KVP rules.** The Step 2 rule builder's output (currently held client-side and never sent) serializes to `kvpRules` on every search. Round-trip fidelity is a required test.
5. **Step 2 filter panel mirrors the request layering** (§7.1):
   - **Site picker first** — multi-select with "All sites" toggle; nothing below it is enabled until site scope is set.
   - **KVP rule builder second** — visually nested within the site scope ("within these sites…"); keys/values from the §6 taxonomy lookup.
   - **Date range** — read-only display, sourced from the active line item's flight (`flightStart`/`flightEnd`); editing flight dates happens in Step 1, not the filter panel.
   - **Ad duration** — read-only display, sourced from the line item's `adDurationSeconds`.
6. **Row rendering:** sold-out zones render disabled with "0% available for this flight"; `durationFits === false` zones render disabled with the loop-fit message (§7.2); `rateCardId === null` zones render with "no rate card" and a deep link to Rate Card Management (View 8.0) for admin users.

**State:**
- Server: search results (mutation result cached in the builder store keyed by serialized filter state), sites, line items, taxonomy
- Zustand (builder store): applied filter set, selected zones + chosen share per zone, per-zone `calendarVersion` snapshot at selection time
- URL: `?step=2` only — filter state lives in the builder store with the wizard draft (auto-save per Phase 3 §6)

**Validation:**
- Zod schema for the filter form mirrors `InventorySearchRequestV2` 1:1 (generated or hand-pinned with a type-equality assertion `satisfies z.ZodType<InventorySearchRequestV2>`).
- "Apply filters" disabled until site scope is valid; KVP groups with empty conditions are pruned before send.

**Cache invalidation:**
- Search results are re-fetched whenever the line item's flight dates or ad duration change in Step 1 (the builder store subscribes and marks Step 2 results stale).
- After a successful booking commit, invalidate the Step 2 result set and `cqQueryInventoryControllerCalendar` for the affected units (the §5 recalc will land asynchronously; the stale-flag treatment below covers the gap).

### 7.7 Error Treatments

Search itself returns only validation (`400 VALIDATION_ERROR`), auth (`401/403`), and standard `5xx` envelopes. The interesting failures happen **at commit**, because search reads the derived calendar while commits validate against the authoritative TimeBudget (§5, D9):

| Error | Where | Treatment |
|---|---|---|
| `409 OVERBOOKING` | Booking commit (Phase 2 engine) | **Existing Phase 3 §4.2 drift flow — reuse verbatim.** The share the planner selected from search results is no longer available at commit time (calendar staleness or a concurrent booking). The FE re-runs the search for the affected zones, re-renders current availability, and prompts the planner to adjust share or drop the zone. No new UX is specified here. |
| `409 STALE_WRITE` | Booking commit | Existing Phase 3 §4.2 optimistic-version treatment — refetch and retry prompt. |
| `409 BOOKINGS_EXIST` | Admin edits on booked entities (§4) | Not reachable from the builder; owned by §8's locked-state UX. Listed here only so engineering doesn't wire it into the commit path. |
| `sov_calendar.bucket_missing` (metric, not an error) | Search read path | Row still served (§7.5 policy); ops alert threshold owned by §5. |

The builder additionally surfaces a **soft staleness hint**: if a selected zone's `availability.recomputedAt` is older than the retailer's recalc SLA (§5) at commit time, the FE re-searches that zone before submitting — reducing, not replacing, the `OVERBOOKING` safety net.

### 7.8 Consistency Model (restated for this contract)

- Search reads `sovCalendars` (derived, eventually consistent — §5).
- Booking commits validate transactionally against `timeBudgets.bookings[]` with the optimistic version lock (§5, D9). **Commits never read the calendar.**
- Therefore calendar staleness can produce a disappointing `409 OVERBOOKING` at commit, but can never double-sell. This sentence is normative: any implementation in which the commit path consults `sovCalendars` is incorrect.

### 7.9 Contract Tests (pin the schema)

Contract tests live with the API and run in CI on both repos (API + `conqrse-admin`):

1. **Request schema pin** — golden JSON fixtures for: `siteIds` scope, `allSites` scope, nested `kvpRules` (2 groups, mixed operators), with/without `candidateShares`. Server must accept all; a rejected fixture fails the build.
2. **Response schema pin** — golden response fixture validated field-for-field against `InventorySearchResponseV2` (types, required/optional, percentage-as-decimal and cents conventions per Phase 1 §2.2). SDK regeneration must produce types that compile against the fixtures.
3. **Redaction pin** — same request with `?audience=brand` must match the Phase 4 §6.3 redacted field list: no `availability.availableShare`, no `availability.bookedShare`, no `rate.cpmCents`/`rate.flatCents`.
4. **Mutual-exclusion pin** — `siteIds` + `allSites: true` together → `400 VALIDATION_ERROR`.
5. **FE round-trip pin** — the Step 2 filter panel's serialized output for a representative filter state deep-equals the corresponding request fixture (guards against the "held client-side, never sent" regression).

### 7.10 Telemetry

| Event | Fired | Props |
|---|---|---|
| `inventory.searched` | On every search execution | `siteScope: 'explicit' \| 'all'`, `siteCount`, `kvpGroupCount`, `kvpConditionCount`, `flightDays`, `adDurationSeconds`, `resultCount`, `durationMs` |
| `inventory.search_zero_results` | When `totalItems === 0` | same props as above — this is the "0 sellable units" detector feeding §8's funnel |
| `inventory.search_row_excluded` | Server-side counter (not per-row FE event) | `reason: 'sold_out' \| 'duration_misfit' \| 'no_time_budget'` |
| `campaign_builder.step2_filters_applied` | On Apply in Step 2 | serialized filter summary (no PII) |
| `campaign_builder.zone_selected` | Zone added to the plan | `endpointId`, `zoneId`, `share`, `bookable` |
| `campaign_builder.overbooking_conflict` | On `409 OVERBOOKING` at commit | `zoneCount`, `staleness Ms` (now − oldest `recomputedAt` among conflicted zones) |

### 7.11 Required Tests

**Backend (integration):**
1. Layer order: KVP rules never match zones outside the site scope, even when tags would match estate-wide.
2. Effective-KVP evaluation: zone-local tag overrides channel/endpoint/site value for the same key (§6 collision rule) and the search result reflects the zone-local value.
3. `availableShare` = min across day buckets: a zone 100% free except one fully-booked day inside the window returns `availableShare: 0` and `soldOutDays: 1`; the same search with the window moved off that day returns the free share.
4. Guarantee math: for known `loopsPerDay`, `guaranteePct`, `deliveryBufferPct`, and share ladder, `shareLevels[]` reproduces the worked values (floor at each integer step) — property test across the ladder.
5. Missing TimeBudget → row excluded, no throw, warning metric emitted.
6. Missing calendar bucket → §7.5 policy, no 500.
7. `audience=brand` → redacted shape (contract test #3).
8. Package gating: retailer without SSP → 403.
9. Performance: seeded 5,000-unit estate, `allSites` search meets the p95 budget.

**Frontend:**
10. No `as never` / `as any` on any inventory call path (lint rule green).
11. Step 2 renders sites and line items from API data with `LINE_ITEMS`/`STORES` constants deleted (build fails if referenced).
12. Displayed plays/guarantees/impressions equal `shareLevels[]` values verbatim for a fixture response — no FE-side derivation (assert `IMPRESSIONS_PER_PLAY`/`GUARANTEE_PCT` no longer exist).
13. KVP rule builder output round-trips into `kvpRules` on the wire (MSW intercept assertion).
14. Site picker gates the panel: KVP builder disabled until site scope set; date range and ad duration render read-only from the line item.
15. `409 OVERBOOKING` at commit triggers the Phase 3 §4.2 drift flow: re-search fires for conflicted zones and the adjust/drop prompt renders.
16. Sold-out, duration-misfit, and no-rate-card rows render their specified disabled states (§7.6 item 6).

---

## 8. Admin UI — Cue Chain Wiring, SSP-Mode Views & Sellability Funnel

This section covers build items **B2** (wire the Cue admin chain UI + the SSP-mode channel/zone view) and **B5** (sellability funnel) from the gap analysis. All views below already exist as presentational components on `develop` — endpoint→channel picker, channel add/detail with the layout/zone canvas, `/signages/layouts`, and Tag Manager — but ship with stubbed data (`channelsList = []`, `setTimeout` saves, "IMPLEMENT: Replace with BFF SDK hooks" markers in 51 files). This section is **wiring plus one new view variant plus one new dashboard module** — not view construction. Layouts and component structure are settled; do not reshape them.

Conventions carry over from Phase 3 unchanged:

- **Page/client separation** — `page.tsx` (server: `verifyAuth()` + Cerbos) renders `[PageName]Client.tsx` (client: all hooks, state, handlers). Presentational components under `components/` receive data and callbacks via props only.
- **Generated hooks only** — every call goes through `cqQuery*` / `cqMutation*` from `@conqrse/api-sdk/hooks` via the BFF proxy. Never raw `fetch`, never hand-rolled query keys. Cache invalidation always uses `queryKey` from the generated hook.
- **State layers** — TanStack Query for server state, URL searchParams for filters/tabs/pagination, React Hook Form + Zod for forms, `useState` for transient UI. No new Zustand stores are required by this section; the retailer-wide SSP mode flag is read from the existing capabilities store (`hasFeature('ssp')` per Phase 3 §3.3).
- **SDK pin** — every hook name below must be verified against the regenerated `@conqrse/api-sdk` ≥ 5.11 (see §7 for contract pinning and §10 for sequencing). The stub comments on `develop` reference hook names that **do not exist** in any SDK version; treat the names in this section as the target surface and reconcile against the generated output at wiring time, raising mismatches to product rather than casting through `as never` / `as any`.

**Mode adaptivity rule (applies to 8.1.2, 8.2, 8.3):** the retailer-wide SSP switch (D7, §2) selects which content-panel variant renders. Structural editing — channel creation, layout selection, zone drawing/geometry, zone tags — is **shared across both modes**. There is no per-zone mode toggle in v1.

**Booking-protection rule (applies everywhere in this section):** any mutation that would invalidate a booking — zone geometry edit or deletion, layout swap/detach, channel unassignment, endpoint retirement, loop config change — is rejected by the API with `409 BOOKINGS_EXIST` while the entity carries active or future bookings (any booking with `flightEnd >= today`; see §4). Every view below that exposes such a mutation must render the locked state specified in §8.2.4: controls disabled *pre-emptively* where lock state is known client-side, and the 409 rendered with the blocking-campaign list and the clear-bookings resolution path when the server rejects. v1 resolution is **clear-first**; move/rebook is post-v1.

---

### 8.1 Wiring the Existing Stubbed Views

Four views, all on `develop`, all currently disconnected. The wiring order matches their position in the chain (endpoint → channel → layout → tags) so each view can be verified against real data produced by the previous one.

#### 8.1.0 Known mismatches to fix during the wiring pass

These were identified in the gap analysis (§4.1, §4.6 there) and are **in scope for B2** — fix them as part of wiring, not as follow-ups:

| # | Mismatch | Where | Fix |
|---|---|---|---|
| M1 | Stub comments reference **non-existent hook names**; components were built against imagined hooks | 51 files across `develop` (`// IMPLEMENT: Replace with BFF SDK hooks`) | Wire to the actual generated `cqQuery*`/`cqMutation*` names from the regenerated SDK (e.g., `cqQueryMediaPlayerChannelControllerFindAllV1`, `cqMutationMediaPlayerZoneControllerCreateV1`). Delete every stub comment as its call site is wired. |
| M2 | UI reads `zone._id`; the entity exposes `id` (BaseEntity) | Zone canvas + zone list components in channel detail | Standardize on `id` everywhere. No `_id` access may survive the wiring pass (add a lint grep to the B2 PR checklist). |
| M3 | UI renders/edits `channel.description`; **no `description` field exists** on `MediaPlayerChannelEntity` | Channel add/detail forms | Remove the field from forms and cards. Do not silently map it to another field — if product wants a description, that is a backend schema request, not a FE remap. |
| M4 | Endpoint detail tag assign sends `model: 'MediaPlayer'` where the `TagModel` enum value is `'media-player'`, cast through `as any` | `MediaPlayerDetailClient.tsx:285–287` (master) | Use the `TagModel` enum member from the SDK types; remove the cast. Flagged PLAUSIBLE from client-side evidence — confirm against backend behavior first (gap analysis §7 caveat), then fix on both master and develop lineages. |
| M5 | Channel detail calls `AssignTags` with the **channel id in the tag-id path slot** and a `{tags}` body that does not match `AssignTagDto { assignIds, model, value }` | `MediaPlayerChannelDetailClient.tsx:673–676` (master) | Rebuild the call per the assign contract in §6: tag id in the path, `{ assignIds: [channelId], model: TagModel.CHANNEL }` in the body. Same confirm-then-fix protocol as M4. |
| M6 | Zone `width`/`height` typed `string` while `x`/`y` are `number`; px-vs-% undocumented | Zone geometry editor | Follow the units contract as pinned in §3 (entity ownership). FE parses/serializes per that contract; no FE-local unit guessing. |

**Required tests (mismatch pass):**
- Static check: repo-wide grep for `_id`, `as never`, `as any` on SDK call sites in the signage tree returns zero hits post-wiring.
- Tag assign requests for endpoint and channel serialize exactly to `AssignTagDto` (contract test against SDK types, MSW request assertion in component tests).
- Channel form snapshot contains no `description` control.

#### 8.1.1 Endpoint → Channel Picker

**Route:** endpoint detail (`MediaPlayerDetailClient.tsx`), `ChannelPicker` + `MediaPlayerDetailsSection` components
**Owner:** Junior
**Source:** existing develop components; gap analysis chain link #2

**APIs consumed:**
- `cqQueryMediaPlayerControllerFindOneV1` — endpoint detail (includes current `channel` ref)
- `cqQueryMediaPlayerChannelControllerFindAllV1` — populate the picker (replaces the hardcoded `channelsList = []`)
- `cqMutationMediaPlayerControllerUpdateV1` — assign/unassign channel on the endpoint (replaces the `setTimeout` fake save)
- Tag assign/lookup per §6 for the endpoint's tag chips (fix M4 here)

**Behavior notes:**
- 1 channel : many endpoints (D2, §2). The picker is a single-select against the retailer's channel list; assigning the same channel to N endpoints is done per endpoint (bulk assignment is post-v1).
- **Assignment is a provisioning lifecycle event** (§4.4 E1): assigning a channel materializes one InventoryUnit + TimeBudget per zone in the channel's layout for this endpoint; unassignment deactivates them. The picker itself does nothing extra — the backend event does the work — but the success toast should say so in SSP mode: "Channel assigned — N zones provisioned as sellable inventory."
- **Unassign is booking-protected.** If any `(thisEndpointId, zoneId)` unit carries active/future bookings, the API returns `409 BOOKINGS_EXIST`; render per §8.2.4.

**State:**
- Server: endpoint detail query, channel list query
- Component: picker open/close, unassign confirmation modal
- No URL state

**Validation:**
- Unassign requires a confirm modal in both modes; in SSP mode the modal warns that sellable units for this endpoint will be deactivated.

**Cache invalidation:**
- Assign/unassign → invalidate `cqQueryMediaPlayerControllerFindOneV1` (this endpoint), `cqQueryMediaPlayerControllerFindAllV1`, and the provisioning-status query (§8.4) so funnel counts move.
- No optimistic update — the mutation can 409.

**Loading / error / empty:**
- Picker skeleton while channel list loads; empty channel list renders "No channels yet — create one" linking to channel add (8.1.2).
- `409 BOOKINGS_EXIST` → locked-state dialog per §8.2.4.

**Telemetry:**
- `endpoint.channel_assigned` (props: `endpointId`, `channelId`)
- `endpoint.channel_unassigned` (props: `endpointId`, `channelId`)
- `endpoint.channel_unassign_blocked` (props: `endpointId`, `blockingBookingCount`)

**Required tests:**
- Picker renders real channel list; selecting fires the update mutation with the channel id.
- Unassign on an endpoint with bookings renders the blocked dialog listing campaigns (MSW 409 fixture).
- Success invalidates endpoint + provisioning-status queries.
- M4 fix verified (enum value serialized, no cast).

#### 8.1.2 Channel Add / Detail with Layout + Zone Editor

**Route:** channel list, channel add, channel detail (`MediaPlayerChannelDetailClient.tsx`) with the zone canvas
**Owner:** Senior (this view also hosts the 8.2 SSP variant and the 8.3 zone tag editor)
**Source:** existing develop components; gap analysis chain link #3

**APIs consumed:**
- `cqQueryMediaPlayerChannelControllerFindAllV1` / `FindOneV1` — list + detail
- `cqMutationMediaPlayerChannelControllerCreateV1` / `UpdateV1` / `DeleteV1`
- `cqQueryMediaPlayerLayoutControllerFindAllV1` — layout template picker
- `cqMutationMediaPlayerChannelControllerCreateChannelLayoutV1` (`CreateChannelLayoutV1`) — attach layout to channel (clone-attach; zoneIds are stable for the life of a channel per Backend Confirmation #1, §2)
- `cqQueryMediaPlayerZoneControllerFindAllV1` (by layout) — zone list for the canvas
- `cqMutationMediaPlayerZoneControllerCreateV1` / `UpdateV1` / `DeleteV1` — zone CRUD from the canvas
- Tag assign/lookup per §6 for channel tags (fix M5 here) and zone tags (§8.3)
- SSP mode only: SOV calendar + provisioning reads per §8.2

**State:**
- Server: queries above
- URL: `?tab=structure|content` (structure = layout/zone editor, both modes; content = schedule calendar in Cue mode, SOV ledger in SSP mode per §8.2), `&zoneId=` for the selected zone panel
- Forms: React Hook Form + Zod for channel create/edit and zone properties (geometry, name, weight, type `standard|take-over`, tags per §8.3)
- Component: canvas selection/drag state

**Validation:**
- Zone geometry per the units contract (M6, §3).
- Σ `zoneWeight` ≤ 1.0 per layout — validate client-side on zone save and surface the server-side invariant error (§4.6 I-1) verbatim if it disagrees.
- Layout swap/detach and zone edit/delete are **booking-protected** (see below).

**Booking-protection surface (this view is where the lock bites hardest):**
- Zone geometry edit, zone delete, layout swap, layout detach, channel delete → all can `409 BOOKINGS_EXIST` in SSP mode.
- The SSP variant already knows per-zone lock state from the SOV data (§8.2); use it to disable geometry fields and delete buttons *before* the user tries, with a lock icon + tooltip "Locked — N active/future bookings". The 409 path remains the source of truth for anything the client can't know (e.g., a booking landing mid-edit).
- Render blocked mutations per §8.2.4.

**Cache invalidation:**
- Channel/layout/zone mutations → invalidate the channel detail query, zone list query, layout list query, and the provisioning-status query (§8.4). Zone mutations additionally invalidate the affected zone's SOV calendar query (§8.2) — the `sov-recalc` job (§5) is async, so refetched calendar data may briefly predate the change; the ledger view shows `recomputedAt` for exactly this reason.
- No optimistic updates anywhere in this view: every structural mutation can 409.

**Loading / error / empty:**
- Canvas skeleton during layout/zone load.
- Channel without layout: empty state "No layout attached — choose a layout" opening the template picker (this is a sellability-funnel stage, §8.4).
- `409 BOOKINGS_EXIST` per §8.2.4; `409 STALE_WRITE` per the existing Phase 3 §4.2 treatment (refetch + retry prompt).

**Telemetry:**
- `channel.created`, `channel.updated`, `channel.deleted` (props: `channelId`)
- `channel.layout_attached` (props: `channelId`, `layoutId`)
- `zone.created`, `zone.updated`, `zone.deleted` (props: `channelId`, `zoneId`)
- `zone.edit_blocked` (props: `zoneId`, `blockingBookingCount`)

**Required tests:**
- Layout attach fires `CreateChannelLayoutV1` and the canvas renders the cloned zones with their (stable) ids.
- Zone create/edit/delete round-trips through real hooks; `id` used throughout (M2).
- Weight-sum validation blocks save at Σ > 1.0.
- Zone with bookings: geometry fields disabled, delete disabled, lock tooltip present; forced mutation (MSW 409) renders the blocked dialog.
- Layout swap on a channel with any booked zone renders the blocked dialog listing all blocking campaigns across zones.
- Tab switching preserves `zoneId` selection.

#### 8.1.3 Layouts Page

**Route:** `/signages/layouts` — currently skeleton-only
**Owner:** Junior
**Source:** gap analysis chain link #3

**APIs consumed:**
- `cqQueryMediaPlayerLayoutControllerFindAllV1` — layout template list
- `cqQueryMediaPlayerLayoutControllerFindOneV1` + `cqQueryMediaPlayerZoneControllerFindAllV1` — read-only zone preview per layout
- `cqMutationMediaPlayerLayoutControllerCreateV1` / `UpdateV1` / `DeleteV1` — template CRUD

**Behavior notes:**
- This page manages layout **templates**. Channel-specific layout instances (the clone-attach product of `CreateChannelLayoutV1`) are edited in channel detail (8.1.2), not here. The page must label templates vs. make no claim of editing live channel layouts — editing a template does **not** propagate to channels that cloned it (Backend Confirmation #1, §2).
- Template delete is safe by definition (templates carry no bookings); channel-attached instances are not deletable from this page at all.

**State:** server list query; URL `?q=&page=&pageSize=`; component: preview drawer.

**Validation:** template create/edit uses the same zone Zod schema as 8.1.2 (shared schema module — do not fork it).

**Cache invalidation:** template CRUD → invalidate layout list. No provisioning impact (templates are not sellable).

**Loading / error / empty:** table skeleton; empty state "No layout templates — create one."

**Telemetry:**
- `layout.created`, `layout.updated`, `layout.deleted` (props: `layoutId`)
- `layout.previewed` (props: `layoutId`)

**Required tests:**
- List renders from the real hook; skeleton page fully replaced.
- Preview drawer renders zones read-only.
- Copy explicitly distinguishes template edits from attached-instance edits (assert the explainer text exists).

#### 8.1.4 Tag Manager

**Route:** Tag Manager (wired on master; stubbed on develop — reconcile to one wired implementation on the branch carrying this build)
**Owner:** Junior
**Source:** gap analysis chain link #5; unified tag architecture per §6

**APIs consumed (all under the extended `/v1/retailers/tags/*` surface per §6):**
- Tag CRUD hooks (`cqQueryTagControllerFindAllV1`, `cqMutationTagControllerCreateV1` / `UpdateV1` / `DeleteV1`)
- Assign / lookup hooks (`cqMutationTagControllerAssignTagsV1`, `cqQueryTagControllerLookupTagsV1`)

**Behavior notes:**
- The manager gains the two new `TagModel` tiers from §6: **ZONE** and **ASSET**. The model filter and the create/edit form's model select list all six tiers (SITE, MEDIA_PLAYER, CHANNEL, PLAYLIST_CONFIG, ZONE, ASSET).
- Key/type/value-list constraints come from the taxonomy (§6.4) — the manager is where taxonomy violations surface as validation errors, not free-text warnings.
- Reverse lookup ("what carries this tag") must render zone assignments with their `(endpointId, zoneId)` context, since a zone is only meaningful per endpoint (D2, §2).

**State:** server queries; URL `?model=&q=&page=`; forms via RHF + Zod generated from the taxonomy.

**Cache invalidation:** tag CRUD/assign → invalidate tag list + lookup queries, and the effective-KVP query used by the zone tag editor (§8.3) when `model === ZONE`.

**Telemetry:**
- `tag.created`, `tag.updated`, `tag.deleted` (props: `tagId`, `model`)
- `tag.assigned`, `tag.unassigned` (props: `tagId`, `model`, `assignCount`)

**Required tests:**
- ZONE and ASSET appear in model filter and create form.
- Assign call serializes to `AssignTagDto` exactly (regression net for M4/M5).
- Taxonomy-invalid key or value blocks save with a field-level error.

---

### 8.2 SSP-Mode Channel/Zone View

**Route:** channel detail (8.1.2), `?tab=content&zoneId=` — the per-zone content panel
**Owner:** Senior
**Source:** B2 (new view variant); concept model §2; SOV calendar §5; booking-protection §4

This is the one **new** view variant in this section. The channel detail view is **mode-adaptive**: the retailer-wide SSP switch (read once from the capabilities store) selects the content panel per zone. Nothing else about the view changes between modes.

#### 8.2.1 Mode matrix

| Zone content panel | Cue mode (existing) | SSP mode (new) |
|---|---|---|
| Content | Per-zone schedule calendar (playlists/content groups) — wire the existing component to real schedule hooks | **SOV ledger view** (§8.2.2) |
| Actions | Add/edit schedule | View loop config (**read-only at the zone** — `loopDuration` is endpoint-level per D5, one clock per endpoint per store); toggle `sellable` flag; view P4 filler source; links to Loop Visualizer and the zone's rate card |
| Lock behavior | None (Cue schedules carry no bookings) | Booking-protection lock per §8.2.4 |

#### 8.2.2 SOV ledger view — content

The ledger panel is presentational (`SovLedgerPanel`, page-specific component under the channel detail route); all fetching stays in `MediaPlayerChannelDetailClient.tsx`. Props contract:

```ts
interface SovLedgerPanelProps {
  zone: { id: string; name: string; type: 'standard' | 'take-over'; weight: number };
  endpointId: string;                    // the sellable unit is (endpointId, zoneId)
  loopConfig: {                          // endpoint-level; rendered read-only at the zone
    loopDurationSeconds: number;         // e.g., 120
    retailerReservedSeconds: number;
    sellableSecondsPerLoop: number;
    source: 'retailer_default' | 'endpoint_override';
  };
  range: { from: string; to: string };   // ISO dates; user-selected, default: today → +90d
  calendar: SovCalendarDays;             // day buckets from sovCalendars (§5): bookedShare / availableShare per day
  recomputedAt: string;                  // staleness indicator — calendar is a derived view (§5)
  bookings: Array<{
    campaignId: string;
    campaignName: string;
    lineItemId: string;
    sharePct: number;
    flightStart: string;
    flightEnd: string;
    priority: number;
    status: 'active' | 'future' | 'past';
  }>;
  sellable: boolean;
  p4FillerSource: { playlistCount: number; scheduleIds: string[] } | null;  // the zone's former playlists (§2, §4.3)
  locked: boolean;                       // any booking with flightEnd >= today
  onRangeChange(range: { from: string; to: string }): void;
  onToggleSellable(next: boolean): void;
  onClearBookings(): void;               // opens the §8.2.4 resolution flow
}
```

Rendered blocks, top to bottom:

1. **Loop config strip** — loopDuration / reserved / sellable seconds, badge for `source`, lock icon with tooltip "Loop clock is endpoint-level — one clock per endpoint per store; edit from the endpoint, subject to booking protection." No edit affordance at the zone, ever.
2. **Booked vs. available share** for the selected date range — a horizontal day-bucket bar (booked share stacked vs. available) fed directly from the `sovCalendars` day buckets via `GET /v2/retailers/inventory/:endpointId/:zoneId/calendar?from=&to=` (§5). Header shows the range's **max concurrent booked share** and min available (the same math search uses, D8 §2). Footer shows `recomputedAt` with a stale hint (> 15 min old and a booking mutation is known to be in flight → "recalculating…").
3. **Bookings list** — table of campaign / share % / flight / priority, each row linking to campaign detail. Past bookings collapsed by default (they never lock, §4).
4. **Sellable toggle** — per D3, optional in v1 (retailer-wide SSP makes everything sellable by default); the toggle exists and writes the flag via the sellable-toggle lifecycle event (§4.4 E9). Toggling OFF with active/future bookings is booking-protected → 409 path.
5. **P4 filler source** — read-only card listing the zone's former playlist schedules now registered as the P4 filler pool (§4.3): "N playlists play whenever no campaign wins the loop." Links to each playlist. If null (zone had no playlists at activation), show the warning state "No filler registered — this zone falls back to the retailer default filler" per §4.3 policy.
6. **Links** — Loop Visualizer (existing view 10.5) pre-scoped to this `(endpointId, zoneId)`, and the zone's rate card entry (Phase 3 rate card view, keyed by the same identity).

#### 8.2.3 View spec

**APIs consumed (SSP variant, in addition to 8.1.2):**
- `cqQueryInventoryCalendarControllerFindV2` — `GET /v2/retailers/inventory/:endpointId/:zoneId/calendar?from=&to=` (§5), keyed by `(endpointId, zoneId, from, to)`
- `cqQueryInventoryUnitControllerFindOneV2` — `GET /v2/retailers/inventory/:endpointId/:zoneId` (§4.8.3): bookings list, sellable flag, locked state, filler pool ref — the single per-unit read; do not invent a second bookings endpoint
- `cqQueryMediaPlayerScheduleControllerFindAllV1` (read-only) — resolve the P4 filler source playlists

**State:**
- URL: `?tab=content&zoneId=&from=&to=` — the date range is URL state so a ledger view is shareable/bookmarkable
- Server: calendar query (per range), bookings/flag query
- Component: clear-bookings dialog state

**Validation:**
- Range picker: `from <= to`, max window **12 months in the UI** — deliberately tighter than the calendar API's 18-month cap (§5.7) to bound the per-view fan-out; the API headroom exists for export/reporting consumers.

**Cache invalidation:**
- `sellable` toggle → invalidate the unit's provisioning read + provisioning-status (§8.4).
- Any booking cleared via §8.2.4 → invalidate calendar + bookings queries for the unit and provisioning-status. Calendar recompute is async (Concourse `sov-recalc`, §5); keep `recomputedAt` visible rather than blocking on freshness.

**Loading / error / empty:**
- Ledger skeleton per block.
- Zone not yet provisioned (no InventoryUnit — e.g., SSP just activated, backfill in flight): render the §4.8.2 provisioning status ("Provisioning… queued by SSP activation") with a link to the funnel (§8.4). **Never render an empty ledger as if availability were 0%.**
- Fully available unit: bar renders 100% available — this is a valid state, not an empty state.

**Telemetry:**
- `zone.sov_viewed` (props: `endpointId`, `zoneId`, `rangeDays`)
- `zone.sov_range_changed` (props: `rangeDays`)
- `zone.sellable_toggled` (props: `endpointId`, `zoneId`, `next`)
- `zone.filler_source_viewed` (props: `zoneId`, `playlistCount`)

**Required tests:**
- Mode switch: same channel fixture renders schedule calendar with `ssp=false` capabilities, SOV ledger with `ssp=true` (both variants snapshot-tested).
- Loop config renders read-only; no mutation hook is reachable from the zone panel (assert no edit control).
- Day-bucket bar math: fixture with two overlapping bookings (40% Aug 1–31, 35% Aug 15–Sep 15) renders max concurrent 75% in August, per-day buckets correct at the boundaries.
- Range change updates URL and refetches only the calendar query.
- Unprovisioned zone renders provisioning state, not 0% availability.
- Sellable toggle OFF with active bookings → 409 fixture → blocked dialog.

#### 8.2.4 Locked states & the `409 BOOKINGS_EXIST` treatment

Uniform treatment everywhere the booking-protection rule applies (8.1.1 unassign, 8.1.2 zone/layout/channel mutations, 8.2.3 sellable-off, endpoint retirement, loop config on the endpoint form):

**Error shape:** the canonical `409 BOOKINGS_EXIST` envelope is §3.7 (entity, entityId, `blockingBookings[]` with campaign name/share/flight, `totalBlocking` when truncated). The FE renders `details` verbatim — no client-side reconstruction.

**Rendering contract:**

1. **Pre-emptive lock** where the client already knows lock state (SOV data loaded): disable the control, lock icon, tooltip "Locked — N active/future bookings on this zone."
2. **Blocked dialog** on 409: title "This {entity} has active bookings"; body lists every blocking booking (campaign name → link to campaign detail, share %, flight); explainer "Entities carrying active or future bookings can't be edited or deleted. Clear the bookings first, then retry."
3. **Resolution path (v1 = clear-first):** primary action **"Review & clear bookings"** — navigates to (or opens over) the affected campaigns' booking entries with a release flow per campaign (the release itself is the campaign-side mutation owned by §9; this dialog only routes there). After clearing, the user retries the original mutation manually. The dialog explicitly notes: "Moving bookings to another zone is coming later" — **move/rebook is post-v1** and must appear as roadmap copy, not a disabled button pretending to exist.
4. `409 OVERBOOKING` and `409 STALE_WRITE` keep their existing Phase 3 §4.2 treatments unchanged; do not route them through this dialog.

**Telemetry:**
- `booking_lock.dialog_viewed` (props: `entityType`, `entityId`, `blockingBookingCount`)
- `booking_lock.clear_path_entered` (props: `entityType`, `campaignCount`)

**Required tests:**
- One shared `<BookingsExistDialog>` component (generic, `src/app/components/shared`) consumed by every surface above — assert single implementation.
- Dialog renders every booking row from a 3-campaign fixture with working campaign links.
- OVERBOOKING and STALE_WRITE fixtures do **not** open this dialog.

---

### 8.3 Zone Tag Editor (`TagModel.ZONE`)

**Route:** channel detail (8.1.2) → zone properties form (both modes — tags are structural)
**Owner:** Senior (lands with 8.1.2)
**Source:** D4 (§2), unified tag architecture §6

**Behavior:**
- The zone properties form gains a **Tags** block with two distinct regions:
  1. **Inherited (read-only chips):** the effective KVP set from the inheritance chain — site ∪ endpoint ∪ channel — each chip labeled with its source tier. Fetched from the per-unit read (`GET /v2/retailers/inventory/:endpointId/:zoneId`, §4.8.3), whose `effectiveKvps[]` carries per-key `source` and `shadowed` per the §6.5 computation; never computed client-side.
  2. **Zone-local (editable):** additive tags assigned with `model: TagModel.ZONE`. This is what differentiates zones on one endpoint — canonical case: a GPU endpoint split into an AMD zone and an NVIDIA zone, each carrying its own `brand_content` tag (D4).
- On key collision, most-specific tier wins (zone > channel > endpoint > site, §6.5). When a zone-local tag shadows an inherited key, render the inherited chip struck-through with tooltip "Overridden by zone tag."
- Key/value pickers are taxonomy-driven (§6.4) — no free-text keys. This is the same taxonomy lookup that replaces the Campaign Builder's hardcoded `KVP_KEYS` array (§7); share the picker component (`src/app/components/shared`).
- Zone tags are **not** booking-protected: they are additive targeting metadata and do not invalidate bookings (§4 lock list does not include tags). Editing tags on a locked zone is allowed — the lock disables geometry/delete only.

**APIs consumed:**
- `cqMutationTagControllerAssignTagsV1` with `{ assignIds: [zoneId], model: TagModel.ZONE }` (per the §6 assign contract)
- Effective-KVP resolution read (§6.5) for the inherited chips
- `cqQueryTagControllerFindAllV1?model=zone` for the taxonomy-scoped picker options

**State:** form state inside the 8.1.2 zone form (RHF field array for zone-local tags); server: effective-KVP query keyed by `(endpointId, zoneId)`.

**Validation:** taxonomy-valid key + value; duplicate zone-local keys blocked; value type enforced per taxonomy (Zod schema generated from the taxonomy response, shared with Tag Manager 8.1.4).

**Cache invalidation:** tag assign/unassign → invalidate the effective-KVP query for the unit and the tag lookup queries. Note in the UI that search-facing effects apply at next search (effective KVPs are evaluated by the search path per §7 — no calendar recompute is triggered by tag changes).

**Loading / error / empty:** inherited chips skeleton; empty zone-local state: "No zone tags — inherited tags apply" with the add control.

**Telemetry:**
- `zone.tag_assigned` / `zone.tag_unassigned` (props: `endpointId`, `zoneId`, `key`)
- `zone.tag_shadowing_viewed` (props: `zoneId`, `key`) — fires when a strike-through chip's tooltip opens (signal for confusing inheritance)

**Required tests:**
- Assign call carries `model: TagModel.ZONE` and the zone id in `assignIds` (exact `AssignTagDto` serialization).
- AMD/NVIDIA fixture: two zones on one endpoint render distinct `brand_content` chips; effective sets differ only by the zone-local tier.
- Collision fixture: zone-local `store_tier` shadows channel-level chip (struck-through + tooltip).
- Locked zone (bookings present): tag editing remains enabled while geometry is disabled.

---

### 8.4 Sellability Funnel — Inventory Dashboard

**Route:** Inventory Dashboard (View 7.0) — new `SellabilityFunnel` module at the top of the page
**Owner:** Junior (module) with Senior review of stage math
**Source:** B5; provisioning status surface §4.8.2

This is the in-product diagnosis for **"854 stores / 66 players / 0 sellable units."** Before this module, that state was only discoverable by an engineer querying Mongo. The funnel makes the provisioning chain's break point visible to the retailer (and to support) as a sequence of stage counts, each linking to its fix surface.

#### 8.4.1 Stages

Data comes from one read — `GET /v2/retailers/:retailerId/inventory/provisioning/status` (§4.8.2) — never assembled from N client-side list queries. Stage semantics (counts are **exclusive**: an entity appears at the first stage that blocks it):

| # | Stage | Counts | Blocked because | Fix surface (link target) |
|---|---|---|---|---|
| 1 | Endpoints without a channel | endpoints, active, with no channel assigned | Nothing to derive zones from | Endpoint list filtered to unassigned → ChannelPicker (8.1.1) |
| 2 | Channels without layout/zones | channels assigned to ≥ 1 endpoint but carrying no layout or zero zones | No zones → no units | Channel detail structure tab (8.1.2) |
| 3 | Zones without a rate card | provisioned `(endpointId, zoneId)` units with no rate card entry | Unit exists but is unpriceable | Rate card manager (Phase 3 view), pre-filtered to the gap |
| 4 | Zones without traffic | units priced but whose store has no StoreTraffic data | Impression math impossible | Store Traffic view + CSV import (Phase 3) |
| 5 | **Sellable units** | units passing all gates (unit + TimeBudget + rate card + traffic + `sellable=true`) | — | Inventory search (§7) scoped to sellable inventory |

Rendered as a left-to-right funnel: each stage a card with count, delta vs. previous stage, and its link. Stages 1–4 show **warning** styling when count > 0; stage 5 shows the healthy count. A header strip totals the estate ("854 stores · 66 endpoints · N sellable units") and shows the provisioning sync state from the same response (last sync time, backfill in progress, queue depth) with a **"Run sync"** action wired to `POST /v2/retailers/:retailerId/inventory/provisioning/sync` (§4.8.1) — Cerbos-gated to retailer admin.

#### 8.4.2 Empty / zero states

| State | Rendering |
|---|---|
| SSP not active for the retailer | Module hidden entirely (package gating: `hasFeature('ssp')`) |
| SSP active, backfill never run / in flight | Funnel replaced by the provisioning progress state (§4.8.2): "Provisioning your inventory — N of M endpoints processed", with the sync status poll |
| Stage 5 = 0 with earlier stages > 0 | The **diagnosis state** — banner above the funnel: "No sellable inventory yet. {firstBlockedStage} is the first gap — fix it there." First non-zero blocked stage gets emphasized styling. This is the exact "854 / 0" scenario rendered as a to-do list instead of a mystery |
| All stages 0 blocked, stage 5 > 0 | Healthy: funnel collapses to a compact single-row summary with an expand control |
| Status endpoint errors | Module-level error card with retry; never block the rest of the dashboard |

#### 8.4.3 View spec

**APIs consumed:**
- `cqQueryInventoryProvisioningControllerStatusV2` — `GET /v2/retailers/:retailerId/inventory/provisioning/status` (§4.8.2); poll at 30s only while a sync/backfill is reported in flight
- `cqMutationInventoryProvisioningControllerSyncV2` — `POST /v2/retailers/:retailerId/inventory/provisioning/sync` (manual trigger)

**State:**
- Server: status query
- Component: none beyond the expand/collapse of the healthy state
- No URL state (the funnel is a dashboard module, not a filterable view; its links carry the filters)

**Validation:** none (read-only + one gated action).

**Cache invalidation:**
- "Run sync" → on 202, switch the status query to the in-flight poll; on completion, invalidate provisioning-status **and** the inventory search queries (§7) and dashboard stat queries.
- Mutations elsewhere in this section (8.1.1 assignment, 8.1.2 zone CRUD, 8.2.3 sellable toggle) already invalidate this query — the funnel is the convergence point that proves the chain works.

**Package gating:** entire module behind `hasFeature('ssp')`; "Run sync" additionally behind the retailer-admin Cerbos action.

**Telemetry:**
- `funnel.viewed` (props: `stageCounts: number[]`, `sellableUnits`)
- `funnel.stage_clicked` (props: `stage`, `count`)
- `funnel.zero_sellable_viewed` (props: `firstBlockedStage`) — the direct measurement of how often retailers hit the "854 / 0" state
- `provisioning.sync_triggered` (props: `source: 'funnel'`)

**Required tests:**
- Fixture reproducing the discovery scenario (854 stores / 66 endpoints / 0 units, all blocked at stage 1) renders the diagnosis banner pointing at stage 1, and stage 1's link carries the unassigned-endpoints filter.
- Exclusive-count fixture: an endpoint blocked at stage 1 does not also appear in stages 2–4.
- Healthy fixture collapses to the summary row.
- Module hidden without `ssp` capability; "Run sync" hidden without the Cerbos action.
- Sync trigger → 202 → poll → completion invalidates search + status queries (MSW sequence test).
- Status endpoint 500 renders the module error card while sibling dashboard modules still render.

---

### 8.5 Section-Level Acceptance

Rolled into §10's gates; the section is done when:

1. Zero stub markers, `setTimeout` saves, hardcoded `[]` catalogs, or `as never`/`as any` SDK casts remain in the signage/tag/funnel trees (M1–M5 closed; M6 per the §3 units contract).
2. A retailer can complete the whole chain in-product with no engineer involvement: create channel → attach layout → draw zones → tag zones → assign channel to endpoints → see units appear in the funnel → price them → watch stage 5 go non-zero → find them in inventory search (§7).
3. The SOV ledger for any booked unit agrees with the calendar API (§5) day-for-day, and every booking-protected mutation across 8.1–8.2 renders the shared `BookingsExistDialog` on 409.
4. The funnel's stage counts agree with the provisioning status endpoint exactly (no client-side recomputation), and the "854 / 0" fixture renders the diagnosis state.

---

## 9. Campaign Activation Side Effects & Creative Routing

**Owner:** Senior (backend + endpoint runtime; overlaps the Phase 4 rule-evaluator rollout channel)
**Modules:**
- Server: `workflows/activation/` (new), extensions to `routes/campaigns.ts`, `routes/endpoints.ts`
- Queue: the Concourse queue — new job type `content-sync` (distinct from `sov-recalc`, §5)
- Endpoint: existing Conqrse Cue content-sync protocol (extended message type; no new endpoint runtime beyond Phase 4 §4)

**Source:** Gap analysis B6; source PRD "assets synced to endpoint during campaign activation" (previously undefined); Phase 4 §4.1 (rule-triggered variant pre-load — referenced, not re-specified here).

Campaign activation today is a bare status PUT with zero side effects. This section defines what "normal content sync" actually means: the ordered side-effect pipeline that fires on the Ready → Active transition, the per-zone creative routing that decides *which* asset each zone receives, the sync payload contract, per-endpoint delivery tracking, and the teardown path on cancellation/completion.

**Design invariant:** a campaign is never eligible to win a loop slot on an endpoint until its content is confirmed delivered to that endpoint. Delivery state is tracked per `(campaignId, endpointId)` in `SyncStatus` records (§9.5); the waterfall skips undelivered endpoints (§9.6). SOV booking (sales time) and content delivery (distribution time) are deliberately decoupled — a booking holds share regardless of delivery state, and delivery failures surface as observable sync records, never as silent non-play.

### 9.1 The Ready → Active Pipeline

Activation is a single server-side workflow executed synchronously up to sync dispatch, with delivery itself asynchronous on the Concourse queue. The status transition to Active commits **only after** steps 1–2 succeed and step 3–4 records are durably written; steps 3–5 then proceed asynchronously.

```
activateCampaign(campaign):                          // Ready → Active transition handler
  // Precondition: campaign.status === 'ready'; all line items carry bookings
  1. deliverySet  = resolveTargeting(campaign)                     // §9.2
  2. assetPlan    = selectAssetsPerZone(campaign, deliverySet)     // §9.3 — aborts atomically
                                                                   //        if any zone resolves 0 assets
  3. for endpoint in groupByEndpoint(assetPlan):
       payload = buildCampaignContentSync(campaign, endpoint)      // §9.4
       upsert SyncStatus { status: 'pending' }                     // §9.5
       enqueue Concourse job 'content-sync' { syncId }
  4. campaign.status = 'active'   // optimistic version lock; conflict → 409 STALE_WRITE (Phase 3 §4.2)
  5. invalidateWaterfallHotCache(retailerId, affectedEndpointIds)  // §9.6
  emit campaign.activation_completed
```

If step 1 resolves an empty delivery set or step 2 fails, the transition is rejected with a structured 422 (§9.9) and the campaign remains Ready. There is no partial activation: either every booked zone has a resolved asset plan and sync records exist for every target endpoint, or nothing changed.

The same pipeline re-runs (delta-only) on mid-flight changes that alter the delivery set or asset plan while Active: creative re-assignment on a line item, and booking changes surviving the booking-protection lock (clear-first resolution, §3/§4 — entities carrying active/future bookings reject edits with `409 BOOKINGS_EXIST`).

### 9.2 Step 1 — Targeting Resolution

Targeting resolves to a concrete set of `(endpointId, zoneId)` keys — the same identity that keys `inventoryUnits`, `timeBudgets`, and `sovCalendars` (§3).

The resolver computes the **union** of two inputs, then partitions it:

1. **Explicit zone bookings** — every booking row on the campaign's line items, read from `timeBudgets.bookings[]`. These are authoritative: a booking holds SOV share and is always delivered to.
2. **KVP-rule matches** — for line items targeted by KVP rules, the rules are re-evaluated at activation time against each provisioned unit's **effective KVP set** (site ∪ endpoint ∪ channel ∪ zone-local; most-specific tier wins — §6). This catches drift since search/booking time (retagged zones, newly provisioned inventory).

Partition of the union:

| Partition | Condition | Treatment |
|---|---|---|
| **Deliverable** | Zone has a booking (whether or not it still matches the KVP rules) | Included in the delivery set. Bookings are the source of truth for where a campaign plays. |
| **Drift — booked, no longer matching** | Booking exists but the zone's current effective KVPs no longer satisfy the line item's rules | Still delivered (the booking holds). Emit `campaign.targeting_drift` with direction `booked_not_matching`; surfaced in the campaign detail view (§8). |
| **Drift — matching, not booked** | Effective KVPs match the rules but no booking exists (e.g., inventory provisioned after the flight was sold — §4 backfill) | **Not delivered** — playing without a booking would corrupt the SOV ledger. Emit `campaign.targeting_drift` with direction `matching_not_booked`; the resolution path is a new booking through the normal engine, never a silent add. |

Output: `deliverySet: Array<{ endpointId, zoneId, lineItemId, bookingId }>`, grouped by `endpointId` for sync dispatch. An empty deliverable set rejects the activation (`422 EMPTY_DELIVERY_SET`, §9.9).

### 9.3 Step 2 — Per-Zone Asset Selection

One campaign carries many creative assets; each zone in the delivery set must receive exactly the assets that fit it. Selection is two gates applied in order — a **spec match** (hard eligibility) then a **tag join** (content differentiation) — followed by a deterministic tie-break.

**Gate A — Spec match (hard):** an asset is eligible for a zone only if all hold:

- **Geometry:** the asset's aspect ratio matches the zone's aspect ratio derived from the zone's layout geometry (`w/h` from the zone record; tolerance ±2% to absorb rounding), and asset resolution ≥ zone pixel dimensions is preferred (below-resolution assets are eligible with a `sync.asset_below_resolution` warning, not blocked — v1 policy).
- **Duration:** `asset.durationSeconds === lineItem.adDuration` for video; images/HTML5 inherit `adDuration` as display duration.
- **Format:** asset type (`video | image | html5`) is supported by the endpoint's `MediaPlayerType`.

**Gate B — Tag join (content differentiation):** assets carry typed KVP tags via the unified `TagEntity` system (`TagModel.ASSET`, §6); zones carry zone-local tags (`TagModel.ZONE`, §6). For every tag key present on **both** the asset and the zone's zone-local tag set, the values must match. Keys present on only one side do not constrain. An asset with no differentiating tags is therefore eligible for every spec-matching zone.

This is a join, not a translation — the single tag schema on both sides (§6) is what makes it one.

**Canonical case (AMD/NVIDIA):** a GPU-aisle endpoint has one channel whose layout splits the screen into two zones: zone A tagged `brand_content = 'AMD'`, zone B tagged `brand_content = 'NVIDIA'` (zone-local tags on the same endpoint — §6). The campaign carries both assets: the AMD creative tagged `brand_content = 'AMD'` and the NVIDIA creative tagged `brand_content = 'NVIDIA'`. Gate B routes each asset to exactly the zone whose zone-local tag matches. One campaign, one endpoint, two zones, two correctly differentiated assets.

**Tie-break (deterministic):** if multiple assets survive both gates for one zone: (1) most matched tag keys wins; (2) then the line item's explicit asset assignment order; (3) then earliest `createdAt`. All selected assets for a zone are synced (multiple eligible assets rotate at runtime per the waterfall's creative rotation — §5/Phase 2); the tie-break orders them.

**Failure:** any zone in the delivery set resolving **zero** assets after Gate A aborts activation atomically (`422 ASSET_RESOLUTION_FAILED`, listing the failing zones and the gate that eliminated each candidate). Note the Ready gate (Phase 3 wizard validation) should make this unreachable; activation re-validates because zones and tags can change between Ready and Active.

**Rule-triggered line items** (`creativeSelectionMode === 'rule_triggered'`): Gates A–B select the *variant pool per zone*; the per-playback variant choice remains endpoint-local per Phase 4 §4.2. The sync payload carries the pre-parsed variant ASTs per Phase 4 §4.1 — this section does not re-specify that contract.

Output: `assetPlan: Array<{ endpointId, zoneId, lineItemId, bookingId, assets: OrderedAsset[] }>`.

### 9.4 Step 3 — Content-Sync Push

Delivery rides the **existing Cue distribution channel** — the same server→endpoint path that delivers `MEDIA_PLAYER_CONFIG` messages today — with one new message type. No new transport is built.

```ts
interface CampaignContentSyncMessage {
  messageType: 'CAMPAIGN_CONTENT_SYNC';        // MEDIA_PLAYER_CONFIG-style envelope
  syncId: string;                              // idempotency key; one per (campaignId, endpointId, revision)
  operation: 'upsert' | 'remove';
  retailerId: string;
  campaignId: string;
  endpointId: string;
  revision: number;                            // monotonic per (campaignId, endpointId); endpoint
                                               // discards messages with revision <= last applied
  zones: {
    zoneId: string;
    lineItemId: string;
    bookingId: string;
    flightStart: string;                       // ISO date — endpoint refuses to play outside flight
    flightEnd: string;
    assets: {
      assetId: string;
      creativeId: string;
      type: 'video' | 'image' | 'html5';
      durationSeconds: number;
      contentUrl: string;                      // CDN URL; endpoint downloads + caches
      checksum: string;                        // sha256 — verified after download
      widthPx: number;
      heightPx: number;
      order: number;                           // rotation order from §9.3 tie-break
    }[];
    ruleTriggered: RuleTriggeredCampaignSync | null;  // Phase 4 §4.1 payload verbatim —
                                                      // variants + pre-parsed KVP ASTs + fallback.
                                                      // null for standard line items.
  }[];
  issuedAt: string;                            // ISO datetime
}
```

Contract rules:

- `operation: 'remove'` carries `zones: [{ zoneId }]` only (no assets) and instructs the endpoint to evict the campaign's cached assets for those zones and drop it from local eligibility.
- The message is **idempotent**: re-delivery of the same `syncId` is a no-op on the endpoint; a higher `revision` fully replaces the prior state for that `(campaignId, endpointId)`.
- The endpoint acks with a delivery receipt (`syncId`, applied revision, per-asset cache result) on the same channel; the ack drives the `SyncStatus` transition (§9.5). Asset download failure (checksum mismatch, CDN error) acks as failed with per-asset detail.
- **Pull fallback:** endpoints also pull pending syncs on boot and on their regular sync interval via `GET /v2/endpoints/:endpointId/pending-syncs` (§9.10) — the same boot-replay pattern as Phase 4 §4.6. Push is an optimization; the pull is the guarantee.

### 9.5 Step 4 — SyncStatus Records, Retry & the Durable Queue

**Collection:** `syncStatuses` (new; supplements the §3 entity set). One record per `(campaignId, endpointId, revision)`.

```ts
interface SyncStatus {
  _id: string;
  retailerId: string;
  campaignId: string;
  endpointId: string;
  syncId: string;
  revision: number;
  operation: 'upsert' | 'remove';
  status: 'pending' | 'delivered' | 'failed';
  attempts: number;
  lastAttemptAt: Date | null;
  deliveredAt: Date | null;
  failureReason: string | null;        // 'endpoint_offline' | 'checksum_mismatch' | 'download_failed' | ...
  payloadHash: string;                 // sha256 of the message body — idempotent re-dispatch
  version: number;                     // optimistic lock; conflicting transition → 409 STALE_WRITE
  createdAt: Date;
  updatedAt: Date;
}
```

**Indexes:** `{ retailerId: 1, campaignId: 1, status: 1 }` (support query); `{ endpointId: 1, status: 1 }` (pull fallback); `{ syncId: 1 }` unique.

**Lifecycle:**

| Transition | Trigger |
|---|---|
| — → `pending` | Pipeline step 3 writes the record and enqueues the `content-sync` job |
| `pending` → `delivered` | Delivery receipt ack from the endpoint (push or pull path) with all assets cached |
| `pending` → `failed` | Push attempts exhausted (see backoff) or ack reports unrecoverable per-asset failure |
| `failed` → `pending` | Endpoint check-in claims it via pull, or support triggers manual retry (§9.10) |

**Retry with backoff (push path):** the `content-sync` job on the Concourse queue is durable — it survives worker restarts and is retried on schedule 1m → 5m → 15m → 1h → then hourly up to 24h (max 28 attempts). After exhaustion the record flips to `failed` and `sync.failed` fires. `failed` is **not terminal**: an offline endpoint that comes back retries on its next sync interval via the pull fallback and completes the delivery — `failed` means "needs endpoint check-in or support attention," and the pull path self-heals it. Duplicate jobs for the same `syncId` coalesce; `payloadHash` makes re-dispatch idempotent end to end.

**The gating rule (restated because it is the point):** a campaign **cannot play** on an endpoint whose `SyncStatus` for the current revision is not `delivered`. The waterfall (§5/Phase 2) skips that endpoint's zones for this campaign; the booked SOV share goes to lower-priority candidates or P4 filler for those loops. Under-delivery caused by sync lag is visible in pacing and is compensated by the pacing nudge once delivery lands — it is never hidden.

### 9.6 Step 5 — Waterfall Hot-Cache Invalidation

The decide-path hot cache (Phase 2) holds each endpoint's candidate campaign set. Activation invalidates it twice:

1. **On activation commit** (pipeline step 5): the campaign enters the candidate pool for all affected endpoints, each gated `deliverable: false` until its `SyncStatus` is `delivered`.
2. **On each delivery ack**: the `(campaignId, endpointId)` gate flips to `deliverable: true` — endpoints join the campaign's waterfall incrementally as their syncs land, rather than waiting for the slowest endpoint.

Cancellation, completion, pause, and resume (§9.7) each invalidate the same cache. Invalidation is keyed to affected endpointIds only — never a retailer-wide flush. A failed invalidation is retried by the queue job; the cache also carries a TTL backstop (Phase 2 setting) so staleness is bounded even on total invalidation failure.

### 9.7 Cancellation, Completion & Pause Semantics

| Transition | Content sync | Bookings / SOV | Waterfall |
|---|---|---|---|
| **Active → Cancelled** | `remove` sync to every delivered endpoint (new revision; same SyncStatus machinery, §9.5) | All bookings with `flightEnd >= today` are **released** on their `timeBudgets`, which enqueues `sov-recalc` for every affected `(endpointId, zoneId)` (§5) — the freed share reappears in the availability calendar and inventory search (§7) after recompute | Immediate hot-cache eviction — the campaign stops winning slots **before** removal syncs deliver; an offline endpoint that plays stale content until its next pull has its proof-of-play flagged `post_cancellation` and excluded from billing aggregates |
| **Active → Completed** (all flights ended) | Daily completion sweep enqueues `remove` syncs to evict cached assets | No release needed — past bookings hold no future share by construction (time-windowed ledger, §3/D8) and never lock (booking-protection lock applies to `flightEnd >= today` only); no `sov-recalc` required | Cache eviction; endpoints additionally self-enforce `flightEnd` from the sync payload, so a missed sweep cannot cause post-flight play |
| **Active → Paused** | **No sync.** Assets stay cached on endpoints | Bookings **keep their SOV hold** — pause is a runtime stop, not a booking release; availability calendars are unchanged and no `sov-recalc` fires. The flight clock keeps running: paused days still consume the flight window and count against guarantee feasibility (the §8 campaign view must warn on this; policy per Phase 2 guarantee math) | Hot-cache invalidation excludes the campaign from candidacy on all endpoints |
| **Paused → Active (resume)** | **No re-sync needed** — content is still cached; the pipeline verifies current-revision `SyncStatus === 'delivered'` per endpoint and re-dispatches only stale ones (e.g., re-provisioned endpoints) | Unchanged | Hot-cache invalidation restores candidacy on delivered endpoints |

Cancelling a campaign that is mid-activation (syncs still `pending`) supersedes those syncs: pending `upsert` jobs for the campaign are cancelled on the queue, and `remove` is dispatched only to endpoints that already acked delivery.

### 9.8 Activation SLA & Observability

**SLA: < 4 hours from Ready → Active to the campaign's first proof-of-play** (network-wide, first play on any delivered endpoint), given at least one target endpoint online. Budget decomposition:

| Stage | Budget | Observed via |
|---|---|---|
| Pipeline steps 1–5 (resolve, select, dispatch, cache) | < 5 min | `campaign.activation_completed` − `campaign.activation_started` |
| Sync delivery to first endpoint | < 60 min (one default endpoint sync interval; push usually lands in seconds) | first `sync.delivered` |
| First loop win + play | remainder (pacing-dependent) | `campaign.first_proof_of_play` |

SyncStatus is what makes the SLA **observable rather than asserted**: at any moment, `GET .../sync-status` (§9.10) answers "how many endpoints have this campaign's content, which are pending, which failed and why." The §8 campaign detail view renders this as a delivery progress strip (delivered / pending / failed counts with per-endpoint drill-down); the sellability funnel (§8) is the pre-activation analogue.

**Alerts** (delivered via the Phase 4 §8 alert machinery):

- `campaign.sync_lagging` — Active > 2h with < 90% of target endpoints `delivered`.
- `campaign.activation_sla_breached` — Active > 4h with zero proof-of-play. Includes the current sync-status breakdown so the on-call sees immediately whether the cause is delivery (failed syncs) or runtime (delivered but not winning loops).

### 9.9 Failure Modes

| # | Failure | Detection | Behavior | Resolution path |
|---|---|---|---|---|
| 1 | Targeting resolves empty deliverable set | Pipeline step 1 | Activation rejected, `422 EMPTY_DELIVERY_SET`; campaign stays Ready | Fix bookings/targeting; typically indicates released bookings or retired inventory (§4) |
| 2 | Zone resolves zero spec-matching assets | Pipeline step 2 | Activation rejected atomically, `422 ASSET_RESOLUTION_FAILED` + per-zone gate detail | Upload/assign a conforming asset or clear the zone booking (booking-protection clear-first) |
| 3 | Endpoint offline at dispatch | Push timeout | `SyncStatus` stays `pending` through backoff; `failed` after exhaustion; **pull fallback recovers on next endpoint check-in**; waterfall skips the endpoint meanwhile | Self-healing; support surfaces via §9.10 if the endpoint never returns |
| 4 | Asset download fails on endpoint (CDN error, checksum mismatch) | Failed ack with per-asset detail | `SyncStatus` → `failed`, `failureReason` set; endpoint retains prior state (revision not applied) | Retry job re-dispatches; persistent checksum mismatch → re-upload asset, new revision |
| 5 | Partial estate delivery at `flightStart` | Sync-status counts | Delivered endpoints play; pending endpoints skipped; pacing nudge compensates post-delivery; `campaign.sync_lagging` alert at threshold | Self-healing + alert |
| 6 | Removal sync undeliverable at cancellation | `remove` SyncStatus `pending`/`failed` | SOV already released (release never waits on delivery); offline endpoint self-enforces `flightEnd`; post-cancellation plays flagged and excluded from billing | Pull fallback evicts on next check-in |
| 7 | Hot-cache invalidation fails | Queue job error | Retried; TTL backstop bounds staleness; worst case = short over-inclusion (campaign gated by SyncStatus anyway) or under-inclusion (missed loops, pacing compensates) | Self-healing |
| 8 | Concurrent status transition (double-activate, cancel-during-activate) | Optimistic version lock on campaign | Loser gets `409 STALE_WRITE` (existing Phase 3 §4.2 treatment) | Client refetch + retry |
| 9 | Structural edit attempted on delivering campaign's inventory | Booking-protection lock (§3/§4) | `409 BOOKINGS_EXIST` with blocking bookings listed; v1 resolution is clear-first | Clear bookings, then edit; move/rebook is post-v1 |
| 10 | KVP targeting drift (both directions) | Activation-time re-evaluation (§9.2) | Delivered set follows bookings; drift emitted as telemetry + shown in §8 | Manual: rebook or retag; never auto-mutated |

### 9.10 Routes / API Additions

| Method | Path | Purpose |
|---|---|---|
| `PUT` | `/v2/retailers/:retailerId/campaigns/:campaignId/status` | Existing transition endpoint — the Ready → Active handler now runs the §9.1 pipeline; Cancelled/Completed/Paused run §9.7. No new activation route. |
| `GET` | `/v2/retailers/:retailerId/campaigns/:campaignId/sync-status` | Per-endpoint `SyncStatus` list; filters `status`, `endpointId`; paginated. The support/observability query behind the §8 delivery strip. |
| `POST` | `/v2/retailers/:retailerId/campaigns/:campaignId/sync-status/retry` | Support tool: re-enqueue `content-sync` for `failed` (or all non-delivered) records; body `{ endpointIds?: string[] }`. Idempotent via `payloadHash`. |
| `GET` | `/v2/endpoints/:endpointId/pending-syncs` | Endpoint pull fallback: all non-delivered `CampaignContentSyncMessage`s for this endpoint, current revisions only. Called on boot and each sync interval (same pattern as Phase 4 §4.6). |

All retailer routes tenant-scoped and Cerbos-checked per the established conventions; the endpoint route authenticates with the existing Cue device credential.

### 9.11 Telemetry & Metrics

**Events** (entity.action form):

- `campaign.activation_started`, `campaign.activation_completed`, `campaign.activation_failed` (with rejection code)
- `campaign.targeting_resolved` (deliverable count, drift counts by direction), `campaign.targeting_drift`
- `campaign.asset_resolution_failed` (zones + eliminating gate)
- `sync.dispatched`, `sync.delivered`, `sync.failed`, `sync.retried`, `sync.removal_dispatched`
- `sync.asset_below_resolution` (warning path, §9.3 Gate A)
- `campaign.first_proof_of_play` (carries Ready→play elapsed — the SLA measurement)
- `campaign.sync_lagging`, `campaign.activation_sla_breached`
- `campaign.paused`, `campaign.resumed`, `campaign.cancelled`, `campaign.completed`
- `booking.released` (cancellation path — the §5 `sov-recalc` trigger)
- `waterfall.cache_invalidated` (reason, endpoint count)

**Metrics (dashboards/alerting):**

- Activation pipeline duration p50/p99 (budget: < 5 min p99)
- Sync delivery latency p50/p99 (dispatch → delivered), split push vs pull-recovered
- % target endpoints `delivered` at activation +1h / +4h
- Ready → first proof-of-play hours (SLA distribution)
- `failed` SyncStatus count by `failureReason` (steady state ≈ offline-endpoint count)
- Targeting drift counts by direction (provisioning-health signal — feeds the §8 funnel)
- Post-cancellation flagged plays (should trend to zero within one pull interval)

### 9.12 Required Tests

- **AMD/NVIDIA routing:** a campaign carrying two assets (`brand_content='AMD'`, `brand_content='NVIDIA'`) booked on a 2-zone endpoint whose zones carry the matching zone-local tags (§6) activates with each zone's sync payload containing exactly the tag-matching asset — asserted per `(endpointId, zoneId)` in the `CampaignContentSyncMessage`.
- **Offline endpoint joins late:** activate with one endpoint offline — its `SyncStatus` walks `pending` → `failed` through backoff; decide-path never awards it a slot; endpoint comes online, pulls `/pending-syncs`, acks, `SyncStatus` → `delivered`, hot-cache gate flips, and the endpoint wins loops **only after** delivery.
- **Cancellation frees SOV:** cancel an Active campaign — `remove` syncs dispatch to all delivered endpoints, bookings with `flightEnd >= today` are released, `sov-recalc` jobs enqueue on the Concourse queue for exactly the affected `(endpointId, zoneId)` keys, and the recomputed `sovCalendars` show the freed share (subsequent §7 search returns it as available).
- Activation aborts atomically with `422 ASSET_RESOLUTION_FAILED` when any booked zone has no spec-matching asset (wrong aspect / wrong duration / unsupported type each covered); no `SyncStatus` records are written.
- Empty deliverable set rejects with `422 EMPTY_DELIVERY_SET`; campaign remains Ready.
- Rule-triggered line item: sync payload embeds the Phase 4 §4.1 `RuleTriggeredCampaignSync` (variants + pre-parsed ASTs + fallback) unchanged; standard line items carry `ruleTriggered: null`.
- Targeting drift both directions: booked-not-matching zone still delivered + drift event; matching-not-booked zone excluded + drift event; neither mutates bookings.
- Idempotency: duplicate `content-sync` jobs for one `syncId` coalesce; endpoint re-ack of an applied revision is a no-op; replayed `upsert` after delivery does not reset `deliveredAt`.
- Revision ordering: endpoint discards a lower-revision message arriving after a higher one.
- Pause: no sync dispatched, assets remain cached, hot cache excludes the campaign, bookings and `sovCalendars` unchanged (no `sov-recalc`); resume restores candidacy without re-sync when revisions are current.
- Partial delivery: with 3 target endpoints (2 delivered, 1 pending), decide awards slots only on the delivered pair.
- Removal to an offline endpoint: SOV release and `sov-recalc` proceed immediately; the endpoint's post-cancellation proof-of-play is flagged `post_cancellation` and excluded from billing aggregates; pull-driven eviction lands on next check-in.
- Concurrent cancel-during-activate: pending `upsert` jobs superseded, `remove` dispatched only to acked endpoints, loser transition gets `409 STALE_WRITE`.
- Support retry: `POST .../sync-status/retry` re-enqueues only non-delivered records and is idempotent via `payloadHash`.

---

## 10. Acceptance Criteria, Test Plan & Sequencing

### 10.1 Acceptance Criteria — This PRD Is Done When

Every criterion below is testable and maps to a spec section (§3–§9). All must pass before this PRD is considered delivered. Numbers in parentheses are the owning section.

**Data model (§3)**

1. `inventoryUnits`, `timeBudgets`, and `sovCalendars` collections exist with the schemas, validation, and indexes in §3, and every document is keyed on `(endpointId, zoneId)` with a unique compound index. (§3)
2. `timeBudgets.bookings[]` carry `flightStart`/`flightEnd`; no scalar `totalShareBooked`/`availableShare` field remains in the schema (D8). Availability for any window is computable as 100% − max concurrent booked share over the interval. (§3)
3. `loopDuration` lives at the endpoint level only — no per-zone loop-duration field exists anywhere in the schema. Retailer defaults live in the SSP waterfall config, and changing a default does not mutate any endpoint carrying active bookings. (§3, §4)
4. Every collection carrying bookings enforces the booking-protection lock invariant: no write path can modify or delete an entity that carries a booking with `flightEnd >= today` without going through the clear-first resolution (§3.7); violations return `409 BOOKINGS_EXIST` with the blocking bookings enumerated in `details`.

**Provisioning service (§4)**

5. The derivation rule in §4.2 materializes exactly one `InventoryUnit` + one `TimeBudget` per `(endpointId, zoneId)` for every active endpoint with an assigned channel, and re-running derivation is idempotent (upsert, zero duplicates). (§4)
6. All lifecycle events in §4.4 (channel assigned/unassigned, layout attached/changed, zone added/edited/removed, endpoint retired, sellable toggled) produce the specified upsert/deactivate side effects within the propagation SLA defined in §4.9. (§4)
7. SSP package activation triggers the backfill: `POST /v2/retailers/:retailerId/inventory/provisioning/sync` materializes units + time budgets for the retailer's entire configured footprint, initializes each unit's `sovCalendars` at 100% available, and registers each zone's existing playlist schedules as that zone's P4 filler pool. `GET /v2/retailers/:retailerId/inventory/provisioning/status` reports the run's progress and per-stage counts. (§4)
8. The invariant checks in §4.6 hold post-backfill: Σ zoneWeight ≤ 1.0 per layout; `(endpointId, zoneId)` uniqueness; no `InventoryUnit` is searchable without its `TimeBudget`.

**Availability calendar & recalc pipeline (§5)**

9. `sovCalendars` is a derived view: the full-rebuild admin job reconstructs every calendar from `timeBudgets.bookings[]` alone, byte-identical to the incrementally maintained state. (§5)
10. Every booking-affecting trigger in §5.4 enqueues a `sov-recalc` job on the Concourse queue keyed to the affected `(endpointId, zoneId)` units only; duplicate keys within the coalescing window collapse to one recompute. (§5)
11. Booking commits validate transactionally against `timeBudgets.bookings[]` with the optimistic version lock — never against the calendar. A stale calendar read followed by a conflicting commit surfaces as `409 OVERBOOKING` (Phase 3 §4.2 treatment), and a concurrent-write conflict surfaces as `409 STALE_WRITE`. (§5)

**Unified KVP tags (§6)**

12. `TagModel` includes `ZONE` and `ASSET`; zone-local tags assign and reverse-lookup through the extended `/v1/retailers/tags/*` surface. (§6)
13. Effective-KVP resolution returns site ∪ endpoint ∪ channel ∪ zone-local for every provisioned unit, with the most specific tier winning on key collision (zone > channel > endpoint > site). The static contract keys (`store_id`, `region`, `store_tier`, `zone_type`, `endpoint_type`, `screen_orientation`) resolve for 100% of provisioned units. (§6)
14. The legacy playlist-asset tag endpoints are migrated (or adaptered with a deprecation window) onto the unified `TagEntity` surface; no third tag schema exists. (§6)

**Search contract (§7)**

15. `POST /v2/retailers/:retailerId/inventory/search` accepts the v2 layered contract (site scope → kvpRules → flight date range → adDuration) and returns per-zone remaining SOV over the window, read from `sovCalendars`. The FE `as never` cast is gone; the SDK is regenerated and pinned. (§7)
16. Plays, guaranteed plays, impressions, and rate per search row are server-computed from the day buckets + `loopsPerDay` + rate card + traffic; no FE-side metric constants remain in the Campaign Builder. (§7)

**Admin UI (§8)**

17. The endpoint→channel picker, channel add/detail with layout/zone editor, `/signages/layouts`, and Tag Manager run against generated SDK hooks — zero `setTimeout` saves, zero hardcoded `channelsList = []`, and the two malformed tag-assign calls (gap analysis §4.1) are fixed. (§8)
18. The channel detail view is mode-adaptive per the retailer-wide SSP switch: Cue mode renders the schedule calendar; SSP mode renders the SOV ledger view (loop config read-only at zone level, booked vs. available share, bookings list, P4 filler source). (§8)
19. Zones carrying active bookings render the locked state: edit/delete disabled, blocking campaigns listed, clear-bookings resolution path offered. (§8)
20. The Inventory Dashboard sellability funnel renders all five stages (endpoints without channel → channels without layout/zones → zones without rate cards → zones without traffic → sellable units) with each stage linking to its fix surface. A retailer with 0 sellable units can diagnose why without engineering. (§8)

**Activation side effects (§9)**

21. Ready→Active resolves the campaign's targeting to the concrete endpoint set, routes per-zone creative assignments by matching asset tags to zone-local tags, pushes via Cue content sync, invalidates the waterfall hot cache, and records per-endpoint sync status with retry. (§9)
22. Campaign cancellation sends removal sync, releases booked SOV, and enqueues `sov-recalc` for every affected unit. (§9)
23. The end-to-end smoke script in §10.2.4 passes in staging against a real (non-seeded) backfilled estate.

### 10.2 Test Plan

#### 10.2.1 Unit tests (pure functions, no I/O)

| Area | Required tests |
|---|---|
| **Interval math (§3, §5)** | max-concurrent-booked-share over: disjoint flights (sum never applied); fully nested flights; partial overlaps; single-day flights; flight boundaries meeting exactly (end = start, no phantom overlap); empty bookings → 100% available; 100%-cap rejection at exact boundary (60% + 40% ok, 60% + 41% rejected on overlap days only) |
| **Step-function recompute (§5)** | booking add/remove changes only the day buckets inside its flight; recompute is idempotent (run twice = same document); recompute from bookings[] alone reproduces incrementally maintained state; month-boundary flights write both month documents; tombstone on unit retirement |
| **Effective-KVP resolution (§6)** | 4-tier union with no collisions; zone > channel > endpoint > site precedence on collision; zone-local additive tags differentiate two zones on one endpoint; static contract keys resolve from mixed sources (entity-derived + tag-derived); missing tier degrades gracefully (endpoint with no channel-level tags) |
| **Derivation rule (§4)** | endpoint + channel + layout + N zones → N units; endpoint without channel → 0 units; inactive endpoint skipped; slot type mapping by `MediaPlayerType`; Σ zoneWeight > 1.0 rejected |
| **Booking-protection lock predicate (§4)** | booking with `flightEnd >= today` locks; `flightEnd < today` does not; multiple bookings → all enumerated in `details`; lock evaluated per entity tier (zone, layout, channel assignment, endpoint, loop config) |

#### 10.2.2 Integration tests (API + DB + queue)

| Area | Required tests |
|---|---|
| **Provisioning backfill (§4)** | seed Cue chain → `POST .../provisioning/sync` → unit/timeBudget/calendar counts match footprint; re-run is a no-op (idempotent); partial failure resumes without duplicates; `GET .../provisioning/status` reflects each stage; P4 filler registration recorded per zone |
| **Lifecycle events (§4)** | zone added to booked layout → new unit provisioned, siblings untouched; channel unassigned from endpoint with no bookings → units deactivated; endpoint retired → calendars tombstoned |
| **Lock enforcement (§4)** | zone edit with active booking → `409 BOOKINGS_EXIST` with blocking campaigns in `details`; same edit after clear-first → 200; past-only bookings → edit allowed; layout swap, channel unassign, endpoint retire, and loop-config change all covered by the same matrix |
| **Queue coalescing (§5)** | N bookings on one unit inside the coalescing window → one `sov-recalc` execution; campaignId payload expands to all booked units; takeover trigger fans out to every zone at affected stores as a batch; failed job retries with backoff and lands eventually; recalc during concurrent booking commit never blocks the commit |
| **Commit-path authority (§5)** | force-stale a calendar, attempt overlapping commit → `409 OVERBOOKING`; concurrent commits on one timeBudget → one wins, other gets `409 STALE_WRITE`; committed booking never exceeds 100% concurrent share regardless of calendar state |
| **Tag APIs (§6)** | assign/lookup with `TagModel.ZONE` and `TagModel.ASSET`; reverse lookup returns units by zone-local tag; migrated asset-tag surface parity with legacy endpoints |

#### 10.2.3 Contract tests (schema pinned)

- `POST /v2/retailers/:retailerId/inventory/search` request and response schemas pinned against SDK 5.11+ generated types; CI fails on drift. Covers: `siteIds[]` vs `allSites: true` exclusivity; `kvpRules` grammar acceptance; date-range validation; response row shape (remaining SOV, plays, guaranteed plays, impressions, rate) exact-matched.
- `GET /v2/retailers/inventory/:endpointId/:zoneId/calendar?from=&to=` response shape pinned (day buckets, `loopsPerDay`, `version`, `recomputedAt`).
- Provisioning sync/status routes pinned.
- Error envelope contract: `BOOKINGS_EXIST`, `OVERBOOKING`, `STALE_WRITE` each carry the structured `details` payload the FE locked/conflict treatments consume (§8, Phase 3 §4.2).
- The `as never` cast is a lint-blocked pattern in the FE from this build forward.

#### 10.2.4 End-to-end smoke (staging, run as one scripted scenario)

This is THE acceptance gate. It must run green on a clean staging environment with no inventory seeds.

1. **Seed a Cue estate:** create 2 sites, 3 endpoints (2 at site A, 1 at site B), 1 channel assigned to all 3 endpoints, 1 layout with 2 zones attached to the channel, zone-local tags `brand_content='AMD'` on zone 1 and `brand_content='NVIDIA'` on zone 2, site/endpoint tags for `region` and `store_tier`, and existing playlist schedules on both zones.
2. **Activate the SSP package** for the retailer.
3. **Verify backfill:** `GET .../provisioning/status` completes; exactly 6 `inventoryUnits` (3 endpoints × 2 zones) + 6 `timeBudgets` exist; 6 `sovCalendars` show 100% available across the horizon; both zones' playlists are registered as P4 filler.
4. **Run layered search:** `POST .../inventory/search` with `allSites: true`, `kvpRules: [brand_content='AMD']`, a 30-day flight range, and a 15s adDuration → returns exactly the 3 AMD-zone units with 100% remaining SOV and server-computed plays/guarantees/impressions/rates.
5. **Book share on 2 zones:** commit 40% SOV bookings on 2 of the returned units for the flight window.
6. **Verify calendar recalc:** a `sov-recalc` job runs on the Concourse queue for exactly those 2 unit keys; `GET .../calendar` on each shows 60% available inside the flight, 100% outside; re-running the search shows 60% remaining on those units.
7. **Attempt a zone edit** on a booked zone → `409 BOOKINGS_EXIST` with the booking campaign in `details`; the admin UI renders the locked state.
8. **Activate the campaign** (Ready→Active).
9. **Verify per-zone asset routing:** the AMD creative variant is assigned to the AMD-tagged zones and the NVIDIA variant to the NVIDIA-tagged zones (asset tag ↔ zone tag join); per-endpoint sync status reaches `synced` for all targeted endpoints.
10. **Verify decide:** the decide endpoint for a booked zone returns the campaign at its booked priority; an unbooked zone at the same store returns P4 filler.
11. **Verify proof-of-play:** playback records roll up per (campaign, zone).
12. **Cancel the campaign:** booked SOV released; `sov-recalc` restores the calendars to 100%; removal sync issued and assets removed from endpoints; search shows full availability again.

**Smoke telemetry assertions** (events must fire in `entity.action` form): `inventory.provisioned`, `inventory.backfill_completed`, `inventory.searched`, `booking.created`, `calendar.recalculated`, `entity.lock_rejected`, `campaign.activated`, `endpoint.sync_completed`, `booking.released`, `campaign.cancelled`.

### 10.3 Sequencing

Adapted from the gap analysis §5 sequencing; decisions D1–D9 are already locked (§2), so the plan starts at documentation.

| Order | Item | Spec | Depends on | Notes |
|---|---|---|---|---|
| 0 | Decisions D1–D9 + backend confirmations #1–#2 | §2 | — | ✅ Done (2026-07-16). zoneId stability and one-clock-per-endpoint are confirmed inputs, not open questions. |
| 1 | This PRD ratified + source-PRD amendments (§19 hierarchy correction, Program/ProgramInventory deprecation notice) | §1, §2 | 0 | Cheap; lands while build 2 is in design. |
| 2 | **Provisioning service + backfill + SOV calendar + recalc pipeline** | §3, §4, §5 | 1 | One build — the time-windowed schema (D8) and calendar (D9) land together; splitting them would ship a scalar ledger that must immediately be rewritten. Unblocks QA on real data. |
| 3 | Admin UI wiring + SSP-mode views + locked states | §8 | none — **parallel with 2** | FE hook wiring needs no new backend; SSP ledger panel and funnel consume build-2 endpoints as they land. |
| 4 | Inventory search contract + FE integration | §7 | 2 | Kills the `as never`; requires calendars to have data worth returning. |
| 5 | Unified KVP tag architecture (`ZONE`/`ASSET`, effective-KVP resolver, asset-tag migration) | §6 | 2 (resolver reads provisioned units) | Search's kvpRules dimension is functional-but-thin until this lands; sequence 4 → 5 is acceptable because site-scope + date-range search is independently shippable. |
| 6 | Sellability funnel | §8.4 | 2 | Read-only aggregation over provisioning output. |
| 7 | Activation side effects + creative routing + sync status | §9 | 2, 5 | Needs zone-local tags for the asset↔zone join; overlaps Phase 4 rule-evaluator channel to Cue endpoint runtime. |
| 8 | E2E smoke (§10.2.4) green in staging | §10 | 2–7 | The release gate. |

**Dependency notes:**

- Build 2 is the critical path; everything else either parallels it (3) or consumes it (4–7).
- Builds 4 and 5 share the SDK regeneration; coordinate one SDK release covering both to avoid double FE churn.
- Build 7's endpoint-runtime work goes through the same Cue engineering channel as the Phase 4 rule evaluator — schedule jointly.

### 10.4 Migration & Rollout Notes

1. **Staging seeds retire when backfill lands.** The digital-inventory seed data that currently props up QA is deleted in the same release that ships build 2's backfill. From that release forward, staging inventory is materialized exclusively by `POST .../inventory/provisioning/sync` against a seeded *Cue* estate (sites/endpoints/channels/zones — which remain legitimate test fixtures). No environment may carry both seeded and provisioned `inventoryUnits`.
2. **Legacy Program/ProgramInventory system is explicitly deprecated.** `POST /v1/retailers/{retailer}/programs/inventory/search` and the `ProgramPlayStats` surface are marked deprecated in the same PRD amendment (sequence 1), return a `Deprecation` header immediately, and are removed after one release cycle with zero recorded callers. The platform ships with exactly one inventory system.
3. **Backfill is safe to re-run.** Derivation is upsert-idempotent (§4.2) and calendars are rebuildable (§5.2); the rollback story for a bad backfill is "fix, re-run sync, full-rebuild calendars" — never manual document surgery.
4. **Rollout order per retailer:** SSP package activation is the retailer-wide switch and the backfill trigger (D7). Enable one pilot retailer in production, run the §10.2.4 smoke against it, then open activation generally. Retailers without the SSP package see zero behavior change.
5. **No mixed estates in v1.** The per-zone `sellable` flag stays in the schema (D3) but is not surfaced as a mode control; the retailer-wide switch is the only mode boundary.

---

## 11. Glossary

| Term | Definition |
|---|---|
| **Share of voice (SOV)** | The percentage of a zone's sellable loop time booked by a campaign, constant per flight (one % from `flightStart` to `flightEnd`). Canonical term throughout this PRD. **Legacy alias:** earlier PRDs and code say "share of play" — same concept; all amended documents and new code use SOV. |
| **Unit of uniqueness** | `(endpointId, zoneId)` — the identity of a sellable digital inventory unit. One channel serves many endpoints, so the same zone definition yields one sellable unit *per endpoint carrying the channel*. zoneIds are stable for the life of a channel (backend-confirmed), making this key safe for time budgets, bookings, calendars, and rate cards. |
| **Provisioning** | The derivation bridge (§4) from Cue's structural chain (Site → Endpoint → Channel → Layout → Zone) to Deal Desk's sellable collections: for every active endpoint with a channel, for every zone in the channel's layout, upsert one `InventoryUnit` + one `TimeBudget`. Kept current by lifecycle events. |
| **Backfill** | The bulk provisioning run triggered by SSP package activation (`POST /v2/retailers/:retailerId/inventory/provisioning/sync`): materializes units + time budgets for the retailer's entire existing footprint, initializes calendars at 100% available, and registers zone playlists as P4 filler. Idempotent and manually re-triggerable. |
| **sovCalendar** | A document in `sovCalendars`: the precomputed, day-granularity availability view for one `(endpointId, zoneId)` per month (§5). A derived view — always rebuildable from `timeBudgets.bookings[]`, read by search, never consulted by booking commits. |
| **Booking-protection lock** | The invariant that entities carrying active or future bookings (any booking with `flightEnd >= today`) are locked from edit and delete — zone geometry, layout swap/detach, channel unassignment, endpoint retirement, loop config. Enforced at the API layer as `409 BOOKINGS_EXIST` with blocking bookings enumerated. |
| **Effective KVPs** | The resolved tag set for a zone: site ∪ endpoint ∪ channel ∪ zone-local, most specific tier winning on key collision (zone > channel > endpoint > site). Feeds search filtering, the decide-time context bag, the rule builder's pickers, and activation asset routing (§6). |
| **Zone-local tags** | Additive `TagModel.ZONE` tags that differentiate zones on the same endpoint — e.g., a GPU endpoint split into a zone tagged `brand_content='AMD'` and another tagged `brand_content='NVIDIA'`: same endpoint, distinct targetable inventory. |
| **P4 filler pool** | The waterfall's lowest tier in SSP mode. On SSP activation, each zone's existing playlist schedules are registered as that zone's P4 filler — retailer content plays whenever no campaign wins the loop slot, so no zone can go dark. |
| **Concourse queue** | The platform job queue carrying the `sov-recalc` job type: payload of affected unit keys (or a campaignId to expand), duplicate-key coalescing, retry with backoff (§5). |
| **Sync status** | The per-endpoint record of creative delivery at campaign activation (§9): whether the resolved assets and rule ASTs reached each targeted endpoint via Cue content sync, with retry state. Cancellation records removal sync the same way. |
| **Clear-first vs. move/rebook** | The two resolutions for a booking-protection lock. **Clear-first** (v1): release the blocking bookings, then edit/delete. **Move/rebook** (post-v1): migrate bookings to another zone, carrying calendars and rate context, without a release gap. |

---

