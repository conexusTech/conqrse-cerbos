
# Cerbos Conqrse - Resource Baseline

This document defines the Conqrse Role-Based Permission Access logic.

## Supported Products

The following products are supported by Cerbos authorization, identified by the first segment in resource names:

| Product | Resource Prefix | Key Resources |
|---------|-----------------|----------------|
| **Footprints** | `footprints:` | sites, endpoints, products, pricing |
| **Signage** | `signage:` | content (templates, assets, playlists, channels), signage (people, places, things, layouts) |
| **QR** | `qr:` | site, media, templates, campaigns |
| **Reports** | `reports:` | qr-performance, campaign-compliance, site-performance-maps, export |
| **Connect** | `connect:` | contacts |

**Administrative Features** (not products):
- `dashboards:` — User dashboards by role (su-dashboard, agency-dashboard, retailer-dashboard)

## Resources

| Resource | Admin Route | Client Component | Create | List | View | Update | Delete | Export | Import |
|----------|-------------|------------------|--------|------|------|--------|--------|--------|--------|
| footprints:sites | `/footprint/sites` | `SitesClient.tsx` | AddSite | SiteTable | | | | SiteTable | SiteTable |
| footprints:sites:item | `/footprint/sites/[id]` | `SiteDetailClient.tsx` | | | | | | | |
| footprints:endpoints | `/footprint/endpoints` | `MediaPlayersClient.tsx` | AddMediaPlayer | MediaPlayerTable | | | | MediaPlayerTable | MediaPlayerTable |
| footprints:endpoints:item | `/footprint/endpoints/[endpointId]` | `MediaPlayerDetailClient.tsx` | | | | | | | |
| footprints:products | `/footprint/products` | `ProductsClient.tsx` | AddProduct | ProductTable | | | | ProductTable | ProductTable |
| footprints:products:item | `/footprint/products/[id]` | `ProductDetailClient.tsx` | | | | | | | |
| footprints:pricing | `/footprint/pricing` | `PricingClient.tsx` | AddPricing | PricingTable | | | | PricingTable | PricingTable |
| signage:content:templates | `/content/templates` | `TemplatesClient.tsx` | | TemplateTable | | | | TemplateTable | TemplateTable |
| signage:content:templates:create | `/content/templates/create` | `CreateTemplatePageClient.tsx` | CreateTemplatePageClient | | | | | | |
| signage:content:templates:item | `/content/templates/[id]` | `TemplateDetailClient.tsx` | | | | | | | |
| signage:content:assets | `/content/assets` | `PlaylistAssetsClient.tsx` | AddAsset | AssetTable | | | | AssetTable | AssetTable |
| signage:content:assets:create-template | `/content/assets/create-template` | `CreateTemplateClient.tsx` | CreateTemplateClient | | | | | | |
| signage:content:assets:create-content-template | `/content/assets/create-content-template` | `CreateContentTemplateClient.tsx` | CreateContentTemplateClient | | | | | | |
| signage:content:playlists | `/content/playlists` | `PlaylistConfigsClient.tsx` | AddPlaylistConfig | PlaylistConfigTable | | | | PlaylistConfigTable | PlaylistConfigTable |
| signage:content:playlists:item:manage | `/content/playlists/[playlistConfigId]/manage` | `ManagePlaylistConfigClient.tsx` | | | | | | | |
| signage:content:backgrounds | `/content/backgrounds` | `BackgroundsClient.tsx` | AddBackground | BackgroundTable | | | | BackgroundTable | BackgroundTable |
| signage:content:channels | `/content/channels` | `MediaPlayerChannelsClient.tsx` | | MediaPlayerChannelTable | | | | MediaPlayerChannelTable | MediaPlayerChannelTable |
| signage:content:channels:add | `/content/channels/add` | `MediaPlayerChannelAddClient.tsx` | MediaPlayerChannelAddClient | | | | | | |
| signage:content:channels:item | `/content/channels/[id]` | `MediaPlayerChannelDetailClient.tsx` | | | | | | | |
| signage:content:tags | `/content/tags` | `TagManagerClient.tsx` | AddTag | TagTable | | | | TagTable | TagTable |
| signage:content:content-groups | `/content/content-groups` | `ContentGroupsClient.tsx` | AddContentGroup | ContentGroupTable | | | | ContentGroupTable | ContentGroupTable |
| signage:content:content-groups:item | `/content/content-groups/[id]` | `ManageContentGroupClient.tsx` | | | | | | | |
| signage:signage:people | `/signages/people` | `SignagePeopleClient.tsx` | AddPerson | PeopleTable | | | | PeopleTable | PeopleTable |
| signage:signage:places | `/signages/places` | `SignagePlacesClient.tsx` | AddPlace | PlaceTable | | | | PlaceTable | PlaceTable |
| signage:signage:things | `/signages/things` | `SignageThingsClient.tsx` | AddThing | ThingTable | | | | ThingTable | ThingTable |
| qr:site | `/qr/site` | `ManagedSiteQrClient.tsx` | AddSiteQr | SiteQrTable | | | | SiteQrTable | SiteQrTable |
| qr:site:item | `/qr/site/[id]` | `ManagedSiteQrDetailClient.tsx` | | | | | | | |
| qr:media | `/qr/media` | `ManageMediaQrClient.tsx` | AddMediaQr | MediaQrTable | | | | MediaQrTable | MediaQrTable |
| qr:media:item | `/qr/media/[id]` | `ManageMediaQrDetailClient.tsx` | | | | | | | |
| qr:templates | `/qr/templates` | `QrTemplatesClient.tsx` | AddQrTemplate | QrTemplateTable | | | | QrTemplateTable | QrTemplateTable |
| qr:templates:item | `/qr/templates/[id]` | `QrTemplateDetailClient.tsx` | | | | | | | |
| qr:campaigns | `/qr/campaigns` | `CampaignsClient.tsx` | AddCampaign | CampaignTable | | | | CampaignTable | CampaignTable |
| reports | `/reports` | `ReportsClient.tsx` | | | | | | | |
| reports:qr-performance | `/reports/qr-performance` | `QRPerformanceAnalysisClient.tsx` | | QRPerformanceTable | | | | QRPerformanceTable | |
| reports:qr-performance-site-to-site | `/reports/qr-performance-site-to-site` | `QRSiteAnalysisClient.tsx` | | QRSiteAnalysisTable | | | | QRSiteAnalysisTable | |
| reports:campaign-compliance | `/reports/campaign-compliance` | `CampaignComplianceClient.tsx` | | ComplianceTable | | | | ComplianceTable | |
| reports:campaign-compliance-details | `/reports/campaign-compliance-details` | `CampaignComplianceDetailsClient.tsx` | | ComplianceDetailsTable | | | | ComplianceDetailsTable | |
| reports:site-performance-maps | `/reports/site-performance-maps` | `SitePerformanceMapsClient.tsx` | | SitePerformanceTable | | | | SitePerformanceTable | |
| reports:media-performance-maps | `/reports/media-performance-maps` | `MediaPerformanceClient.tsx` | | MediaPerformanceTable | | | | MediaPerformanceTable | |
| reports:campaign-performance-maps | `/reports/campaign-performance-maps` | `CampaignPerformanceMapsClient.tsx` | | CampaignPerformanceTable | | | | CampaignPerformanceTable | |
| reports:content-proof-of-play | `/reports/content-proof-of-play` | `ContentProofOfPlayClient.tsx` | | ProofOfPlayTable | | | | ProofOfPlayTable | |
| reports:export | `/export` | `BatchClient.tsx` | | | | | | BatchClient | |
| connect:contacts | `/connect/contacts` | `ContactsClient.tsx` | AddContact | ContactTable | | | | ContactTable | ContactTable |
| dashboards:su-dashboard | `/su-dashboard` | `SUDashboardClient.tsx` | | | | | | | |
| dashboards:agency-dashboard | `/agency-dashboard` | `AgencyDashboardClient.tsx` | | | | | | | |
| dashboards:retailer-dashboard | `/retailer-dashboard` | `RetailerDashboardClient.tsx` | | | | | | | |
| settings:admin:general | `/settings/general` | `GeneralSettingsClient.tsx` | | | | | | | |
| settings:admin:users | `/settings/users` | `UserSettingsClient.tsx` | AddUser | UserTable | | | | UserTable | UserTable |
| settings:admin:teams | `/settings/teams` | `TeamSettingsClient.tsx` | AddTeam | TeamTable | | | | TeamTable | TeamTable |
| settings:admin:profile | `/profile` | `ProfileClient.tsx` | | | | | | | |
| footprints:sites:settings:property | `/settings/footprint` | `FootprintSettingsClient.tsx` | AddProperty | PropertyTable | | | | PropertyTable | PropertyTable |
| footprints:sites:settings:property:item | `/settings/footprint` | `FootprintSettingsClient.tsx` | | | | | | | |
| footprints:products:settings:property | `/settings/product` | `ProductSettingsClient.tsx` | AddProperty | PropertyTable | | | | PropertyTable | PropertyTable |
| footprints:products:settings:property:item | `/settings/product` | `ProductSettingsClient.tsx` | | | | | | | |
| footprints:products:settings:pricing-group | `/settings/price-tag` | `PriceTagSettingsClient.tsx` | AddPricingGroup | PricingGroupTable | | | | PricingGroupTable | PricingGroupTable |
| footprints:products:settings:pricing-group:item | `/settings/price-tag` | `PriceTagSettingsClient.tsx` | | | | | | | |
| qr:settings:design | `/settings/qr` | `QrSettingsClient.tsx` | AddQrDesign | QrDesignTable | | | | QrDesignTable | QrDesignTable |
| qr:settings:design:item | `/settings/qr` | `QrSettingsClient.tsx` | | | | | | | |
| qr:settings:power-tag | `/settings/qr` | `QrSettingsClient.tsx` | AddPowerTag | PowerTagTable | | | | PowerTagTable | PowerTagTable |
| qr:settings:power-tag:item | `/settings/qr` | `QrSettingsClient.tsx` | | | | | | | |
| qr:settings:default-redirect | `/settings/qr` | `QrSettingsClient.tsx` | AddDefaultRedirect | DefaultRedirectTable | | | | DefaultRedirectTable | DefaultRedirectTable |
| qr:settings:domain | `/settings/qr` | `QrSettingsClient.tsx` | AddDomain | DomainTable | | | | DomainTable | DomainTable |
| qr:settings:domain:item | `/settings/qr` | `QrSettingsClient.tsx` | | | | | | | |
| signage:signage:people:settings:property | `/settings/properties-manager/people` | `PeoplePropertiesClient.tsx` | AddProperty | PropertyTable | | | | PropertyTable | PropertyTable |
| signage:signage:people:settings:property:item | `/settings/properties-manager/people` | `PeoplePropertiesClient.tsx` | | | | | | | |
| signage:signage:places:settings:property | `/settings/properties-manager/places` | `PlacePropertiesClient.tsx` | AddProperty | PropertyTable | | | | PropertyTable | PropertyTable |
| signage:signage:places:settings:property:item | `/settings/properties-manager/places` | `PlacePropertiesClient.tsx` | | | | | | | |
| signage:signage:things:settings:property | `/settings/properties-manager/things` | `ThingPropertiesClient.tsx` | AddProperty | PropertyTable | | | | PropertyTable | PropertyTable |
| signage:signage:things:settings:property:item | `/settings/properties-manager/things` | `ThingPropertiesClient.tsx` | | | | | | | |
| signage:settings:layout | `/settings/signage` | `SignageSettingsClient.tsx` | AddLayout | LayoutTable | | | | LayoutTable | LayoutTable |
| signage:settings:layout:item | `/settings/signage` | `SignageSettingsClient.tsx` | | | | | | | |

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

