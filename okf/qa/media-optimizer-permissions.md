---
type: QA Checklist
title: Media optimizer administration access — checks
description: Proof contract for the contents:media_optimizer resource (Cue Media Optimizer media-optimizer-permissions).
owners: [jody@conexus-tech.com]
tags: [qa, authorization, contents, media-optimizer]
---

### Check: media-optimizer-admin-tier
**Requirement:** Only the owner and admin tier administers the optimizer
**Surface:** Cerbos resource `contents:media_optimizer`, actions `create`, `update`, `delete`
**Automated:** tests/test-cases.json

**Do:**
- Evaluate `view`, `create`, `update`, `delete` as a retailer owner, retailer admin, agency owner and agency admin with Signage
- Evaluate `create`, `update`, `delete` as a team lead, retailer member, guest collaborator and agency member with Signage

**Expect:**
- The owner and admin tier is allowed every action (`mo_allow_retailer_owner`, `mo_allow_retailer_admin`, `mo_allow_agency_owner`, `mo_allow_agency_admin`)
- Every other tier is denied every write (`mo_deny_team_lead_write`, `mo_deny_member_write`, `mo_deny_guest_write`, `mo_deny_agency_member_write`)

### Check: media-optimizer-read-tier
**Requirement:** Everyone holding Signage sees scan results and presets
**Surface:** Cerbos resource `contents:media_optimizer`, action `view`
**Automated:** tests/test-cases.json

**Do:**
- Evaluate `view` as a team lead, a retailer member and a guest collaborator with Signage

**Expect:**
- Each is allowed (`mo_allow_team_lead_view`, `mo_allow_member_view`, `mo_allow_guest_view`)

### Check: media-optimizer-excluded
**Requirement:** Brands and retailers without Signage have no optimizer access
**Surface:** Cerbos resource `contents:media_optimizer`
**Automated:** tests/test-cases.json

**Do:**
- Evaluate `view`, `create`, `update`, `delete` as a brand owner with Brand Center and Signage whose retailers include the resource's
- Evaluate the same actions as a retailer owner without Signage

**Expect:**
- The brand owner is denied every action (`mo_deny_brand`)
- The retailer owner without Signage is denied every action (`mo_deny_no_signage`)

### Check: media-optimizer-tenancy-boundary
**Requirement:** Keeping a retailer to its own optimizer is not Cerbos's decision
**Surface:** Cerbos resource `contents:media_optimizer`
**Automated:** tests/test-cases.json

**Do:**
- Evaluate `view`, `create`, `update`, `delete` as the owner of another retailer and agency, with Signage, against a resource carrying a different retailer

**Expect:**
- Every action is allowed (`mo_allow_other_tenant_owner`): the policy has no tenant condition, so api3 must scope each optimizer route to the caller's retailer
