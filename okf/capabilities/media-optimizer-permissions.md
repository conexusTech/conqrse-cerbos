---
type: Capability
title: Media optimizer administration access
description: Cerbos decides who may administer the Cue Media Optimizer — start a scan, create, edit and delete presets, set advanced settings — and who may only see its scan results and presets.
owners: [jody@conexus-tech.com]
tags: [authorization, contents, signage, media-optimizer]
---

#### Scenario: Only the owner and admin tier administers the optimizer
- GIVEN a retailer owner or admin, or an agency owner or admin, with Signage
- WHEN they start a scan, create or edit a preset, set advanced settings or delete a preset
- THEN it is allowed
- AND a team lead, a retailer member, a guest collaborator or an agency member is denied every one of those

**Checked by:** media-optimizer-admin-tier

#### Scenario: Cerbos lets every Signage holder view, but only owners and admins see the optimizer
- GIVEN a retailer user of any tier with Signage
- WHEN Cerbos is asked whether they may view the optimizer's scan results and presets
- THEN it allows it, including for a team lead, a member and a guest collaborator
- AND in practice only owners and admins see them, because api3 narrows every optimizer route, views included, to owners and admins, and the admin screens show only to owners and admins who hold the write grants

**Checked by:** media-optimizer-read-tier

#### Scenario: Brands and retailers without Signage have no optimizer access
- GIVEN a brand user, even with Signage and the retailer among its own
- OR a retailer owner without Signage
- WHEN they view, scan, set advanced settings or manage presets
- THEN every action is denied

**Checked by:** media-optimizer-excluded

#### Scenario: Keeping a retailer to its own optimizer is not Cerbos's decision
- GIVEN the owner of another retailer, with Signage
- WHEN Cerbos is asked about the optimizer
- THEN it decides on role and product alone, as for every collection resource
- AND scoping each optimizer request to the caller's own retailer is left to api3

**Checked by:** media-optimizer-tenancy-boundary
