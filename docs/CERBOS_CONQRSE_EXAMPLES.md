# Cerbos Conqrse - Validation Examples

This document contains real-world Cerbos validation payload examples for the "Act AS" delegation model, grouped by expected result.

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
  "action": "resource:list"
}
```

**Expected**: ALLOW
**Reason**: Member can list resources in their retailer, and product is in their products list.

---

### Scenario 2: SU Admin Acting AS Retailer Admin Creating a User

**Context**: Super user with admin type delegating to act as a retailer admin to create a new retailer user.

```json
{
  "principal": {
    "id": "su-user-001",
    "userLevel": "su",
    "userType": "admin",
    "name": "admin@platform.com",
    "products": ["footprints", "signage", "qr"],
    "actingAs": {
      "level": "retailer",
      "retailerId": "retail-789"
    }
  },
  "resource": {
    "name": "settings:admin:users",
    "product": "settings",
    "retailerId": "retail-789"
  },
  "action": "settings:create"
}
```

**Expected**: ALLOW
**Reason**: When acting AS, SU Admin becomes Retailer Admin with full settings access.

---

### Scenario 3: Agency Admin Acting AS Retailer Creating QR Campaign

**Context**: Agency-level admin delegating to act as retailer admin to create a campaign.

```json
{
  "principal": {
    "id": "agency-user-002",
    "userLevel": "agency",
    "userType": "admin",
    "name": "manager@agency.com",
    "products": ["footprints", "qr"],
    "agencyId": "agency-456",
    "actingAs": {
      "level": "retailer",
      "retailerId": "retail-789",
      "agencyId": "agency-456"
    }
  },
  "resource": {
    "name": "qr:campaigns",
    "product": "qr",
    "retailerId": "retail-789",
    "agencyId": "agency-456"
  },
  "action": "resource:create"
}
```

**Expected**: ALLOW
**Reason**: Agency Admin acting AS becomes Retailer Admin, can create resources in child retailers.

---

### Scenario 4: Agency Owner Creating a User for Child Retailer

**Context**: Agency owner creating a new user account within a child retailer.

```json
{
  "principal": {
    "id": "agency-user-001",
    "userLevel": "agency",
    "userType": "owner",
    "name": "owner@agency.com",
    "products": ["footprints", "signage", "qr"],
    "agencyId": "agency-456"
  },
  "resource": {
    "name": "settings:admin:users",
    "product": "settings",
    "retailerId": "retail-789",
    "agencyId": "agency-456"
  },
  "action": "settings:create"
}
```

**Expected**: ALLOW
**Reason**: Agency Owner can create users for child retailers directly, no "Act AS" needed.

---

### Scenario 7: SU Owner Managing Agency Configuration

**Context**: Super user with owner type accessing SU-level settings (system configuration).

```json
{
  "principal": {
    "id": "su-user-000",
    "userLevel": "su",
    "userType": "owner",
    "name": "owner@platform.com",
    "products": ["footprints", "signage", "qr"]
  },
  "resource": {
    "name": "settings:admin:general",
    "product": "settings"
  },
  "action": "settings:update"
}
```

**Expected**: ALLOW
**Reason**: SU Owner has full settings access at the SU level.

---

### Scenario 8: SU Lead Viewing System Data

**Context**: SU lead user viewing system-level reports (read-mostly access).

```json
{
  "principal": {
    "id": "su-user-003",
    "userLevel": "su",
    "userType": "lead",
    "name": "lead@platform.com",
    "products": ["footprints", "signage", "qr"]
  },
  "resource": {
    "name": "dashboards:su-dashboard",
    "product": "dashboards"
  },
  "action": "resource:view"
}
```

**Expected**: ALLOW
**Reason**: SU Lead can view resources at the SU level.

---

### Scenario 9: SU Collaborator Acting AS Retailer Member

**Context**: SU collaborator (read-only) delegating to act as retailer member (still read-only).

```json
{
  "principal": {
    "id": "su-user-004",
    "userLevel": "su",
    "userType": "collaborator",
    "name": "viewer@platform.com",
    "products": ["qr"],
    "actingAs": {
      "level": "retailer",
      "retailerId": "retail-789"
    }
  },
  "resource": {
    "name": "qr:campaigns",
    "product": "qr",
    "retailerId": "retail-789"
  },
  "action": "resource:view"
}
```

**Expected**: ALLOW
**Reason**: SU Collaborator acting AS becomes Retailer Collaborator (read-only), can view but not create.

---

### Scenario 10: Agency Lead Acting AS Retailer Creating Resources

**Context**: Agency lead (supervisory) acting as retailer to create a campaign.

```json
{
  "principal": {
    "id": "agency-user-003",
    "userLevel": "agency",
    "userType": "lead",
    "name": "lead@agency.com",
    "products": ["qr"],
    "agencyId": "agency-456",
    "actingAs": {
      "level": "retailer",
      "retailerId": "retail-789",
      "agencyId": "agency-456"
    }
  },
  "resource": {
    "name": "qr:campaigns",
    "product": "qr",
    "retailerId": "retail-789",
    "agencyId": "agency-456"
  },
  "action": "resource:create"
}
```

**Expected**: ALLOW
**Reason**: Agency Lead acting AS becomes Retailer Lead with full resource permissions (no settings).

---

### Scenario 11: Agency Member Viewing Child Retailer Resources

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
  "action": "resource:list"
}
```

