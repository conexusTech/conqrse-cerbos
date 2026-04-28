# Cerbos Conqrse - Validation Examples

This document contains real-world Cerbos validation payload examples, grouped by expected result.

## Allow - Examples

These scenarios demonstrate cases where Cerbos should return **ALLOW**.

### Scenario 1: Retailer Member Listing QR Campaigns (Direct Access)

**Context**: Retailer-level user viewing campaigns in their own retailer.

```json
{
  "principal": {
    "id": "user-123",
    "userLevel": "retailer",
    "userType": "member",
    "name": "john.doe",
    "products": ["qr"],
    "agencyId": "agency-456",
    "retailerId": "retail-789"
  },
  "resource": {
    "name": "qr:campaigns",
    "product": "qr",
    "retailerId": "retail-789",
    "agencyId": "agency-456"
  },
  "action": "list"
}
```

**Expected**: ALLOW
**Reason**: Member can list resources in their retailer, and product is in their products list.

---

### Scenario 2: Agency Admin Creating QR Campaign for Child Retailer

**Context**: Agency-level admin creating a campaign for a child retailer.

```json
{
  "principal": {
    "id": "agency-user-002",
    "userLevel": "agency",
    "userType": "admin",
    "name": "manager@agency.com",
    "products": ["footprints", "qr"],
    "agencyId": "agency-456"
  },
  "resource": {
    "name": "qr:campaigns",
    "product": "qr",
    "retailerId": "retail-789",
    "agencyId": "agency-456"
  },
  "action": "create"
}
```

**Expected**: ALLOW
**Reason**: Agency Admin can create resources in child retailers.

---

### Scenario 3: Agency Owner Creating a User for Child Retailer

**Context**: Agency owner creating a new user account within a child retailer.

```json
{
  "principal": {
    "id": "agency-user-001",
    "userLevel": "agency",
    "userType": "owner",
    "name": "owner@agency.com",
    "products": ["footprints", "signages", "qr"],
    "agencyId": "agency-456"
  },
  "resource": {
    "name": "settings:admin:users",
    "product": "settings",
    "retailerId": "retail-789",
    "agencyId": "agency-456"
  },
  "action": "create"
}
```

**Expected**: ALLOW
**Reason**: Agency Owner can create users for child retailers.

---

### Scenario 4: SU Owner Managing Platform Configuration

**Context**: Super user with owner type accessing SU-level settings (system configuration).

```json
{
  "principal": {
    "id": "su-user-000",
    "userLevel": "su",
    "userType": "owner",
    "name": "owner@platform.com",
    "products": ["footprints", "signages", "qr"]
  },
  "resource": {
    "name": "settings:admin:general",
    "product": "settings"
  },
  "action": "update"
}
```

**Expected**: ALLOW
**Reason**: SU Owner has full settings access at the SU level.

---

### Scenario 5: SU Lead Viewing System Reports

**Context**: SU lead user viewing system-level reports (read-mostly access).

```json
{
  "principal": {
    "id": "su-user-003",
    "userLevel": "su",
    "userType": "lead",
    "name": "lead@platform.com",
    "products": ["footprints", "signages", "qr"]
  },
  "resource": {
    "name": "reports:qr-performance",
    "product": "reports"
  },
  "action": "view"
}
```

**Expected**: ALLOW
**Reason**: SU Lead can view reports at the SU level.

---

### Scenario 6: Retailer Member Accessing Contents Templates

**Context**: Retailer member accessing templates from the Contents product.

```json
{
  "principal": {
    "id": "user-206",
    "userLevel": "retailer",
    "userType": "member",
    "name": "staff@retailer.com",
    "products": ["contents", "qr"],
    "agencyId": "agency-456",
    "retailerId": "retail-789"
  },
  "resource": {
    "name": "contents:templates",
    "product": "contents",
    "retailerId": "retail-789",
    "agencyId": "agency-456"
  },
  "action": "list"
}
```

**Expected**: ALLOW
**Reason**: Member can list resources in their retailer, and contents product is in their products list.

---

### Scenario 7: Agency Manager Accessing Signages People for Child Retailer

**Context**: Agency manager accessing signages people for a child retailer.

```json
{
  "principal": {
    "id": "agency-user-003",
    "userLevel": "agency",
    "userType": "admin",
    "name": "manager@agency.com",
    "products": ["signages", "qr"],
    "agencyId": "agency-456"
  },
  "resource": {
    "name": "signages:people",
    "product": "signages",
    "retailerId": "retail-789",
    "agencyId": "agency-456"
  },
  "action": "create"
}
```

