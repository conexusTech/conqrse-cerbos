---
type: QA Checklist
title: Brand creative upload access — checks
description: Proof contract for the dealdesk_brand:creatives resource (Cue Media Optimizer CMO-0.3).
owners: [jody@conexus-tech.com]
tags: [qa, authorization, deal-desk, brand-portal]
---

### Check: brand-creative-upload-tenant
**Requirement:** A brand starts a video upload only into a retailer it belongs to
**Surface:** Cerbos resource `dealdesk_brand:creatives`, action `create`
**Automated:** tests/test-cases.json

**Do:**
- Evaluate `create` as a brand member with Brand Center against its own retailer and another retailer, and without Brand Center

**Expect:**
- Its own retailer is allowed (`dd_brand_creatives_allow_1`)
- Another retailer is denied (`dd_brand_creatives_deny_1`)
- No Brand Center is denied (`dd_brand_creatives_deny_2`)

### Check: brand-creative-upload-operator
**Requirement:** An operator acting as a brand needs Brand Center
**Surface:** Cerbos resource `dealdesk_brand:creatives`
**Automated:** tests/test-cases.json

**Do:**
- Evaluate `create` as a retailer owner with and without Brand Center, and `delete` as a brand member

**Expect:**
- With Brand Center the owner is allowed (`dd_brand_creatives_allow_2`); without it, denied (`dd_brand_creatives_deny_3`)
- `delete` is denied (`dd_brand_creatives_deny_4`)
