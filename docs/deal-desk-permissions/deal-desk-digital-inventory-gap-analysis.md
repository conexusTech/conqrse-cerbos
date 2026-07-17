# Gap Analysis — Digital Inventory Provisioning (Endpoints → Channels → Zones → Sellable Units)

> **Trigger:** Engineering found `inventory/search` returns empty for every retailer — digital `InventoryUnit`s exist only as seeded test data. Campaigns cannot be built end-to-end even where the footprint exists (e.g., "Video MP" = 854 stores / 66 players / 0 sellable digital units).
> **Verdict:** Confirmed spec gap, not a missed build. Additionally: the PRD's structural model conflicts with the intended product model, and the Deal Desk KVP layer is not connected to the platform's existing tag system.
> **Method:** 5-agent research sweep over `prd-deal-desk-v2.md`, `phase-1-prd-backend-foundation.md`, `phase-2-prd-core-engine.md`, the `@conqrse/api-sdk`/`@conqrse/api-types` surface, and the `conqrse-admin` codebase (master, develop, `feat/deal-desk-permissions-v2`, worktrees). All claims below carry file/line evidence from that sweep.
> **Date:** 2026-07-16 · **Author:** Claude (research swarm + Fable synthesis) for Jody Holmes

---

## 1. Executive Summary

The engineer is right, and the gap is wider than "no creation path":

1. **No PRD anywhere specifies how a digital `InventoryUnit` or `TimeBudget` comes into existence.** The source PRD defines them declaratively ("each zone in the layout = an inventory unit"); Phase 1 §3.14 explicitly declares Endpoint/Store/Zone/Layout as **external Cue entities that Deal Desk "references by ID but does not create"**, read via an optional thin `cueAdapter`. No sync, materialization job, or CRUD route for digital inventory exists in any phase PRD. Phase 2's inventory search reads **exclusively** from Deal Desk's own Mongo collections (`inventoryUnits`, `timeBudgets`, `rateCards`, `storeTraffic`) — so with nothing writing those collections, search is empty by construction. Physical inventory got a production path (Blueprint/Onboarding CRUD); digital never did.

2. **The word "channel" appears zero times in the Phase 1 and Phase 2 PRDs**, and the source PRD treats channels as a *Playlist-Mode-only scheduling construct* (its data model attaches Layout → Zones directly to the Endpoint for SSP). Your answer to the engineer — endpoint → **channel** → layout of zones — matches the **actual Cue API**, not the PRD. The PRD needs to be corrected to the channel-centric model, or the discrepancy resolved explicitly.

3. **The good news: most of the chain already exists as API surface.** Cue's SDK has full CRUD for Site → MediaPlayer(endpoint) → Channel (with `layout` ref and `mediaPlayer` ref) → Layout → Zone (first-class entities with stable IDs) → per-zone Schedules, plus a real, typed, retailer-scoped KVP tag system (`TagEntity` + assign + reverse lookup). What's missing is (a) the **bridge** that derives sellable Deal Desk inventory from that chain, (b) **zone-level tags** (TagModel stops at channel), (c) **share-of-play capacity** anywhere in the Cue model, and (d) **activation side effects** that route creative to the resolved endpoints.

4. **The admin UI for the chain exists but is largely disconnected.** On `develop`, the endpoint→channel picker, channel/layout/zone editor, and tag manager are all presentational stubs (`channelsList = []`, `setTimeout` saves, "IMPLEMENT: Replace with BFF SDK hooks" in 51 files). On `master` (production), the tag/channel/schedule pages are wired — but the Deal Desk Campaign Builder that ships there is the `(UIDesignLayout)` mock, which **never queries any inventory API at all**.

---

## 1.5 Confirmed Concept Model (decided with product, 2026-07-16)

One structural chain, two content modes. The chain `Site → Endpoint → Channel → Layout → Zones` exists in **both** modes — SSP removes the *playlist/schedule* layer from zones, not the channel. The channel has two jobs the original PRD conflated: **structure** (carrying the layout of zones — survives in both modes) and **content scheduling** (playlists — Cue mode only).

```
                        Endpoint → Channel → Layout → Zone
                                                        │
        ┌───────────────────────────────────────────────┴──────────────────────────────┐
        │ MODE 1 — Cue (existing)                MODE 2 — Deal Desk / SSP (new)         │
        │ Zone → Schedules → Playlists           Zone → SOV Loop (fixed 120s)           │
        │ Retailer curates content order         Playlist layer removed from the zone   │
        │ Dynamic loop = playlist length         Campaigns book % share of voice        │
        │                                        Waterfall (P1→P4) fills each loop      │
        │                                        iteration; filler takes the remainder  │
        └────────────────────────────────────────────────────────────────────────────────┘
```

