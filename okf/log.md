---
type: Log
title: Cerbos OKF log
description: Append-only record of durable learnings and knowledge-bundle updates.
owners: [jody@conexus-tech.com]
tags: [log, okf]
---

# Cerbos OKF log

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
