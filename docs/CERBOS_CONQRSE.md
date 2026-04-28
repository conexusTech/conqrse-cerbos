
# Cerbos Conqrse - Resource Baseline

This document defines the Conqrse Role-Based Permission Access logic.

## Supported Products

The following products are supported by Cerbos authorization, identified by the first segment in resource names:

| Product        | Resource Prefix | Key Resources                                                                       |
| -------------- | --------------- | ------------------------------------------------------------------------------------|
| **Footprints** | `footprints:`   | sites, endpoints, products, pricing                                                |
| **Signages**   | `signages:`     | people, places, things                                                             |
| **Contents**   | `contents:`     | templates, assets, playlists, channels, tags, tags_assignments, content_groups, backgrounds, backgrounds_transition |
| **QR**         | `qr:`           | site, media, templates, campaigns                                                  |
| **Reports**    | `reports:`      | qr_performance, campaign_compliance, site_performance_maps, export                 |
| **Connect**    | `connect:`      | contacts                                                                           |

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
- `settings:admin_*` — Platform/system-level settings (owners/admins only)
- `settings:user_*` — User-specific settings (personal profile, preferences)
- `settings:{product}_{feature}` — Product-specific configuration (e.g., `settings:qr_design`, `settings:signage_layout`)
- `settings:{product}_{feature}_{category}` — Sub-categories within product settings

**Example:**
```
settings:admin_general_agency       ← Agency-level settings
settings:admin_general_retailer     ← Retailer-level settings
settings:admin_general_brand        ← Brand-level settings
settings:admin_general_ambient      ← Ambient-level settings
settings:admin_users                ← User management
settings:admin_teams                ← Team management
settings:qr_design                  ← QR design settings
settings:qr_power_tag               ← QR power-tag settings
settings:signage_layout             ← Signage layout settings
settings:signage_people_property    ← Signage people property settings
settings:footprints_sites_property  ← Footprints site property settings
settings:user_profile               ← User profile/preferences
```

**Why NOT `product:settings`?**
- ❌ Leads to repetitive policy patterns
- ❌ Harder to enforce platform-wide settings governance
- ❌ Settings and product access have different rules (should be separated)
- ❌ Violates separation of concerns

## Resources

