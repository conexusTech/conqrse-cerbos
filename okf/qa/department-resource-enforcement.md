---
type: QA Checklist
title: Team-based resource access enforcement — checks
description: Proof contract for trusted team membership and tenant-aware authorization. The filename retains its historical roadmap slug; department profile metadata is explicitly excluded.
owners: [jody@conexus-tech.com]
tags: [qa, authorization, teams]
---

### Check: restricted-resource-team-membership
**Requirement:** A restricted resource is available only to an assigned team member
**Surface:** Cerbos playlist, channel, zone, site, and endpoint collection/item resources
**Automated:** tests/test-cases.json; conqrse-api3 resource authorization tests

**Do:**
- Evaluate each restricted resource type as an assigned member, a non-member, and the member after removal

**Expect:**
- The assigned member is allowed
- The non-member and removed member are denied

### Check: all-resource-access
**Requirement:** An all-access resource remains available to retailer members
**Surface:** Cerbos playlist, channel, zone, site, and endpoint collection/item resources
**Automated:** tests/test-cases.json

**Do:**
- Evaluate an all-access playlist, channel, zone, site, and endpoint as an ordinary user from its retailer

**Expect:**
- Access is allowed without a team assignment

### Check: team-enforcement-tenant-boundary
**Requirement:** Team authorization cannot cross tenant boundaries
**Surface:** API3 resource/team guards and Cerbos team resources
**Automated:** tests/test-cases.json; conqrse-api3:/src/cerbos/guards/cerbos-authorization.guard.spec.ts

**Do:**
- Request a playlist or department using a retailer identity from another tenant

**Expect:**
- The guard or policy denies the request before the controller operation runs
- Supplying an act-as header without super-user authority does not bypass the denial

### Check: department-manager-access
**Requirement:** Authorized managers retain complete retailer access
**Surface:** Cerbos `contents:playlists` resources and API3 playlist listing
**Automated:** tests/test-cases.json; conqrse-api3:/src/backend/services/data/playlist-config.service.spec.ts

**Do:**
- Evaluate restricted playlist, channel, zone, site, and endpoint access with each management role in a permitted tenant

**Expect:**
- Managers can administer the complete playlist set
- Ordinary users remain filtered by membership before pagination

### Check: department-metadata-ignored
**Requirement:** Department metadata cannot grant access
**Surface:** Cerbos principal attributes and API3 principal construction
**Automated:** tests/test-cases.json; conqrse-api3:/src/cerbos/cerbos.service.spec.ts

**Do:**
- Evaluate a restricted resource with no matching `teamIds` while setting `department` to the assigned team name and then its identifier

**Expect:**
- Both decisions are denied
- The same principal is allowed only after the matching trusted team ID is supplied