**Expected**: ALLOW
**Reason**: Agency Member can list resources for child retailers (bypasses product check at agency level).

---

### Scenario 12: Agency Collaborator Viewing Agency Dashboard

**Context**: Agency collaborator accessing read-only agency-level dashboard.

```json
{
  "principal": {
    "id": "agency-user-005",
    "userLevel": "agency",
    "userType": "collaborator",
    "name": "viewer@agency.com",
    "products": ["qr"],
    "agencyId": "agency-456"
  },
  "resource": {
    "name": "dashboards:agency-dashboard",
    "product": "dashboards"
  },
  "action": "resource:view"
}
```

**Expected**: ALLOW
**Reason**: Agency Collaborator can view resources at agency level (read-only).

---

### Scenario 13: Retailer Owner Managing Store Settings

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
  "action": "settings:update"
}
```

**Expected**: ALLOW
**Reason**: Retailer Owner has full settings access at retailer level.

---

### Scenario 14: Retailer Admin Creating QR Codes

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
  "action": "resource:create"
}
```

**Expected**: ALLOW
**Reason**: Retailer Admin can create resources and manage settings.

---

### Scenario 15: Retailer Lead Exporting Campaign Data

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
  "action": "resource:export"
}
```

**Expected**: ALLOW
**Reason**: Retailer Lead can export resources (no settings access).

---

### Scenario 16: Retailer Collaborator Viewing Campaigns

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
  "action": "resource:view"
}
```

**Expected**: ALLOW
**Reason**: Retailer Collaborator can view and export resources (read-only access).

---

## Deny - Examples

These scenarios demonstrate cases where Cerbos should return **DENY**.

### Scenario 5: Retailer Collaborator Attempting to Create

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
  "action": "resource:create"
}
```

**Expected**: DENY
**Reason**: Collaborators can only list, view, and export. Create action not permitted.

---

### Scenario 6: Retailer Member Accessing Product Not in Subscription

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
    "name": "signage:content:templates",
    "product": "signage",
    "retailerId": "retail-789",
    "agencyId": "agency-456"
  },
  "action": "resource:list"
}
```

**Expected**: DENY
**Reason**: Signage product is not in the user's products array. Product subscription validation failed.

---

### Scenario 17: SU Collaborator Attempting to Create Settings

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
  "action": "settings:create"
}
```

**Expected**: DENY
**Reason**: Collaborators are read-only and cannot create settings.

---

### Scenario 18: Agency Lead Attempting to Modify Settings

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
  "action": "settings:create"
}
```

**Expected**: DENY
**Reason**: Lead users do not have access to settings (only owner/admin).

---

### Scenario 19: Agency Collaborator Attempting to Create Resource

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
  "action": "resource:create"
}
```

**Expected**: DENY
**Reason**: Collaborators can only list, view, and export. No create permission.

---

### Scenario 20: Retailer Lead Attempting to Modify Settings

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
  "action": "settings:update"
}
```

**Expected**: DENY
**Reason**: Lead users do not have settings access at retailer level.

---

### Scenario 21: Agency User Acting AS Unrelated Retailer

**Context**: Agency admin attempting to act as a retailer that is not a child of their agency.

```json
{
  "principal": {
    "id": "agency-user-008",
    "userLevel": "agency",
    "userType": "admin",
    "name": "manager@agency-a.com",
    "products": ["qr"],
    "agencyId": "agency-456",
    "actingAs": {
      "level": "retailer",
      "retailerId": "retail-999",
      "agencyId": "agency-999"
    }
  },
  "resource": {
    "name": "qr:campaigns",
    "product": "qr",
    "retailerId": "retail-999",
    "agencyId": "agency-999"
  },
  "action": "resource:list"
}
```

**Expected**: DENY
**Reason**: Agency user can only act as retailers that are children of their agency. This retailer belongs to a different agency.

---

### Scenario 22: Retailer User Attempting to Act AS Another Retailer

**Context**: Retailer staff attempting to act as another retailer (retailer users cannot delegate).

```json
{
  "principal": {
    "id": "user-205",
    "userLevel": "retailer",
    "userType": "member",
    "name": "staff@retailer-a.com",
    "products": ["qr"],
    "agencyId": "agency-456",
    "retailerId": "retail-789",
    "actingAs": {
      "level": "retailer",
      "retailerId": "retail-999"
    }
  },
  "resource": {
    "name": "qr:campaigns",
    "product": "qr",
    "retailerId": "retail-999"
  },
  "action": "resource:list"
}
```

**Expected**: DENY
**Reason**: Retailer-level users cannot use Act AS delegation. Only SU and Agency can delegate.

---