> **Key Architectural Constraint**: All product resources (footprints, signage, qr, reports, connect) are **retailer-scoped** and require a retailer context for access. SU and Agency users do not have a native retailer context, therefore they **cannot access any product features directly**. They must use the "Act AS" delegation model to assume a retailer context first. This constraint is enforced at the API level — v3 endpoints do not support product access without retailer information.

#### Super User (SU) Level
- **Direct Actions**: Create/manage agencies, view all system data at SU level, manage SU-level settings
- **Delegation**: Can "Act AS" any agency or retailer (child or not)
- **User Type Inheritance**: Retains their user type when acting as (e.g., SU Admin acting as Retailer = Retailer Admin)
- **Product Check**: Bypasses product checks when acting as retailer

#### Agency Level
- **Direct Actions**: Create/manage users for their retailers, manage child retailers, view agency-level data, manage agency settings
- **Delegation**: Can "Act AS" only their child retailers
- **User Type Inheritance**: Retains their user type when acting as (e.g., Agency Member acting as Retailer = Retailer Member)
- **Product Check**: Bypasses product checks for their child retailers

#### Retailer Level
- **Direct Actions**: Manage resources and operations within their retailer scope
- **Delegation**: NO delegation capability (end users of the system)
- **User Type Inheritance**: N/A
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

