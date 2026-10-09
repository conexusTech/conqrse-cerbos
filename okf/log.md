---
type: Log
title: Cerbos OKF log
description: Append-only record of durable learnings and knowledge-bundle updates.
owners: [jody@conexus-tech.com]
tags: [log, okf]
---

# Cerbos OKF log

## 2026-10-09 — Brand creative upload resource (Cue Media Optimizer CMO-0.3)

- Added `dealdesk_brand:creatives` (collection, `create`, Brand Center) to the matrix and
  regenerated its policy and the permission-types enum and `RESOURCE_META`; registered the
  policy in `k8s/base/kustomization.yaml`. It is the policy for the Brand Hub video draft
  route (`POST /v1/deal-desk/brand/creative/draft`): brand roles only for a retailer in
  `P.attr.retailerIds`, operator roles (View-as-Brand) with Brand Center. Six native test
  cases; seeded the `brand-creative-upload` capability and checklist. **api3 does not check it
  yet:** Cerbos cannot evaluate a brand user today (Drexel #36).
- Published as `@conqrse/permission-types@1.10.0-cmo.0` on dist-tag `cmo` (Leo approved;
  `latest` stays 1.9.0). It also carries the team-access `Principal.teamIds`; the plain 1.10.0
  stays with the team-access work.
- `scripts/generate_policy_tests.py` needs PyYAML, which a stock Python lacks: run the gate
  with it on `PATH` (a virtualenv works). Rewriting `tests/test-cases.json` with
  `json.dump` reformats the whole file — insert new suites as text.

## 2026-09-13 — Local QA runtime

- Corrected the local Docker configuration to use Cerbos's disk driver over the
  checked-in policy bundle. The previous fresh SQLite store either failed when
  `/data` was absent or started empty and default-denied every decision. The
  Kubernetes SQLite ConfigMap remains unchanged; local allow/deny decisions are
  now evaluated from the current workspace policies. A live assigned-member
  playlist check returned `EFFECT_ALLOW`, while the equivalent non-member check
  returned `EFFECT_DENY`.

## 2026-09-09 — Update

- Adopted process v3 with a repository service concept, lazy capabilities, QA
  checklists, a single workspace roadmap, and a local conformance gate.