| Resource                                        | Admin Route                             | Client Component                      | Actions                                            |
| ----------------------------------------------- | --------------------------------------- | ------------------------------------- | -------------------------------------------------- |
| footprints:sites                                | `/footprint/sites`                      | `SitesClient.tsx`                     | list, view, create, update, delete, export, import |
| footprints:sites:item                           | `/footprint/sites/[id]`                 | `SiteDetailClient.tsx`                | view, update, delete                               |
| footprints:endpoints                            | `/footprint/endpoints`                  | `MediaPlayersClient.tsx`              | list, view, create, update, delete, export, import |
| footprints:endpoints:item                       | `/footprint/endpoints/[endpointId]`     | `MediaPlayerDetailClient.tsx`         | view, update, delete                               |
| footprints:products                             | `/footprint/products`                   | `ProductsClient.tsx`                  | list, view, create, update, delete, export, import |
| footprints:products:item                        | `/footprint/products/[id]`              | `ProductDetailClient.tsx`             | view, update, delete                               |
| footprints:pricing                              | `/footprint/pricing`                    | `PricingClient.tsx`                   | list, view, create, update, delete, export, import |
| contents:templates                              | `/content/templates`                    | `TemplatesClient.tsx`                 | list, view, create, update, delete, export, import |
| contents:templates:item                         | `/content/templates/[id]`               | `TemplateDetailClient.tsx`            | view, update, delete                               |
| contents:assets                                 | `/content/assets`                       | `PlaylistAssetsClient.tsx`            | list, view, create, update, delete, export, import |
| contents:assets:item                            | `/content/assets`                       | `PlaylistAssetsClient.tsx`            | view, update, delete                               |
| contents:playlists                              | `/content/playlists`                    | `PlaylistConfigsClient.tsx`           | list, view, create, update, delete, export, import |
| contents:playlists:item                         | `/content/playlists/[playlistConfigId]` | `ManagePlaylistConfigClient.tsx`      | view, update, delete                               |
| contents:backgrounds                            | `/content/backgrounds`                  | `BackgroundsClient.tsx`               | list, view, create, update, delete, export, import |
| contents:backgrounds:item                       | `/content/backgrounds`                  | `BackgroundsClient.tsx`               | view, update, delete                               |
| contents:backgrounds_transition                 | `/content/backgrounds`                  | `BackgroundsClient.tsx`               | list, view, create, update, delete, export, import |
| contents:backgrounds_transition:item            | `/content/backgrounds`                  | `BackgroundsClient.tsx`               | view, update, delete                               |
| contents:channels                               | `/content/channels`                     | `MediaPlayerChannelsClient.tsx`       | list, view, create, update, delete, export, import |
| contents:channels:item                          | `/content/channels/[id]`                | `MediaPlayerChannelDetailClient.tsx`  | view, update, delete                               |
| contents:tags                                   | `/content/tags`                         | `TagManagerClient.tsx`                | list, view, create, update, delete, export, import |
| contents:tags:item                              | `/content/tags`                         | `TagManagerClient.tsx`                | view, update, delete                               |
| contents:tags_assignments                       | `/content/tags`                         | `TagManagerClient.tsx`                | list, view, create, update, delete, export, import |
| contents:tags_assignments:item                  | `/content/tags`                         | `TagManagerClient.tsx`                | view, update, delete                               |
| contents:content_groups                         | `/content/content-groups`               | `ContentGroupsClient.tsx`             | list, view, create, update, delete, export, import |
| contents:content_groups:item                    | `/content/content-groups/[id]`          | `ManageContentGroupClient.tsx`        | view, update, delete                               |
| signages:people                                 | `/signages/people`                      | `SignagePeopleClient.tsx`             | list, view, create, update, delete, export, import |
| signages:people:item                            | `/signages/people`                      | `SignagePeopleClient.tsx`             | view, update, delete                               |
| signages:places                                 | `/signages/places`                      | `SignagePlacesClient.tsx`             | list, view, create, update, delete, export, import |
| signages:places:item                            | `/signages/places`                      | `SignagePlacesClient.tsx`             | view, update, delete                               |
| signages:things                                 | `/signages/things`                      | `SignageThingsClient.tsx`             | list, view, create, update, delete, export, import |
| signages:things:item                            | `/signages/things`                      | `SignageThingsClient.tsx`             | view, update, delete                               |
| qr:site                                         | `/qr/site`                              | `ManagedSiteQrClient.tsx`             | list, view, create, update, delete, export, import |
| qr:site:item                                    | `/qr/site/[id]`                         | `ManagedSiteQrDetailClient.tsx`       | view, update, delete                               |
| qr:media                                        | `/qr/media`                             | `ManageMediaQrClient.tsx`             | list, view, create, update, delete, export, import |
| qr:media:item                                   | `/qr/media/[id]`                        | `ManageMediaQrDetailClient.tsx`       | view, update, delete                               |
| qr:templates                                    | `/qr/templates`                         | `QrTemplatesClient.tsx`               | list, view, create, update, delete, export, import |
| qr:templates:item                               | `/qr/templates/[id]`                    | `QrTemplateDetailClient.tsx`          | view, update, delete                               |
| qr:campaigns                                    | `/qr/campaigns`                         | `CampaignsClient.tsx`                 | list, view, create, update, delete, export, import |
| qr:campaigns:item                               | `/qr/campaigns/[id]`                    | `CampaignsClient.tsx`                 | view, update, delete                               |
| reports:qr_performance                          | `/reports/qr_performance`               | `QRPerformanceAnalysisClient.tsx`     | list, view, export                                 |
| reports:qr_performance_site_to_site             | `/reports/qr_performance_site_to_site`  | `QRSiteAnalysisClient.tsx`            | list, view, export                                 |
| reports:campaign_compliance                     | `/reports/campaign_compliance`          | `CampaignComplianceClient.tsx`        | list, view, export                                 |
| reports:campaign_compliance_details             | `/reports/campaign_compliance_details`  | `CampaignComplianceDetailsClient.tsx` | list, view, export                                 |
| reports:site_performance_maps                   | `/reports/site_performance_maps`        | `SitePerformanceMapsClient.tsx`       | list, view, export                                 |
| reports:media_performance_maps                  | `/reports/media_performance_maps`       | `MediaPerformanceClient.tsx`          | list, view, export                                 |
| reports:campaign_performance_maps               | `/reports/campaign_performance_maps`    | `CampaignPerformanceMapsClient.tsx`   | list, view, export                                 |
| reports:content_proof_of_play                   | `/reports/content_proof_of_play`        | `ContentProofOfPlayClient.tsx`        | list, view, export                                 |
| reports:export                                  | `/export`                               | `BatchClient.tsx`                     | export                                             |
| connect:contacts                                | `/connect/contacts`                     | `ContactsClient.tsx`                  | list, view, create, update, delete, export, import |
| connect:contacts:item                           | `/connect/contacts/[id]`                | `ContactsClient.tsx`                  | view, update, delete                               |
| settings:admin_general_agency:item              | `/settings/general`                     | `GeneralSettingsClient.tsx`           | view, update, delete                               |
| settings:admin_general_retailer:item            | `/settings/general`                     | `GeneralSettingsClient.tsx`           | view, update, delete                               |
| settings:admin_general_brand:item               | `/settings/general`                     | `GeneralSettingsClient.tsx`           | view, update, delete                               |
| settings:admin_general_ambient:item             | `/settings/general`                     | `GeneralSettingsClient.tsx`           | view, update, delete                               |
| settings:admin_users                            | `/settings/users`                       | `UserSettingsClient.tsx`              | list, view, create, update, delete, export, import |
| settings:admin_users:item                       | `/settings/users`                       | `UserSettingsClient.tsx`              | view, update, delete                               |
| settings:admin_teams                            | `/settings/teams`                       | `TeamSettingsClient.tsx`              | list, view, create, update, delete, export, import |
| settings:admin_teams:item                       | `/settings/teams`                       | `TeamSettingsClient.tsx`              | view, update, delete                               |
| settings:admin_cerbos                           | `/settings/cerbos`                      | `CerbosSettingsClient.tsx`            | list, view, create, update, delete, export, import |
| settings:admin_cerbos:item                      | `/settings/cerbos`                      | `CerbosSettingsClient.tsx`            | view, update, delete                               |
| settings:user_profile:item                      | `/profile`                              | `ProfileClient.tsx`                   | view, update                                       |
| settings:footprints_sites_property              | `/settings/footprint`                   | `FootprintSettingsClient.tsx`         | list, view, create, update, delete, export, import |
| settings:footprints_sites_property:item         | `/settings/footprint`                   | `FootprintSettingsClient.tsx`         | view, update, delete                               |
| settings:footprints_products_property           | `/settings/product`                     | `ProductSettingsClient.tsx`           | list, view, create, update, delete, export, import |
| settings:footprints_products_property:item      | `/settings/product`                     | `ProductSettingsClient.tsx`           | view, update, delete                               |
| settings:footprints_products_pricing_group      | `/settings/price-tag`                   | `PriceTagSettingsClient.tsx`          | list, view, create, update, delete, export, import |
| settings:footprints_products_pricing_group:item | `/settings/price-tag`                   | `PriceTagSettingsClient.tsx`          | view, update, delete                               |
| settings:qr_design                              | `/settings/qr`                          | `QrSettingsClient.tsx`                | list, view, create, update, delete, export, import |
| settings:qr_design:item                         | `/settings/qr`                          | `QrSettingsClient.tsx`                | view, update, delete                               |
| settings:qr_power_tag                           | `/settings/qr`                          | `QrSettingsClient.tsx`                | list, view, create, update, delete, export, import |
| settings:qr_power_tag:item                      | `/settings/qr`                          | `QrSettingsClient.tsx`                | view, update, delete                               |
| settings:qr_default_redirect                    | `/settings/qr`                          | `QrSettingsClient.tsx`                | list, view, create, update, delete                 |
| settings:qr_default_redirect:item               | `/settings/qr`                          | `QrSettingsClient.tsx`                | view, update, delete                               |
| settings:qr_domain                              | `/settings/qr`                          | `QrSettingsClient.tsx`                | list, view, create, update, delete, export, import |
| settings:qr_domain:item                         | `/settings/qr`                          | `QrSettingsClient.tsx`                | view, update, delete                               |
| settings:signage_layout                         | `/settings/signage`                     | `SignageSettingsClient.tsx`           | list, view, create, update, delete, export, import |
| settings:signage_layout:item                    | `/settings/signage`                     | `SignageSettingsClient.tsx`           | view, update, delete                               |
| settings:signage_people_property                | `/settings/properties-manager/people`   | `PeoplePropertiesClient.tsx`          | list, view, create, update, delete, export, import |
| settings:signage_people_property:item           | `/settings/properties-manager/people`   | `PeoplePropertiesClient.tsx`          | view, update, delete                               |
| settings:signage_places_property                | `/settings/properties-manager/places`   | `PlacePropertiesClient.tsx`           | list, view, create, update, delete, export, import |
| settings:signage_places_property:item           | `/settings/properties-manager/places`   | `PlacePropertiesClient.tsx`           | view, update, delete                               |
| settings:signage_things_property                | `/settings/properties-manager/things`   | `ThingPropertiesClient.tsx`           | list, view, create, update, delete, export, import |
| settings:signage_things_property:item           | `/settings/properties-manager/things`   | `ThingPropertiesClient.tsx`           | view, update, delete                               |

