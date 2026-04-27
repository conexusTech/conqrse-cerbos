
# Cerbos Conqrse - Resource Baseline

This document defines the Conqrse Role-Based Permission Access logic.

## Supported Products

The following products are supported by Cerbos authorization, identified by the first segment in resource names:

| Product | Resource Prefix | Key Resources |
|---------|-----------------|----------------|
| **Footprints** | `footprints:` | sites, endpoints, products, pricing |
| **Signages** | `signages:` | people, places, things |
| **Contents** | `contents:` | templates, assets, playlists, channels, tags, content-groups, backgrounds |
| **QR** | `qr:` | site, media, templates, campaigns |
| **Reports** | `reports:` | qr-performance, campaign-compliance, site-performance-maps, export |
| **Connect** | `connect:` | contacts |

**Administrative & Configuration Features** (not products):
- `settings:` — Configuration and settings management (cross-cutting concern, see [Resource Naming Patterns](#resource-naming-patterns))

## Resource Naming Patterns

### Settings: Cross-Cutting Concern

Settings resources use the `settings:{context}_{resource}` pattern (underscore-separated) as a **cross-cutting concern**, separate from product resources. This architectural decision enables:

1. **Unified Authorization** — All settings follow consistent access control patterns in a single place
2. **Scalability** — Adding new products doesn't require new settings policies
3. **Consistency** — Every product-level and admin-level setting follows the same semantic structure
4. **Maintainability** — Settings logic is not duplicated across product namespaces

**Pattern:**
- `settings:admin:*` — Platform/system-level settings (owners/admins only)
- `settings:user:*` — User-specific settings (personal profile, preferences)
- `settings:{product}_{feature}` — Product-specific configuration (e.g., `settings:qr_design`, `settings:signage_layout`)
- `settings:{product}_{feature}_{category}` — Sub-categories within product settings

**Example:**
```
settings:admin:general              ← Platform-wide configuration
settings:admin:users                ← User management
settings:admin:teams                ← Team management
settings:qr_design                  ← QR design settings
settings:qr_power-tag               ← QR power-tag settings
settings:signage_layout             ← Signage layout settings
settings:signage_people_property    ← Signage people property settings
settings:footprints_sites_property  ← Footprints site property settings
settings:user:profile               ← User profile/preferences
```

**Why NOT `product:settings`?**
- ❌ Leads to repetitive policy patterns
- ❌ Harder to enforce platform-wide settings governance
- ❌ Settings and product access have different rules (should be separated)
- ❌ Violates separation of concerns

## Resources

| Resource | Admin Route | Client Component | Actions |
|----------|-------------|------------------|---------|
| footprints:sites | `/footprint/sites` | `SitesClient.tsx` | list, view, create, update, delete, export, import |
| footprints:sites:item | `/footprint/sites/[id]` | `SiteDetailClient.tsx` | view, update, delete |
| footprints:endpoints | `/footprint/endpoints` | `MediaPlayersClient.tsx` | list, view, create, update, delete, export, import |
| footprints:endpoints:item | `/footprint/endpoints/[endpointId]` | `MediaPlayerDetailClient.tsx` | view, update, delete |
| footprints:products | `/footprint/products` | `ProductsClient.tsx` | list, view, create, update, delete, export, import |
| footprints:products:item | `/footprint/products/[id]` | `ProductDetailClient.tsx` | view, update, delete |
| footprints:pricing | `/footprint/pricing` | `PricingClient.tsx` | list, view, create, update, delete, export, import |
| contents:templates | `/content/templates` | `TemplatesClient.tsx` | list, view, create, update, delete, export, import |
| contents:templates:item | `/content/templates/[id]` | `TemplateDetailClient.tsx` | view, update, delete |
| contents:assets | `/content/assets` | `PlaylistAssetsClient.tsx` | list, view, create, update, delete, export, import |
| contents:assets:item | `/content/assets` | `PlaylistAssetsClient.tsx` | view, update, delete |
| contents:playlists | `/content/playlists` | `PlaylistConfigsClient.tsx` | list, view, create, update, delete, export, import |
| contents:playlists:item | `/content/playlists/[playlistConfigId]` | `ManagePlaylistConfigClient.tsx` | view, update, delete |
| contents:backgrounds | `/content/backgrounds` | `BackgroundsClient.tsx` | list, view, create, update, delete, export, import |
| contents:backgrounds:item | `/content/backgrounds` | `BackgroundsClient.tsx` | view, update, delete |
| contents:channels | `/content/channels` | `MediaPlayerChannelsClient.tsx` | list, view, create, update, delete, export, import |
| contents:channels:item | `/content/channels/[id]` | `MediaPlayerChannelDetailClient.tsx` | view, update, delete |
| contents:tags | `/content/tags` | `TagManagerClient.tsx` | list, view, create, update, delete, export, import |
| contents:tags:item | `/content/tags` | `TagManagerClient.tsx` | view, update, delete |
| contents:content-groups | `/content/content-groups` | `ContentGroupsClient.tsx` | list, view, create, update, delete, export, import |
| contents:content-groups:item | `/content/content-groups/[id]` | `ManageContentGroupClient.tsx` | view, update, delete |
| signages:people | `/signages/people` | `SignagePeopleClient.tsx` | list, view, create, update, delete, export, import |
| signages:people:item | `/signages/people` | `SignagePeopleClient.tsx` | view, update, delete |
| signages:places | `/signages/places` | `SignagePlacesClient.tsx` | list, view, create, update, delete, export, import |
| signages:places:item | `/signages/places` | `SignagePlacesClient.tsx` | view, update, delete |
| signages:things | `/signages/things` | `SignageThingsClient.tsx` | list, view, create, update, delete, export, import |
| signages:things:item | `/signages/things` | `SignageThingsClient.tsx` | view, update, delete |
| qr:site | `/qr/site` | `ManagedSiteQrClient.tsx` | list, view, create, update, delete, export, import |
| qr:site:item | `/qr/site/[id]` | `ManagedSiteQrDetailClient.tsx` | view, update, delete |
| qr:media | `/qr/media` | `ManageMediaQrClient.tsx` | list, view, create, update, delete, export, import |
| qr:media:item | `/qr/media/[id]` | `ManageMediaQrDetailClient.tsx` | view, update, delete |
| qr:templates | `/qr/templates` | `QrTemplatesClient.tsx` | list, view, create, update, delete, export, import |
| qr:templates:item | `/qr/templates/[id]` | `QrTemplateDetailClient.tsx` | view, update, delete |
| qr:campaigns | `/qr/campaigns` | `CampaignsClient.tsx` | list, view, create, update, delete, export, import |
| qr:campaigns:item | `/qr/campaigns/[id]` | `CampaignsClient.tsx` | view, update, delete |
| reports:qr-performance | `/reports/qr-performance` | `QRPerformanceAnalysisClient.tsx` | list, view, export |
| reports:qr-performance-site-to-site | `/reports/qr-performance-site-to-site` | `QRSiteAnalysisClient.tsx` | list, view, export |
| reports:campaign-compliance | `/reports/campaign-compliance` | `CampaignComplianceClient.tsx` | list, view, export |
| reports:campaign-compliance-details | `/reports/campaign-compliance-details` | `CampaignComplianceDetailsClient.tsx` | list, view, export |
| reports:site-performance-maps | `/reports/site-performance-maps` | `SitePerformanceMapsClient.tsx` | list, view, export |
| reports:media-performance-maps | `/reports/media-performance-maps` | `MediaPerformanceClient.tsx` | list, view, export |
| reports:campaign-performance-maps | `/reports/campaign-performance-maps` | `CampaignPerformanceMapsClient.tsx` | list, view, export |
| reports:content-proof-of-play | `/reports/content-proof-of-play` | `ContentProofOfPlayClient.tsx` | list, view, export |
| reports:export | `/export` | `BatchClient.tsx` | export |
| connect:contacts | `/connect/contacts` | `ContactsClient.tsx` | list, view, create, update, delete, export, import |
| connect:contacts:item | `/connect/contacts/[id]` | `ContactsClient.tsx` | view, update, delete |
| settings:admin:general | `/settings/general` | `GeneralSettingsClient.tsx` | list, view, create, update, delete |
| settings:admin:users | `/settings/users` | `UserSettingsClient.tsx` | list, view, create, update, delete, export, import |
| settings:admin:teams | `/settings/teams` | `TeamSettingsClient.tsx` | list, view, create, update, delete, export, import |
| settings:admin:cerbos | `/settings/cerbos` | `CerbosSettingsClient.tsx` | list, view, update, export, import |
| settings:user:profile | `/profile` | `ProfileClient.tsx` | list, view, update |
| settings:footprints_sites_property | `/settings/footprint` | `FootprintSettingsClient.tsx` | list, view, create, update, delete, export, import |
| settings:footprints_sites_property:item | `/settings/footprint` | `FootprintSettingsClient.tsx` | view, update, delete |
| settings:footprints_products_property | `/settings/product` | `ProductSettingsClient.tsx` | list, view, create, update, delete, export, import |
| settings:footprints_products_property:item | `/settings/product` | `ProductSettingsClient.tsx` | view, update, delete |
| settings:footprints_products_pricing_group | `/settings/price-tag` | `PriceTagSettingsClient.tsx` | list, view, create, update, delete, export, import |
| settings:footprints_products_pricing_group:item | `/settings/price-tag` | `PriceTagSettingsClient.tsx` | view, update, delete |
| settings:qr_design | `/settings/qr` | `QrSettingsClient.tsx` | list, view, create, update, delete, export, import |
| settings:qr_design:item | `/settings/qr` | `QrSettingsClient.tsx` | view, update, delete |
| settings:qr_power-tag | `/settings/qr` | `QrSettingsClient.tsx` | list, view, create, update, delete, export, import |
| settings:qr_power-tag:item | `/settings/qr` | `QrSettingsClient.tsx` | view, update, delete |
| settings:qr_default-redirect | `/settings/qr` | `QrSettingsClient.tsx` | list, view, create, update, delete |
| settings:qr_domain | `/settings/qr` | `QrSettingsClient.tsx` | list, view, create, update, delete, export, import |
| settings:qr_domain:item | `/settings/qr` | `QrSettingsClient.tsx` | view, update, delete |
| settings:signage_layout | `/settings/signage` | `SignageSettingsClient.tsx` | list, view, create, update, delete, export, import |
| settings:signage_layout:item | `/settings/signage` | `SignageSettingsClient.tsx` | view, update, delete |
| settings:signage_people_property | `/settings/properties-manager/people` | `PeoplePropertiesClient.tsx` | list, view, create, update, delete, export, import |
| settings:signage_people_property:item | `/settings/properties-manager/people` | `PeoplePropertiesClient.tsx` | view, update, delete |
| settings:signage_places_property | `/settings/properties-manager/places` | `PlacePropertiesClient.tsx` | list, view, create, update, delete, export, import |
| settings:signage_places_property:item | `/settings/properties-manager/places` | `PlacePropertiesClient.tsx` | view, update, delete |
| settings:signage_things_property | `/settings/properties-manager/things` | `ThingPropertiesClient.tsx` | list, view, create, update, delete, export, import |
| settings:signage_things_property:item | `/settings/properties-manager/things` | `ThingPropertiesClient.tsx` | view, update, delete |

## Actions

| Action | Type | Description |
|--------|------|-------------|
| **Create** | Write | Create new resources (POST operations) |
| **List** | Read | View collection of resources with filters and pagination (GET list operations) |
| **View** | Read | View individual resource details (GET detail operations) |
| **Update** | Write | Modify existing resources (PUT/PATCH operations) |
| **Delete** | Write | Remove resources from the system (DELETE operations) |
| **Export** | Read | Download/export resource data (GET export operations) |
| **Import** | Write | Upload/import data to create or update resources (POST/PUT bulk operations) |

### Summary
- **Read Operations**: List, View, Export — Safe operations that do not modify data
- **Write Operations**: Create, Update, Delete, Import — Operations that create, modify, or remove data

## User Dimensions

Every user has two attributes that determine access:

| Dimension | Values | Purpose |
|-----------|--------|---------|
| **userLevel** | `su`, `agency`, `retailer` | Organizational scope — what data you can see |
| **userType** | `owner`, `admin`, `lead`, `member`, `collaborator` | Permission role — what actions you can perform |

### First Dimension: User Level Scoping & Access Model

#### Super User (SU) Level
- **Direct Actions**: Create/manage agencies, view all system data at SU level, manage SU-level settings
- **Scope**: Platform-wide visibility and control
- **Product Access**: Can view system-level data and reports

#### Agency Level
- **Direct Actions**: Create/manage users for their retailers, manage child retailers, view agency-level data, manage agency settings
- **Scope**: Agency and child retailer visibility
- **Product Access**: Can view and manage resources across child retailers

#### Retailer Level
- **Direct Actions**: Manage resources and operations within their retailer scope
- **Scope**: Retailer-scoped access only
- **Product Check**: All actions validated against `retailer.products[]`

### Second Dimension: User Type Action Restrictions

| User Type | Description | Resource Actions | Settings Actions |
|-----------|-------------|------------------|------------------|
| **owner** | Principal/owner of the level | list, view, create, update, delete, export, import | list, create, update, delete |
| **admin** | Administrator of the level | list, view, create, update, delete, export, import | list, create, update, delete |
| **lead** | Senior operator, supervisory role | list, view, create, update, delete, export, import | NONE |
| **member** | Standard operator | list, view, create, update, delete, export, import | NONE |
| **collaborator** | Viewer/collaborator (read-only) | list, view, export | NONE |

### User Level × User Type Combinations (Derived Roles)

The system defines 15 base roles (5 per user level):

#### SU Level Roles (5 roles)

| User Type | **Derived Role** | **Actions** | Description |
|---|---|---|---|
| owner | **Root User** | settings:list, settings:create, settings:update, settings:delete, resource:list, resource:view, resource:create, resource:update, resource:delete, resource:export, resource:import | Owner of the overall system with unrestricted access |
| admin | **Platform Administrator** | settings:list, settings:create, settings:update, settings:delete, resource:list, resource:view, resource:create, resource:update, resource:delete, resource:export, resource:import | Manages system configuration, users, and integrations |
| lead | **Platform Lead** | resource:list, resource:view, resource:create, resource:update, resource:delete, resource:export, resource:import | Supervises platform operations, limited system modifications |
| member | **Platform Member** | resource:list, resource:view, resource:create, resource:update, resource:delete, resource:export, resource:import | System support and operations |
| collaborator | **Platform Collaborator** | resource:list, resource:view, resource:export | System viewer, read-only access |

#### Agency Level Roles (5 roles)

| User Type | **Derived Role** | **Actions** | Description |
|---|---|---|---|
| owner | **Agency Owner** | settings:list, settings:create, settings:update, settings:delete, resource:list, resource:view, resource:create, resource:update, resource:delete, resource:export, resource:import | Owner/principal of the agency/subscriber |
| admin | **Agency Manager** | settings:list, settings:create, settings:update, settings:delete, resource:list, resource:view, resource:create, resource:update, resource:delete, resource:export, resource:import | Trusted employee managing agency resources and retailers |
| lead | **Agency Lead** | resource:list, resource:view, resource:create, resource:update, resource:delete, resource:export, resource:import | Senior operator, supervises agency operations |
| member | **Agency Member** | resource:list, resource:view, resource:create, resource:update, resource:delete, resource:export, resource:import | Operator, day-to-day agency operations |
| collaborator | **Agency Collaborator** | resource:list, resource:view, resource:export | Viewer, limited agency visibility |

#### Retailer Level Roles (5 roles)

| User Type | **Derived Role** | **Actions** | Product Validation | Description |
|---|---|---|---|---|
| owner | **Retailer Owner** | settings:list, settings:create, settings:update, settings:delete, resource:list, resource:view, resource:create, resource:update, resource:delete, resource:export, resource:import | Yes: `retailer.products[]` | Owner/principal of the retail business |
| admin | **Retailer Manager** | settings:list, settings:create, settings:update, settings:delete, resource:list, resource:view, resource:create, resource:update, resource:delete, resource:export, resource:import | Yes: `retailer.products[]` | Store manager, manages staff and operations |
| lead | **Team Lead** | resource:list, resource:view, resource:create, resource:update, resource:delete, resource:export, resource:import | Yes: `retailer.products[]` | Senior staff, supervises operations |
| member | **Staff / Operator** | resource:list, resource:view, resource:create, resource:update, resource:delete, resource:export, resource:import | Yes: `retailer.products[]` | Day-to-day operational user |
| collaborator | **Guest / Collaborator** | resource:list, resource:view, resource:export | Yes: `retailer.products[]` | Limited access, viewer/collaborator |

## Cerbos Validation Payload

The following data structure must be sent to Cerbos for permission evaluation.

### Principal Attributes

User or service principal making the request:

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | string | Yes | Unique user identifier |
| `userLevel` | string | Yes | `su`, `agency`, or `retailer` |
| `userType` | string | Yes | `owner`, `admin`, `lead`, `member`, `collaborator` |
| `name` | string | Yes | Human-readable identifier (username, email) |
| `products` | string[] | Yes | Product codes where user has subscription access (e.g., `["footprints", "signages", "qr"]`) |
| `agencyId` | string | Conditional | Agency ID if userLevel is `agency` or `retailer` |
| `retailerId` | string | Conditional | Retailer ID if userLevel is `retailer` |

### Resource Attributes

Resource being accessed and validated:

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `name` | string | Yes | Resource identifier (e.g., `footprints:sites`, `settings:admin:users`, `qr:campaigns`) |
| `product` | string | Yes | Product code (e.g., `footprints`, `signage`, `qr`, `settings`, `dashboards`) |
| `resourceId` | string | Conditional | Resource record ID — **only for resources with `:item` suffix** |
| `agencyId` | string | Conditional | Agency ID if resource is scoped to agency |
| `retailerId` | string | Conditional | Retailer ID if resource is scoped to retailer |

### Action

Namespaced action string in format: `{scope}:{action}`

| Scope | Actions |
|-------|---------|
| `resource:` | `list`, `view`, `create`, `update`, `delete`, `export`, `import` |
| `settings:` | `list`, `create`, `update`, `delete` |

### Validation Request Format

```json
{
  "principal": {
    "id": "user-123",
    "userLevel": "retailer",
    "userType": "member",
    "name": "john.doe",
    "products": ["footprints", "qr"],
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

### Notes

- Principal `products` array must include the resource's product to pass product subscription validation
- Retailer-level users are scoped to their own retailer; all product resources require a valid `retailerId`
- Agency-level users can access resources across their child retailers
- SU-level users have system-wide access but still require proper resource scoping

## Validation Examples

See [CERBOS_CONQRSE_EXAMPLES.md](./CERBOS_CONQRSE_EXAMPLES.md) for detailed validation request examples, organized by expected result (Allow/Deny scenarios).