**Expected**: ALLOW
**Reason**: Agency Admin can create resources in child retailers.

---

### Scenario 8: Agency Member Viewing Child Retailer Resources

**Context**: Agency member viewing resources from a child retailer.

```json
{
  "principal": {
    "id": "agency-user-004",
    "userLevel": "agency",
    "userType": "member",
    "name": "operator@agency.com",
    "products": ["footprints", "qr"],
    "agencyId": "agency-456"
  },
  "resource": {
    "name": "footprints:sites",
    "product": "footprints",
    "retailerId": "retail-789",
    "agencyId": "agency-456"
  },
  "action": "list"
}
```

**Expected**: ALLOW
**Reason**: Agency Member can list resources for child retailers.

---

### Scenario 9: Retailer Owner Managing Store Settings

**Context**: Retailer owner updating store-level configuration.

```json
{
  "principal": {
    "id": "user-200",
    "userLevel": "retailer",
    "userType": "owner",
    "name": "owner@retailer.com",
    "products": ["footprints", "qr"],
    "agencyId": "agency-456",
    "retailerId": "retail-789"
  },
  "resource": {
    "name": "settings:admin:general",
    "product": "settings",
    "retailerId": "retail-789"
  },
  "action": "update"
}
```

**Expected**: ALLOW
**Reason**: Retailer Owner has full settings access at retailer level.

---

### Scenario 10: Retailer Admin Creating QR Codes

**Context**: Retailer manager (admin) creating new QR campaigns.

```json
{
  "principal": {
    "id": "user-201",
    "userLevel": "retailer",
    "userType": "admin",
    "name": "manager@retailer.com",
    "products": ["qr"],
    "agencyId": "agency-456",
    "retailerId": "retail-789"
  },
  "resource": {
    "name": "qr:campaigns",
    "product": "qr",
    "retailerId": "retail-789",
    "agencyId": "agency-456"
  },
  "action": "create"
}
```

**Expected**: ALLOW
**Reason**: Retailer Admin can create resources and manage settings.

---

### Scenario 11: Retailer Lead Exporting Campaign Data

**Context**: Team lead exporting campaign performance data.

```json
{
  "principal": {
    "id": "user-202",
    "userLevel": "retailer",
    "userType": "lead",
    "name": "lead@retailer.com",
    "products": ["qr"],
    "agencyId": "agency-456",
    "retailerId": "retail-789"
  },
  "resource": {
    "name": "qr:campaigns",
    "product": "qr",
    "retailerId": "retail-789",
    "agencyId": "agency-456"
  },
  "action": "export"
}
```

**Expected**: ALLOW
**Reason**: Retailer Lead can export resources (no settings access).

---

### Scenario 12: Retailer Collaborator Viewing Campaigns

**Context**: Guest/external collaborator viewing campaign information (read-only).

```json
{
  "principal": {
    "id": "user-203",
    "userLevel": "retailer",
    "userType": "collaborator",
    "name": "guest@retailer.com",
    "products": ["qr"],
    "agencyId": "agency-456",
    "retailerId": "retail-789"
  },
  "resource": {
    "name": "qr:campaigns",
    "product": "qr",
    "retailerId": "retail-789",
    "agencyId": "agency-456"
  },
  "action": "view"
}
```

**Expected**: ALLOW
**Reason**: Retailer Collaborator can view and export resources (read-only access).

---

### Scenario 13: Retailer Member Accessing Signages Places

**Context**: Retailer member accessing signages places.

```json
{
  "principal": {
    "id": "user-207",
    "userLevel": "retailer",
    "userType": "member",
    "name": "staff@retailer.com",
    "products": ["signages", "qr"],
    "agencyId": "agency-456",
    "retailerId": "retail-789"
  },
  "resource": {
    "name": "signages:places",
    "product": "signages",
    "retailerId": "retail-789",
    "agencyId": "agency-456"
  },
  "action": "view"
}
```

**Expected**: ALLOW
**Reason**: Member can view resources in their retailer, and signages product is in their products list.

---

## Deny - Examples

These scenarios demonstrate cases where Cerbos should return **DENY**.

### Scenario 14: Retailer Collaborator Attempting to Create

**Context**: Retail-level collaborator trying to create a resource (collaborators are read-only).

```json
{
  "principal": {
    "id": "user-456",
    "userLevel": "retailer",
    "userType": "collaborator",
    "name": "guest@retailer.com",
    "products": ["qr"],
    "agencyId": "agency-456",
    "retailerId": "retail-789"
  },
  "resource": {
    "name": "qr:campaigns",
    "product": "qr",
    "retailerId": "retail-789",
    "agencyId": "agency-456"
  },
  "action": "create"
}
```