Two layers keep SSP mode honest:

1. **Booking layer (sales time):** each zone carries a share-of-voice ledger. Campaigns book a % of it for a date range. Inventory search reads this ledger.
2. **Runtime layer (playback time):** every loop iteration, the waterfall walks P1 → P4 and picks what plays *this* loop; pacing nudges under-delivered campaigns so actual plays converge on booked share over the day.

**Campaign fan-out:** one campaign spans many endpoints/zones. The tracked trace is: campaign → line items → per-zone bookings (share % against that zone's ledger) → per-zone asset assignment (creative variant matching the zone's dims/specs) → runtime loop placements → proof-of-play rolled up per (campaign, zone).

**Decisions locked 2026-07-16:**

| Decision | Outcome |
|---|---|
| Mode switch level | **Retailer-wide** (as PRD §6.1 wrote it) — buying SSP flips the entire estate. No mixed estates in v1. |
| SOV booking granularity | **Constant % per flight** — one share % from flightStart to flightEnd. Availability = 100% − *max concurrent booked share over the requested window*. Dayparting is a runtime-targeting concern, not a booking concern. |
| Playlist fate on switch | **Playlists become the P4 filler pool** — existing zone playlist content isn't deleted; it plays whenever no campaign wins the loop slot. Zero-content screens are impossible; retailer content investment is preserved. |

**Terminology note:** "share of voice" (product) = "share of play" (PRDs/code) — same concept; pick one term for the amended PRD.

---

## 2. The Chain, Link by Link

The production path should be: **Store → Endpoint → Channel → Layout → Zones → (KVP tags) → InventoryUnit + TimeBudget (+ RateCard + Traffic) → Inventory Search → Booking (share-of-play) → Activation → Creative routed to endpoints → Playback + proof-of-play.**

| # | Link | API | UI | Spec (PRD) | Status |
|---|------|-----|----|-----------|--------|
| 1 | Store/Site + Endpoint registration | ✅ Full CRUD (`siteController*`, `mediaPlayerController*`, incl. device pairing, CSV import) | ⚠️ Exists; de-wired stubs on develop | Assumed from Cue | **Exists** |
| 2 | Endpoint → Channel assignment | ✅ Expressible both ways (`MediaPlayerEntity.channel`, `MediaPlayerChannelEntity.mediaPlayer`) | ⚠️ ChannelPicker built, but `channelsList` hardcoded `[]`, save is a `setTimeout` | ❌ Not in any Deal Desk PRD | **API yes, UI stub, spec missing** |
| 3 | Channel → Layout → Zones | ✅ `mediaPlayerLayoutController*`, `mediaPlayerZoneController*` (zones have stable IDs, x/y/w/h, type `standard\|take-over`), `CreateChannelLayoutV1` clone-attach | ⚠️ Channel add/detail with zone canvas built; all data stubbed. `/signages/layouts` page is skeleton-only | ❌ "layout/zone definitions" delegated to Cue as a dependency row | **API yes, UI stub, spec missing** |
| 4 | **Zone → InventoryUnit + TimeBudget materialization** | ❌ Nothing links `MediaPlayerZone` to `InventoryUnit`; zero create routes for digital inventory in Phase 1 §5.4 / Phase 2 §5 | ❌ None | ❌ **The core gap** — no creation trigger, owner, or workflow in any PRD | **MISSING ENTIRELY** |
| 5 | KVP tagging for targeting + routing | ⚠️ Real `TagEntity` (typed key/value) + `AssignTags` + `LookupTags` reverse search — but `TagModel` = SITE, PLAYLIST_CONFIG, MEDIA_PLAYER, CHANNEL only. **No ZONE.** `MediaPlayerZoneEntity.tags` is a bare `string[]` | ⚠️ Tag Manager wired on master; 2 wired call sites appear malformed (see §4) | ⚠️ KVP taxonomy + rule grammar defined; **assignment mechanism/owner never specified**; no KVP CRUD in §16 | **Partial — zone tier unsupported; Deal Desk grammar not connected to TagEntity** |
| 6 | Rate card + traffic attach | ✅ `PUT /v2/retailers/endpoints/:id/rate-card` upsert + bulk; StoreTraffic CRUD + CSV | ✅ Phase 3 views spec'd/built | ✅ Spec'd — but the `zones[]` array in the upsert **presupposes zoneIds already exist** | **Exists, blocked by link 4** |
| 7 | Inventory search | ⚠️ FE calls `InventoryControllerSearch` with `{filters:{}, page, pageSize} as never` — contract unverified; design spec's `DigitalSearchRequest` (adDuration, kvpRules, endpointTypes) doesn't match the wired body | ⚠️ Step 2 built; KVP rules held client-side and **never sent**; LINE_ITEMS/STORES hardcoded; guarantee/impression constants hardcoded FE-side | ✅ Response shape fully spec'd (§3.4) | **Built on both sides, contract unpinned, returns empty per link 4** |
| 8 | Booking / share-of-play | ✅ Phase 2 booking engine spec'd; mutates TimeBudget (deref'd **without null check** — provisioning is a hard precondition) | ✅ Step 2 share sliders | ✅ Spec'd | **Spec'd, blocked by link 4** |
| 9 | Activation → creative routing to endpoints | ❌ Campaign activation today is a bare status PUT with zero side effects; "assets synced to endpoint during campaign activation" via "normal content sync" is **never defined**; the mock Activate button promising "72 zones booked, 3 creatives deployed" has **no onClick** | ❌ | ⚠️ Named but unspecified (no API/component resolves KVP targeting → concrete endpoint list → pushes assets) | **MISSING** |
| 10 | Endpoint availability display | — | Depends on 4/6/7 | ✅ Search response includes per-zone `availableShare`, plays at share levels, guaranteed plays, impressions, rates | **Blocked by link 4** |