#### SU Level Roles

| User Type | **Derived Role** | **Direct Actions (SU-level)** | **Can Act AS** | **When Acting As, Becomes** | Description |
|---|---|---|---|---|---|
| owner | **Root User** | settings:list, settings:create, settings:update, settings:delete, resource:list, resource:view, resource:create, resource:update, resource:delete, resource:export, resource:import | Agency (any level), Retailer (any level) | Agency Owner / Retailer Owner | Owner of the overall system with unrestricted access |
| admin | **Platform Administrator** | settings:list, settings:create, settings:update, settings:delete, resource:list, resource:view, resource:create, resource:update, resource:delete, resource:export, resource:import | Agency (any level), Retailer (any level) | Agency Admin / Retailer Admin | Manages system configuration, users, and integrations |
| lead | **Platform Lead** | resource:list, resource:view, resource:create, resource:update, resource:delete, resource:export, resource:import | Agency (any level), Retailer (any level) | Agency Lead / Retailer Lead | Supervises platform operations, limited system modifications |
| member | **Platform Member** | resource:list, resource:view, resource:create, resource:update, resource:delete, resource:export, resource:import | Agency (any level), Retailer (any level) | Agency Member / Retailer Member | System support and operations |
| collaborator | **Platform Collaborator** | resource:list, resource:view, resource:export | Agency (any level), Retailer (any level) | Agency Collaborator / Retailer Collaborator | System viewer, read-only access |

