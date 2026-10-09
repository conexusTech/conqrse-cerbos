---
type: Capability
title: Brand creative upload access
description: The policy for who may start a Brand Hub video upload (the Cue Media Optimizer's brand draft route, CMO-0.3) — a brand only into a retailer it belongs to, and only with Brand Center. Verified as policy; api3 does not check it yet (Drexel #36).
owners: [jody@conexus-tech.com]
tags: [authorization, deal-desk, brand-portal, media-optimizer]
---

The policy is in place and tested, but api3 does not ask Cerbos about it yet: Cerbos cannot
evaluate a brand user today (api3's guard looks callers up in `users`, and BrandUser carries no
role for the `brand_*` derived roles — Drexel #36). Until then the brand portal's own context
check protects the route. As in every generated retailer-path policy, the operator rule carries no
retailer condition; tenancy for operators is enforced in api3.

#### Scenario: A brand starts a video upload only into a retailer it belongs to
- GIVEN a brand user with the Brand Center product
- WHEN they start a Brand Hub video upload for a retailer they belong to
- THEN it is allowed
- AND for any other retailer it is denied
- AND without Brand Center it is denied

**Checked by:** brand-creative-upload-tenant

#### Scenario: An operator acting as a brand needs Brand Center
- GIVEN a retailer operator driving the brand portal as one of its brands
- WHEN they start a Brand Hub video upload
- THEN it is allowed only when the retailer has Brand Center
- AND starting an upload is the only action the resource grants

**Checked by:** brand-creative-upload-operator