**Root cause in one sentence:** two systems of record — Cue (endpoints/channels/layouts/zones) and Deal Desk (`inventoryUnits`/`timeBudgets`/`rateCards`) — with the PRDs explicitly saying "reference by ID, don't create," and **no one ever wrote the materialization contract between them.**

---

## 3. Model Conflicts to Resolve (product decisions required)

These are decisions, not builds. They gate the build.

| # | Decision | Options / evidence | Recommendation |
|---|----------|-------------------|----------------|
| **D1** | **Canonical hierarchy.** PRD §19: Endpoint → Layout → Zones (channels playlist-only). Your model & Cue API: Endpoint → Channel → Layout → Zones. §12.2 already lists "channels" as an SSP search facet, contradicting the PRD's own data model. | Adopt the channel-centric model (matches the real API; channel is the natural sellability/scheduling container) and amend the PRD. | **Endpoint → Channel → Layout → Zones**; PRD amendment |
| **D2** | **Channel : endpoint cardinality.** Entities carry single refs both ways (1:1-ish today); your model implies one channel serving many endpoints (which is also what makes bulk sellability practical — assign one "Video MP" channel to 66 players). | 1:1 keeps identity simple but multiplies channel admin ×N endpoints. 1:many requires the inventory identity to be **(endpointId, zoneId)** — same zone definition, one sellable unit *per endpoint carrying the channel*. | **1 channel : many endpoints**; sellable unit keyed on (endpointId, zoneId); confirm backend semantics of `CreateChannelLayoutV1` (channel-specific layout clone) first |
| **D3** | **Materialization strategy.** (a) Event-driven sync: channel-assigned/layout-changed events upsert units; (b) on-demand derivation at search time (no stored units — contradicts Phase 1/2 schema + booking engine); (c) explicit "publish/sellable" step with a retailer-facing toggle. | (b) would require re-speccing Phase 2. (a)+(c) combined gives automation with retailer control. | **Sync job + lifecycle events, with a per-channel (or per-zone) `sellable` flag**; default sellable=true on SSP retailers |
| **D4** | **Zone-level KVPs.** TagModel has no ZONE; zone.tags is `string[]`. Zone-scoped keys the grammar already assumes: `zone_type`, `product_category_in_zone`. | (a) Add `TagModel.ZONE` + assign/lookup support; (b) inheritance: effective KVP set = site ∪ endpoint ∪ channel ∪ zone-intrinsics (type, name, weight). | **Both**: inheritance for computed context, `TagModel.ZONE` for retailer-set zone tags |
| **D5** | **Loop config ownership.** `loopDuration` (120), `retailerReservedSeconds` (30), `atomicUnit` (5) are "configurable per zone" but no UI/API sets them. | Defaults at retailer level (SSP waterfall config is the natural home) with per-zone override on the channel/zone editor. | Retailer defaults + per-zone override |
| **D6** | **Search contract.** Wired FE sends `{filters:{}, page, pageSize}` (cast `as never`); design spec says `DigitalSearchRequest` with lineItemId/adDuration/kvpRules; SDK 5.11.0 (private registry) is the only artifact that knows the truth and isn't installed locally. | Pin one contract; regenerate SDK; remove the `as never`. | **v2 spec contract** (adDuration + kvpRules server-side) |
| **D7** | **SSP-activation semantics.** §6.1: SSP purchase is "a retailer-wide switch — all endpoints transition." Does flipping it materialize inventory for every configured endpoint? | Tie the initial bulk materialization (backfill) to SSP package activation; incremental sync thereafter. | Yes — backfill on activation, then event-driven |