#### Agency Level Roles

| User Type | **Derived Role** | **Direct Actions (Agency-level)** | **Can Act AS** | **When Acting As, Becomes** | Description |
|---|---|---|---|---|---|
| owner | **Agency Owner** | settings:list, settings:create, settings:update, settings:delete, resource:list, resource:view, resource:create, resource:update, resource:delete, resource:export, resource:import | Child Retailers (any level) | Retailer Owner | Owner/principal of the agency/subscriber |
| admin | **Agency Manager** | settings:list, settings:create, settings:update, settings:delete, resource:list, resource:view, resource:create, resource:update, resource:delete, resource:export, resource:import | Child Retailers (any level) | Retailer Admin | Trusted employee managing agency resources and retailers |
| lead | **Agency Lead** | resource:list, resource:view, resource:create, resource:update, resource:delete, resource:export, resource:import | Child Retailers (any level) | Retailer Lead | Senior operator, supervises agency operations |
| member | **Agency Member** | resource:list, resource:view, resource:create, resource:update, resource:delete, resource:export, resource:import | Child Retailers (any level) | Retailer Member | Operator, day-to-day agency operations |
| collaborator | **Agency Collaborator** | resource:list, resource:view, resource:export | Child Retailers (any level) | Retailer Collaborator | Viewer, limited agency visibility |

#### Retailer Level Roles

| User Type | **Derived Role** | **Direct Actions (Retailer-level)** | **Can Act AS** | Product Validation | Description |
|---|---|---|---|---|---|
| owner | **Retailer Owner** | settings:list, settings:create, settings:update, settings:delete, resource:list, resource:view, resource:create, resource:update, resource:delete, resource:export, resource:import | NONE | Yes: `retailer.products[]` | Owner/principal of the retail business |
| admin | **Retailer Manager** | settings:list, settings:create, settings:update, settings:delete, resource:list, resource:view, resource:create, resource:update, resource:delete, resource:export, resource:import | NONE | Yes: `retailer.products[]` | Store manager, manages staff and operations |
| lead | **Team Lead** | resource:list, resource:view, resource:create, resource:update, resource:delete, resource:export, resource:import | NONE | Yes: `retailer.products[]` | Senior staff, supervises operations |
| member | **Staff / Operator** | resource:list, resource:view, resource:create, resource:update, resource:delete, resource:export, resource:import | NONE | Yes: `retailer.products[]` | Day-to-day operational user |
| collaborator | **Guest / Collaborator** | resource:list, resource:view, resource:export | NONE | Yes: `retailer.products[]` | Limited access, viewer/collaborator |

## Cerbos Validation Payload

The following data structure must be sent to Cerbos for permission evaluation using the "Act AS" delegation model.

### Principal Attributes

User or service principal making the request:

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | string | Yes | Unique user identifier |
| `userLevel` | string | Yes | `su`, `agency`, or `retailer` |
| `userType` | string | Yes | `owner`, `admin`, `lead`, `member`, `collaborator` |
| `name` | string | Yes | Human-readable identifier (username, email) |
| `products` | string[] | Yes | Product codes where user has subscription access (e.g., `["footprints", "signage", "qr"]`) |
| `agencyId` | string | Conditional | Agency ID if userLevel is `agency` or `retailer` |
| `retailerId` | string | Conditional | Retailer ID if userLevel is `retailer` |
| `actingAs` | object | Conditional | **NEW** — Only present if user is delegating via "Act AS" |
| `actingAs.level` | string | When actingAs present | Target level: `agency` or `retailer` |
| `actingAs.retailerId` | string | When actingAs present and level is `retailer` | The retailer ID being delegated to |
| `actingAs.agencyId` | string | When actingAs present and level is `agency` | The agency ID being delegated to |

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

## Validation Examples

See [CERBOS_CONQRSE_EXAMPLES.md](./CERBOS_CONQRSE_EXAMPLES.md) for detailed validation request examples, organized by expected result (Allow/Deny scenarios).