## Actions

| Action     | Type  | Description                                                                    |
| ---------- | ----- | ------------------------------------------------------------------------------ |
| **Create** | Write | Create new resources (POST operations)                                         |
| **List**   | Read  | View collection of resources with filters and pagination (GET list operations) |
| **View**   | Read  | View individual resource details (GET detail operations)                       |
| **Update** | Write | Modify existing resources (PUT/PATCH operations)                               |
| **Delete** | Write | Remove resources from the system (DELETE operations)                           |
| **Export** | Read  | Download/export resource data (GET export operations)                          |
| **Import** | Write | Upload/import data to create or update resources (POST/PUT bulk operations)    |

### Summary
- **Read Operations**: List, View, Export — Safe operations that do not modify data
- **Write Operations**: Create, Update, Delete, Import — Operations that create, modify, or remove data

## User Dimensions

Every user has two attributes that determine access:

| Dimension     | Values                                             | Purpose                                        |
| ------------- | -------------------------------------------------- | ---------------------------------------------- |
| **userLevel** | `su`, `agency`, `retailer`                         | Organizational scope — what data you can see   |
| **userType**  | `owner`, `admin`, `lead`, `member`, `collaborator` | Permission role — what actions you can perform |

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

| User Type        | Description                       | Resource Actions                                   | Settings Actions             |
| ---------------- | --------------------------------- | -------------------------------------------------- | ---------------------------- |
| **owner**        | Principal/owner of the level      | list, view, create, update, delete, export, import | list, create, update, delete |
| **admin**        | Administrator of the level        | list, view, create, update, delete, export, import | list, create, update, delete |
| **lead**         | Senior operator, supervisory role | list, view, create, update, delete, export, import | NONE                         |
| **member**       | Standard operator                 | list, view, create, update, delete, export, import | NONE                         |
| **collaborator** | Viewer/collaborator (read-only)   | list, view, export                                 | NONE                         |

