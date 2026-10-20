---
type: Capability
title: Brand creative upload access
description: Who may start a Brand Hub video upload (the Cue Media Optimizer's brand draft, upload and register routes, CMO-0.3) — a brand only into a retailer it belongs to, and only with Brand Center; api3 asks Cerbos about the brand on each of those routes.
owners: [jody@conexus-tech.com]
tags: [authorization, deal-desk, brand-portal, media-optimizer]
---

api3 asks Cerbos `dealdesk_brand:creatives` `create` on the brand portal's video draft, file
upload and register routes, beside its own brand-context check. The principal is built from the
brand context, never from the caller's own account: a brand member (`userLevel: brand`,
`userType: member`) whose only retailer (`retailerIds`) is the context's retailer, carrying that
retailer's products, with the brand's `brandId`. An operator driving the portal as a brand (the
act-as-brand header) is evaluated as that brand, with the operator's user id as the principal id.
Listing, reporting and editing creatives check no Cerbos action yet — the resource grants only
`create` — and stay under the brand-context check alone. The policy's retailer-path rule (retailer
roles with Brand Center) remains, but these routes do not reach it.

#### Scenario: A brand starts a video upload only into a retailer it belongs to
- GIVEN a brand user with the Brand Center product
- WHEN they start a Brand Hub video upload for a retailer they belong to
- THEN it is allowed
- AND for any other retailer it is denied
- AND without Brand Center it is denied

**Checked by:** brand-creative-upload-tenant

#### Scenario: An operator acting as a brand is decided as that brand
- GIVEN a retailer operator driving the brand portal as one of its brands
- WHEN they start a Brand Hub video upload
- THEN Cerbos decides it as that brand, a member of the retailer being driven, with that retailer's products
- AND it is allowed only when that retailer has Brand Center
- AND starting an upload is the only action the resource grants

**Checked by:** brand-creative-upload-operator
