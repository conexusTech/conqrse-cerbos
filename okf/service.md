---
type: Service
title: Conqrse Cerbos authorization service
description: Policy source, generator, tests, and shared permission-type package for Conqrse services.
owners: [jody@conexus-tech.com]
tags: [cerbos, authorization, policies]
---

# Conqrse Cerbos authorization service

This repository owns the Cerbos resource policies, derived roles, schemas,
policy-generation tooling, and `@conqrse/permission-types` package consumed by
Conqrse Admin and API3.

The resource/action and product matrix in
`../docs/RESOURCES_ACTIONS_MATRIX.md` is the editable source of truth. Generated
policy YAML, generated TypeScript enums, the Kustomize policy allowlist, and
consumer permission decorators must remain synchronized.

## Boundaries

- This repo defines whether a principal may perform an action on a resource.
- API3 supplies authenticated principal and resource attributes and enforces the
  decision.
- Admin consumes permission types and uses permissions for presentation, but UI
  visibility is not an authorization boundary.
- Deployment and package publication are external actions requiring explicit
  approval.