### User Level × User Type Combinations (Derived Roles)

The system defines 15 base roles (5 per user level):

#### SU Level Roles (5 roles)

| User Type    | **Derived Role**           | **Actions**                                                                                                                                                                         | Product Access | Description                                                  |
| ------------ | -------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------- | ------------------------------------------------------------ |
| owner        | **Root User**              | settings:list, settings:create, settings:update, settings:delete, resource:list, resource:view, resource:create, resource:update, resource:delete, resource:export, resource:import | Yes* | Owner of the overall system with unrestricted access         |
| admin        | **Platform Administrator** | settings:list, settings:create, settings:update, settings:delete, resource:list, resource:view, resource:create, resource:update, resource:delete, resource:export, resource:import | Yes* | Manages system configuration, users, and integrations        |
| lead         | **Platform Lead**          | resource:list, resource:view, resource:create, resource:update, resource:delete, resource:export, resource:import                                                                   | Yes* | Supervises platform operations, limited system modifications |
| member       | **Platform Member**        | resource:list, resource:view, resource:create, resource:update, resource:delete, resource:export, resource:import                                                                   | Yes* | System support and operations                                |
| collaborator | **Platform Collaborator**  | resource:list, resource:view, resource:export                                                                                                                                       | Yes* | System viewer, read-only access                              |

#### Agency Level Roles (5 roles)

