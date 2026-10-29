# Conqrse Cerbos agent guide

This is the canonical instruction file for Codex/ChatGPT and other coding agents
working on Conqrse authorization policies and permission types. Repository
knowledge lives in the OKF database (source `conqrse-cerbos`), read and written
through the `okf` MCP server and browsable at https://okf.conqrse.com; start with
`okf_get conqrse-cerbos:/service.md`. The repo `okf/` folder was removed on
2026-10-29 (git history keeps it).

## Absolute guardrails

- Never expose or commit secrets, credentials, tokens, customer data, or `.env`
  files. Inspect staged changes before every commit.
- Never push, publish `@conqrse/permission-types`, deploy policies, merge, or
  mutate a cluster without explicit user approval in the current conversation.
- Never add `Co-Authored-By:` or an agent signature to a commit.
- Preserve unrelated work. Never reset or clean changes you did not create.
- Never weaken policy tests, schemas, consumer contracts, or OKF concepts to make a
  gate pass.

## Calibrated autonomy

Stay inside the requested authorization outcome. Proceed on reversible changes
that follow the matrix and established generators. Stop for any change to intended
access, compatibility, package versioning strategy, production, or irreversible
state. Recommend one option with reasoning when a decision is required.

State a compact read/write/verification plan for multi-step work and report failed
or skipped checks exactly.

## Model and delegation policy

- **Astra** (`gpt-6-astra`) owns planning, authorization architecture, threat
  review, arbitration, synthesis, and final curated writes.
- **Sol** (`gpt-5.6-sol`) handles bounded policy implementation, extraction,
  generation checks, tests, and mechanical documentation work.
- The **ChatGPT/Codex main session** owns scope, user decisions, integration,
  final review, roadmap/log changes, and commits.

Delegate only genuinely parallel work. Reading may fan out; writers require
strictly disjoint ownership declared before launch. Select Sol or Astra explicitly
for delegated work. A worker does not certify its own changes.

## Process v3

The workspace methodology at `../.claude/rules/methodology.md` governs this repo.

- One change equals one user-meaningful authorization outcome and exit criterion.
- `workspace:/roadmap.md` (`../roadmap.md`) is the only status surface.
- Implemented behavior is recorded in `conqrse-cerbos:/capabilities/`; its proof
  contract is recorded in the matching `conqrse-cerbos:/qa/` concept.
- Temporary plans live under `artifacts/<slug>/` and are removed when landed.
- Plan and land are the two human gates.
- `_proposals/` is non-authoritative input or history.

## Policy invariants

- The resource/action and product matrix in
  `docs/RESOURCES_ACTIONS_MATRIX.md` is the source of truth. Do not hand-edit a
  generated `resource_*.yaml` policy.
- Regenerate policies with `scripts/generate_policies.py` and types with
  `scripts/generate_types.py`; inspect the generated diff.
- Keep `k8s/base/kustomization.yaml` synchronized. A policy omitted from its
  allowlist does not deploy.
- Narrowing an action is a breaking API contract. Inspect API3 permission
  decorators and land compatible consumer changes first.
- A policy contract change requires an appropriate semver update to
  `@conqrse/permission-types`; publishing still requires explicit approval.
- Staging must precede production, and both deployments require explicit approval.
- Authorization is default-deny. Tests must cover expected allows and denials,
  tenant isolation, product gates, and derived roles.

## OKF protocol

Before changing policies, `okf_get conqrse-cerbos:/service.md`, then use
`okf_search` / `okf_list` / `okf_links` for the relevant business/integration
concepts and the matching capability and QA checklist. Inspect the Admin and API3
sources when the contract affects consumers. When a public surface changes,
`okf_concept_update` the concept in the same change; use `okf_concept_create` for
stubs and `okf_propose` for bigger rewrites. Add capability scenarios only for
implemented and verified behavior, and give every scenario a matching QA check.
Record durable learnings and updates with `okf_log_append` (Update or Learning).

## Verification gate

Run focused generation and policy checks while implementing. Before claiming
completion, run:

```bash
make gate
```

The gate validates the generated permission-types package, policy
matrix synchronization, and locally available policy tests. Live-server or
cluster verification is additional evidence and never implied by a static gate.
