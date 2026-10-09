---
type: Capability
title: Brand creative upload access
description: Cerbos decides who may start a Brand Hub video upload (the Cue Media Optimizer's brand draft route, CMO-0.3) — a brand only into a retailer it belongs to, and only with Brand Center.
owners: [jody@conexus-tech.com]
tags: [authorization, deal-desk, brand-portal, media-optimizer]
---

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