| User Type    | **Derived Role**        | **Actions**                                                                                                                                                                         | Product Access | Description                                              |
| ------------ | ----------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------- | -------------------------------------------------------- |
| owner        | **Agency Owner**        | settings:list, settings:create, settings:update, settings:delete, resource:list, resource:view, resource:create, resource:update, resource:delete, resource:export, resource:import | Yes* | Owner/principal of the agency/subscriber                 |
| admin        | **Agency Manager**      | settings:list, settings:create, settings:update, settings:delete, resource:list, resource:view, resource:create, resource:update, resource:delete, resource:export, resource:import | Yes* | Trusted employee managing agency resources and retailers |
| lead         | **Agency Lead**         | resource:list, resource:view, resource:create, resource:update, resource:delete, resource:export, resource:import                                                                   | Yes* | Senior operator, supervises agency operations            |
| member       | **Agency Member**       | resource:list, resource:view, resource:create, resource:update, resource:delete, resource:export, resource:import                                                                   | Yes* | Operator, day-to-day agency operations                   |
| collaborator | **Agency Collaborator** | resource:list, resource:view, resource:export                                                                                                                                       | Yes* | Viewer, limited agency visibility                        |

#### Retailer Level Roles (5 roles)

| User Type    | **Derived Role**         | **Actions**                                                                                                                                                                         | Product Validation         | Description                                 |
| ------------ | ------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------- | ------------------------------------------- |
| owner        | **Retailer Owner**       | settings:list, settings:create, settings:update, settings:delete, resource:list, resource:view, resource:create, resource:update, resource:delete, resource:export, resource:import | Yes: `retailer.products[]` | Owner/principal of the retail business      |
| admin        | **Retailer Manager**     | settings:list, settings:create, settings:update, settings:delete, resource:list, resource:view, resource:create, resource:update, resource:delete, resource:export, resource:import | Yes: `retailer.products[]` | Store manager, manages staff and operations |
| lead         | **Team Lead**            | resource:list, resource:view, resource:create, resource:update, resource:delete, resource:export, resource:import                                                                   | Yes: `retailer.products[]` | Senior staff, supervises operations         |
| member       | **Staff / Operator**     | resource:list, resource:view, resource:create, resource:update, resource:delete, resource:export, resource:import                                                                   | Yes: `retailer.products[]` | Day-to-day operational user                 |
| collaborator | **Guest / Collaborator** | resource:list, resource:view, resource:export                                                                                                                                       | Yes: `retailer.products[]` | Limited access, viewer/collaborator         |

## Cerbos Payload

The following data structure must be sent to Cerbos for permission evaluation.

### Principal

User or service principal making the request:

```json
{
   "id": "string - the ID of the logged in user",
   "roles": ["string - derived roles, see k8s/base/policies/_derived_roles.yaml"],
   "attr": {
      "userLevel": "retailer, su, agency or user",
      "userType": "admin, collaborator, owner, lead, or member",
      "name": "string",
      "products": ["string - list of known products (qr, priceTags, compliance, product, signage, landing, connect, ppt)"],
      "agencyId": "string - retailer's agency ID",
      "retailerId": "string - the retailer in subject"
   }
}
```

### Resource

Resource being accessed and validated:

```json
{
   "id": "string - the resource in subject",
   "kind": "string - the resource in subject",
   "attr": {
      "retailerId": "string - the retailer of the resource",
      "products": ["string - required products the retailer must have to have access to the resource"]
   }
}
```

### Action

Namespaced action string in format: `{scope}:{action}`

| Scope       | Actions                                                          |
| ----------- | ---------------------------------------------------------------- |
| `resource:` | `list`, `view`, `create`, `update`, `delete`, `export`, `import` |
| `settings:` | `list`, `create`, `update`, `delete`                             |

### Notes

- Principal `products` array must include the resource's product to pass product subscription validation
- Retailer-level users are scoped to their own retailer; all product resources require a valid `retailerId`
- Agency-level users can access product resources across their child retailers (when `retailerId` matches)
- SU-level users have system-wide product resource access (when `retailerId` matches and required products are present)
- *Product Access: SU and Agency-level roles have full access to product-scoped resources with the same permissions as Retailer-level owners/managers, subject to product subscription validation

## Validation Examples

See [CERBOS_CONQRSE_EXAMPLES.md](./CERBOS_CONQRSE_EXAMPLES.md) for detailed validation request examples, organized by expected result (Allow/Deny scenarios).