Also resolve (smaller): physical-vs-digital "zone" naming collision (Blueprint floor-plan zones vs screen-layout zones — different entities, same word — decide whether `product_category_in_zone` refers to the *physical* zone the endpoint is pinned in); zone `width/height` typed `string` while `x/y` are `number` (px vs % undocumented).

### Decision outcomes (recorded 2026-07-16)

| # | Status | Outcome |
|---|--------|---------|
| D1 | ✅ **Resolved** | Channel-centric hierarchy confirmed: Endpoint → Channel → Layout → Zones in **both** modes. Channel carries structure always; playlists are its Cue-mode content role only. PRD §19 to be amended. |
| D2 | ✅ **Resolved** | 1 channel : many endpoints. **A zone in an endpoint is what makes a sellable unit unique** — identity is `(endpointId, zoneId)`. Backend confirmed (§3.1 #1): zoneIds are stable for the life of a channel. |
| D3 | ✅ **Resolved (shape)** | Sync job + lifecycle events. Retailer-wide SSP switch makes the per-zone sellable flag optional in v1 (everything sellable when SSP is on); keep the flag in the schema for future mixed estates. |
| D4 | ✅ **Resolved** | Inheritance **plus zone-local additive tags**: effective KVPs = site ∪ endpoint ∪ channel ∪ zone-local. Zone-local tags differentiate zones on one endpoint (e.g., a GPU endpoint split into an AMD zone and an NVIDIA zone, each carrying its own `brand_content` tag). Most-specific tier wins on collision. Requires `TagModel.ZONE`. |
| D5 | ✅ **Resolved** | **One loop clock per endpoint per store** (Backend Confirmation #2). `loopDuration` is endpoint-level, boundary-aligned to preserve top-of-the-hour takeovers (absorbed in the guarantee buffer). Per-zone loop-duration override dropped. Retailer defaults live in SSP waterfall config; default changes do **not** retroactively apply to endpoints/zones carrying active bookings (booking-protection lock, B1). |
| D6 | ✅ **Resolved (shape)** | Search is a **multi-dimensional filter**: (1) site scope — specific siteIds or all sites; (2) kvpRules layered on top of the site scope; (3) flight date range; (4) adDuration. Response = per-zone remaining SOV over the window. Pin against SDK 5.11 and remove the `as never`. |
| D7 | ✅ **Resolved** | SSP activation is the retailer-wide switch and the backfill trigger: activation materializes InventoryUnits + TimeBudgets for every endpoint-with-channel, and registers zone playlists as the P4 filler pool. |
| **D8 (new)** | ✅ **Resolved** | **TimeBudget must be time-windowed, not scalar.** Phase 1's schema stores a single `totalShareBooked`/`availableShare` and its bookings carry no flight dates — it cannot answer "share remaining Aug 1–31" and wrongly blocks non-overlapping bookings. Bookings carry `flightStart/flightEnd`; availability = 100% − max concurrent booked share over the requested interval (constant % per flight per the 2026-07-16 decision). This lands **before** B1 writes any documents. |
| **D9 (new)** | ✅ **Resolved** | **Availability is precomputed, not computed at search time.** A materialized per-unit **SOV availability calendar** (day-granularity buckets) is recalculated on the Concourse queue whenever a booking-affecting change lands, keyed to the affected `(endpointId, zoneId)` units only. Search reads the calendar; **booking commits validate against the authoritative TimeBudget bookings transactionally, never the calendar** (staleness surfaces as the existing 409 OVERBOOKING treatment, Phase 3 §4.2). The calendar is a derived view — always rebuildable from bookings. See B1b. |

### 3.1 Backend confirmations required before B1 schema design

**Confirmation #1 — `CreateChannelLayoutV1` semantics: is `zoneId` stable for the life of a channel?**

> ✅ **ANSWERED 2026-07-16: Yes — zoneIds are stable for the life of a channel.** B1 keys on `(endpointId, zoneId)` safely. The clone-vs-link mechanics remain an implementation detail with no schema impact.

Everything downstream (TimeBudgets, bookings, SOV calendars, rate cards) is keyed `(endpointId, zoneId)`; any operation that regenerates zoneIds orphans all of it. Answer via API-repo inspection (current revision — local `conqrse-api3` predates this) or empirically in staging (create layout with zones → attach to two channels → diff zone IDs → edit a zone → observe propagation):

1. Does `POST /channels/{channel}/layouts/{layout}` **clone** (new layout + new zone IDs) or **link** (shared layout document)?
2. What does `MediaPlayerLayoutEntity.reference` mean — template lineage? Does cloning preserve zone IDs?
3. Can two channels share one layout document? If yes, which channels/endpoints see a zone edit?
4. Does **any** operation regenerate zoneIds (re-attach, layout swap, re-save)?
5. On channel layout swap, what happens to the old zones — deleted, orphaned, retained?

Design consequence: clone-with-stable-IDs → B1 events map 1:1. Shared-by-reference → layout edits become fan-out events across all referencing channels. IDs regenerate → PRD needs a **zone identity survival policy** (block swap while `bookedShare > 0`, or an old→new ID migration carrying bookings/calendars/rate cards).

**Confirmation #2 — Loop-config: can the runtime honor per-zone overrides, and what breaks when config changes?**

> ✅ **ANSWERED 2026-07-16: One loop clock per endpoint per store.** Loop boundaries stay aligned to preserve top-of-the-hour takeovers; takeover impact is absorbed by the guarantee buffer (consistent with the conservative guarantee math, PRD §3.6). **Per-zone loop-duration overrides are dropped from the PRD** — `loopDuration` is endpoint-level. Config changes on booked inventory are governed by the **booking-protection lock** (see B1): entities with active bookings are not editable or deletable; bookings must be moved or cleared first.

Direct to Cue endpoint-runtime engineering (same channel as the Phase 4 rule-evaluator rollout):

1. Can one multi-zone screen run **different loop durations per zone**, or do all zones on an endpoint share a single loop clock?
2. Do takeover semantics ("synced to local time across every endpoint") require loop-boundary alignment per store or network-wide — effectively making `loopDuration` a retailer-level constant?
3. Where is the loop enforced — server-paced decide responses, or an endpoint-local loop scheduler? (Determines whether config changes propagate via hot-cache invalidation or content-sync push.)
4. Product policy once #1 is known: changing loop config on a zone with active bookings changes `loopsPerDay`/`sellableSecondsPerLoop` — silently altering booked campaigns' plays/day, duration fits, and guarantees. Block while booked, or allow + recalc (B1b trigger) + re-validate guarantees + notify?

Design consequence: if the answer is "one clock per endpoint/store," D5 collapses to *retailer default + per-endpoint reserved-seconds override* and the per-zone override drops from the PRD. If per-zone loops are supported, the SOV calendar already carries `loopsPerDay` per unit and nothing changes structurally — but the #4 policy must be written either way.

---

## 4. Defects & Risks Found Along the Way

Not the headline gap, but they'll bite during the closure build:

1. **Two wired production tag calls look malformed** (flagged PLAUSIBLE, not confirmed against backend):
   - Endpoint detail sends `model: 'MediaPlayer'` where the `TagModel` enum value is `'media-player'` (cast through `as any`) — `MediaPlayerDetailClient.tsx:285-287` (master).
   - Channel detail calls `AssignTags` with the **channel id in the tag-id path slot** and a `{tags}` body that doesn't match `AssignTagDto {assignIds, model, value}` — `MediaPlayerChannelDetailClient.tsx:673-676` (master).
2. **Phase 2 search pseudocode dereferences TimeBudget without a null check** (§3.5.1) — even after seeding, any zone missing its TimeBudget can throw rather than degrade.
3. **Phase 1 internal contradiction:** §1.3 promises "CRUD endpoints" for every §3 entity; §5 defines none for `inventoryUnits`/`timeBudgets`. This is likely how the gap slipped through review.
4. **SDK drift:** the FE branch depends on `@conqrse/api-sdk@5.11.0` (private registry, not installed anywhere locally); local checkouts have 4.19.0 with **zero** InventoryController types. Entity shapes are only recoverable from hand-maintained FE view interfaces marked "provisional… confirm the field names when seeded."
5. **Branch topology risk:** Deal Desk FE exists only on `feat/deal-desk-permissions-v2`; neither `develop` nor `master` has the directory. Master (production) ships the `(UIDesignLayout)` mocks — worth confirming those mock routes aren't customer-reachable.
6. **UI/model mismatches queued up for the wiring pass:** `channel.description` and `zone._id` in UI vs no `description` field and `id` (BaseEntity) in entities; stub comments reference non-existent hook names.
7. **A legacy bridge already exists and is unused:** the Program/ProgramInventory system (`POST /v1/retailers/{retailer}/programs/inventory/search` taking tags/sites/channels/mediaPlayers; `ProgramPlayStats.guaranteedPlays`) is the closest ancestor of what we're building. Zero UI calls it. Decide explicitly to deprecate it rather than leave two inventory systems.

---

## 5. What to Build to Close the Gap

### B1 — Digital Inventory Provisioning service (the missing link — build first)
The bridge from Cue's chain to Deal Desk's sellable collections.

- **Derivation rule:** for every active endpoint with a channel, for every zone in the channel's layout → upsert one `InventoryUnit` (`screen_zone_slot`, keyed `(endpointId, zoneId)`, carrying `layoutId`, `zoneName`, `zoneWeight`, denormalized store/tier) + one `TimeBudget` per `(zoneId, endpointId)` with retailer-default loop config (per D5). Stream/audio endpoints map to their slot types by `MediaPlayerType`.
- **Lifecycle events (keep it in sync):** channel assigned/unassigned to endpoint; layout attached/changed; zone added/edited/removed; endpoint retired/deleted; sellable flag toggled. Removal deactivates units, and defines a policy for stranded bookings (block removal if `totalShareBooked > 0`, or auto-release + notify).
- **Backfill job:** materialize the existing footprint on SSP activation (per D7) — this is what turns "854 stores / 66 players / 0 units" into real numbers.
- **Invariant checks:** Σ zoneWeight ≤ 1.0 per layout; `(endpointId, zoneId)` uniqueness; TimeBudget always exists before a unit is searchable (fixes risk §4.2).
- **Time-windowed SOV ledger (per D8):** TimeBudget bookings carry `flightStart/flightEnd`; `availableShare` is computed per requested date range (100% − max concurrent booked share over the interval), not stored as a scalar. The booking engine's 100%-cap check and category-exclusivity check both evaluate over the interval.
- **Booking-protection lock (confirmed 2026-07-16):** any entity whose mutation would invalidate a booking — zone geometry/deletion, layout swap or detach, channel unassignment, endpoint retirement, loop config — is **locked from edit and delete while it carries active or future bookings** (any booking with `flightEnd ≥ today`; past bookings never lock). To edit or delete, the bookings must be **moved or cleared first**. Enforcement at the API layer with a structured error (`409 BOOKINGS_EXIST`, `details` listing the blocking campaigns/bookings) so the UI can render a locked state with a resolution path. v1 ships **clear-first** (release bookings, then edit); a **move/rebook flow** (migrate bookings to another zone) can follow post-v1.
- **P4 filler mapping (per 2026-07-16 decision):** on SSP activation, each zone's existing playlist schedules are registered as that zone's P4 filler pool — playlists stop being the primary content layer and become the waterfall's fallback. No zone can go dark.

### B1b — SOV Availability Calendar + recalculation pipeline (per D9)
The materialized layer that makes inventory search a pure read.

- **Entity `sovCalendars`:** one document per `(endpointId, zoneId)` per month — `{ retailerId, endpointId, zoneId, month, days: { <day>: { bookedShare, availableShare } }, loopsPerDay, version, recomputedAt }`. Day granularity suffices because bookings are constant % per whole-day flights (D8); the step function only changes at flight boundaries. The same buckets feed the Brand Portal Calendar tab's month-view availability heatmap directly.
- **Derived view, never source of truth:** always rebuildable from the TimeBudget's authoritative `bookings[]`. Recompute reads the source and overwrites — idempotent, self-healing; ships with a full-rebuild admin job for backfill and repair.
- **Recalculation on the Concourse queue** (`sov-recalc` job; payload = affected unit keys or a campaignId to expand; coalesce duplicate keys; retry with backoff). Triggers: booking created/changed/released; campaign flight-date change; loop-config change; **takeover booked/released** (fan-out to every zone at affected stores — batch); unit provisioned/retired (initialize at 100% / tombstone).
- **Consistency rule (must be explicit in the PRD):** searches read the calendar; **booking commits never do** — commits validate transactionally against the TimeBudget's `bookings[]` with an optimistic version lock. Calendar staleness between event and recompute therefore can't double-sell; it surfaces at commit as `409 OVERBOOKING` (UX already specified, Phase 3 §4.2).
- **Read-time math stays cheap:** plays/guaranteed-plays/impressions per search row derive from the day bucket + `loopsPerDay` + rate card + traffic at read time; only booked/available share is precomputed.

### B2 — Wire the Cue admin chain UI + SSP-mode channel view (wiring + one new view variant)
The endpoint→channel picker, channel add/detail + layout/zone editor, `/signages/layouts`, and Tag Manager all exist as components. Replace the stubbed arrays/`setTimeout` saves with the generated hooks (`cqQueryMediaPlayerChannelControllerFindAllV1`, `cqMutationMediaPlayerZoneControllerCreateV1`, …), fix the hook-name and `_id`/`description` mismatches, and fix the two malformed tag-assign calls (§4.1).

**SSP-mode channel/zone view (new, clarified 2026-07-16):** the channel detail view is **mode-adaptive**. Structural editing (layout selection, zone drawing/geometry, zone tags) is shared across both modes. What changes per zone is the content panel:

| Zone panel | Cue mode (today) | SSP mode (new) |
|---|---|---|
| Content | Per-zone schedule calendar (playlists/content groups) | **SOV ledger view**: loop config (120s / reserved / sellable seconds), booked share vs. available (for a selected date range), bookings list (campaign, share %, flight, priority), link out to Loop Visualizer (10.5) and to the zone's rate card |
| Actions | Add/edit schedule | View loop config (endpoint-level clock — read-only at the zone); toggle sellable flag; view P4 filler source (the zone's former playlists). **Locked state** when the zone carries active bookings (B1 booking-protection): edit/delete disabled, with the blocking campaigns listed and a clear-bookings resolution path |

The retailer-wide SSP switch determines which variant renders — no per-zone mode toggle in v1.

### B3 — Unified KVP tag architecture (expanded 2026-07-16)
Today the platform has **two disjoint tag schemas**: (a) the retailer-scoped typed `TagEntity` (key/value/type, `AssignTags`/`LookupTags`) covering sites, media players, channels, and playlist configs; and (b) a **separate** playlist-asset tag system (`tag-keys`, `tag-keys/{key}/values`, `{id}/tags` via `useAssetTags`) with its own endpoints and shape. The inventory KVP work must not add a third. Scope:

- **One schema for all KVP tags.** `TagEntity` becomes the single tag architecture. Extend `TagModel` with **`ZONE`** and **`ASSET`**; migrate the asset tag endpoints onto the unified assign/lookup surface (or adapter + deprecation window). One taxonomy (allowed keys, types, value lists) governs every tier: site, endpoint, channel, zone, asset.
- **Inheritance + zone-local additive tags (per D4).** Effective KVPs for a zone = site ∪ endpoint ∪ channel ∪ **zone-local tags**. Zone-local tags are *additive* — they exist to differentiate zones on the same endpoint. Canonical use case: a GPU endpoint split into two zones — one tagged `brand_content = 'AMD'`, the other `brand_content = 'NVIDIA'` — same endpoint, different targetable inventory. On key collision, the most specific tier wins (zone > channel > endpoint > site).
- **Static KVP contract:** the keys the rule grammar already assumes (`store_id`, `region`, `store_tier`, `zone_type`, `endpoint_type`, `screen_orientation`) must be resolvable for every provisioned unit — some derive from entities (tier, type), some from tags.
- **Consumers:** effective KVPs feed (a) inventory search filtering, (b) the decide-time context bag, (c) the KVP rule builder's key/value pickers (replace the hardcoded `KVP_KEYS` array with a taxonomy lookup), and (d) asset routing at activation (asset tags matched to zone tags — the same schema on both sides is what makes routing a join instead of a translation).

### B4 — Inventory search contract + FE integration
Pin the search contract (D6), regenerate the SDK, remove the `as never` cast. The request is a **layered multi-dimensional filter**:

1. **Site scope** — explicit `siteIds[]` or `allSites: true` (the first dimension the planner picks);
2. **KVP rules** — layered on top of the site scope, evaluated against each zone's *effective* KVP set (B3 inheritance);
3. **Flight date range** — availability window;
4. **Ad duration** — line-item context for plays/guarantee math.

Response returns each matching zone's **remaining SOV over that window** — read from the precomputed availability calendar (B1b), never computed across all zones at query time — plus plays/guaranteed plays at candidate share levels, impressions, and rate. Replace hardcoded LINE_ITEMS/STORES catalogs and FE metric constants (guarantee %, impressions/play) with server-computed values so the math is single-source. Step 2's filter panel mirrors the layering: site picker first, then the KVP rule builder scoped within it.

### B5 — Sellability funnel / readiness surfacing
Make the gap diagnosable in-product: Inventory Dashboard (7.0) gains a provisioning funnel — endpoints without a channel → channels without layouts/zones → zones without rate cards → zones without traffic → **sellable units**. Each stage links to the fix surface. (This is the tool that would have caught "0 sellable units" before an engineer did.)

### B6 — Activation side effects (creative routing)
Define and build what "normal content sync" means: on Ready→Active, resolve the campaign's targeting (KVP rules + explicit zone bookings) to the concrete endpoint set, pre-load creatives (and rule-triggered variant ASTs, per Phase 4 §4) via Cue's content-sync/`MEDIA_PLAYER_CONFIG` push, invalidate the waterfall hot cache, and record sync status per endpoint with retry. Cancellation sends removal sync.

### B7 — PRD amendments (close the spec gap itself)
- New section in the source PRD + a Phase 1/2 addendum: **"Digital Inventory Provisioning"** — derivation rule, lifecycle events, backfill, sellable flag, API routes (`POST /v2/retailers/:id/inventory/provisioning/sync`, unit/timeBudget upsert semantics), and the Cue↔Deal Desk identity contract for `(endpointId, zoneId)`.
- Correct §19's data model to the channel-centric hierarchy (D1) and remove the internal contradictions (§1.3 CRUD promise; §12.2 channels facet).
- Specify KVP assignment ownership + API, and the activation content-sync contract (B6).
- Explicitly deprecate the legacy Program/ProgramInventory system.

### Suggested sequencing

| Order | Item | Depends on | Notes |
|---|---|---|---|
| 0 | Decisions D1–D7 | — | Product; blocks everything |
| 1 | B7 PRD amendments | D1–D7 | Cheap; do while B1 is designed |
| 2 | **B1 provisioning service + backfill, with B1b availability calendar + recalc pipeline** | D1–D3, D5, D7–D9 | Backend; time-windowed schema (D8) and calendar (D9) land in the same build — unblocks QA against real data (replaces seeds) |
| 3 | B2 admin UI wiring | none (parallel) | FE; makes retailers self-serve the chain |
| 4 | B4 search contract | B1, D6 | Backend+FE; kills the `as never` |
| 5 | B3 KVP completion | D4 | Backend+FE |
| 6 | B5 readiness funnel | B1 | FE |
| 7 | B6 activation routing | B1, B3 | Backend + endpoint runtime; overlaps Phase 4 rule-triggered work |

---

## 6. Answer to the Engineer's Question

> "Was digital-as-seed intentional for now, or is a production path expected (and just not written down)?"

**A production path was always intended and was never written down.** Phase 1 §3.14 assumed Cue owned endpoints/layouts/zones and Deal Desk would "reference by ID" — but the step that turns a Cue zone into a sellable `InventoryUnit` + `TimeBudget` fell between the two systems and no PRD claimed it. The intended model: every endpoint is assigned a **channel**; the channel carries a **layout of zones**; each zone (per endpoint carrying that channel) becomes a sellable unit with a per-zone TimeBudget; endpoints/channels/zones carry **KVP tags** used for campaign targeting and for routing creative to the right endpoints at activation. Note this also means the PRD's own data model (layout attached directly to endpoint, channels playlist-only) is wrong and will be amended.

**Keep the staging seeds** so QA can proceed, and **hold the digital-creation build** until the D1–D7 decisions land (channel cardinality and materialization strategy in particular change the schema) — then B1 (provisioning service + backfill) is the first build.

---

## 7. Caveats

- The Conqrse API backend repo was not inspectable from this machine (local `conqrse-api3` predates the InventoryController; SDK 5.11.0 lives only on the private registry). Entity field names and the search body must be validated against the actual backend before B1 is designed.
- Where the current staging seeds live was not found in any local repo — presumably a newer backend revision or ops tooling.
- The two malformed tag-assign calls (§4.1) are flagged from client-side evidence only; confirm against backend behavior before filing as bugs.