**Expected**: DENY
**Reason**: Collaborators can only list, view, and export. Create action not permitted.

---

### Scenario 15: Retailer Member Accessing Product Not in Subscription

**Context**: Retailer user trying to access a product they're not subscribed to.

```json
{
  "principal": {
    "id": "user-789",
    "userLevel": "retailer",
    "userType": "member",
    "name": "staff@retailer.com",
    "products": ["qr"],
    "agencyId": "agency-456",
    "retailerId": "retail-789"
  },
  "resource": {
    "name": "contents:templates",
    "product": "contents",
    "retailerId": "retail-789",
    "agencyId": "agency-456"
  },
  "action": "list"
}
```

**Expected**: DENY
**Reason**: Contents product is not in the user's products array. Product subscription validation failed.

---

### Scenario 16: SU Collaborator Attempting to Create Settings

**Context**: SU collaborator (read-only) trying to create a system setting (not permitted).

```json
{
  "principal": {
    "id": "su-user-005",
    "userLevel": "su",
    "userType": "collaborator",
    "name": "viewer@platform.com",
    "products": ["footprints"]
  },
  "resource": {
    "name": "settings:admin:general",
    "product": "settings"
  },
  "action": "create"
}
```

**Expected**: DENY
**Reason**: Collaborators are read-only and cannot create settings.

---

### Scenario 17: Agency Lead Attempting to Modify Settings

**Context**: Agency lead trying to update agency settings (leads cannot modify settings).

```json
{
  "principal": {
    "id": "agency-user-006",
    "userLevel": "agency",
    "userType": "lead",
    "name": "lead@agency.com",
    "products": ["qr"],
    "agencyId": "agency-456"
  },
  "resource": {
    "name": "settings:admin:users",
    "product": "settings",
    "agencyId": "agency-456"
  },
  "action": "create"
}
```

**Expected**: DENY
**Reason**: Lead users do not have access to settings (only owner/admin).

---

### Scenario 18: Agency Collaborator Attempting to Create Resource

**Context**: Agency collaborator trying to create a resource (collaborators are read-only).

```json
{
  "principal": {
    "id": "agency-user-007",
    "userLevel": "agency",
    "userType": "collaborator",
    "name": "viewer@agency.com",
    "products": ["qr"],
    "agencyId": "agency-456"
  },
  "resource": {
    "name": "qr:campaigns",
    "product": "qr",
    "agencyId": "agency-456"
  },
  "action": "create"
}
```

**Expected**: DENY
**Reason**: Collaborators can only list, view, and export. No create permission.

---

### Scenario 19: Retailer Lead Attempting to Modify Settings

**Context**: Retailer team lead trying to update store settings (leads cannot modify settings).

```json
{
  "principal": {
    "id": "user-204",
    "userLevel": "retailer",
    "userType": "lead",
    "name": "lead@retailer.com",
    "products": ["qr"],
    "agencyId": "agency-456",
    "retailerId": "retail-789"
  },
  "resource": {
    "name": "settings:admin:general",
    "product": "settings",
    "retailerId": "retail-789"
  },
  "action": "update"
}
```

**Expected**: DENY
**Reason**: Lead users do not have settings access at retailer level.

---

### Scenario 20: Agency User Accessing Unrelated Retailer Resources

**Context**: Agency admin attempting to access a retailer that is not a child of their agency.

```json
{
  "principal": {
    "id": "agency-user-008",
    "userLevel": "agency",
    "userType": "admin",
    "name": "manager@agency-a.com",
    "products": ["qr"],
    "agencyId": "agency-456"
  },
  "resource": {
    "name": "qr:campaigns",
    "product": "qr",
    "retailerId": "retail-999",
    "agencyId": "agency-999"
  },
  "action": "list"
}
```

**Expected**: DENY
**Reason**: Agency user can only access resources for retailers that are children of their agency. This retailer belongs to a different agency.

---

### Scenario 21: Retailer User Attempting to Access Another Retailer

**Context**: Retailer staff attempting to access another retailer's resources.

```json
{
  "principal": {
    "id": "user-205",
    "userLevel": "retailer",
    "userType": "member",
    "name": "staff@retailer-a.com",
    "products": ["qr"],
    "agencyId": "agency-456",
    "retailerId": "retail-789"
  },
  "resource": {
    "name": "qr:campaigns",
    "product": "qr",
    "retailerId": "retail-999",
    "agencyId": "agency-456"
  },
  "action": "list"
}
```

**Expected**: DENY
**Reason**: Retailer-level users can only access resources scoped to their own retailer.

---
