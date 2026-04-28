# Resources × Product × Actions Matrix

This document provides a comprehensive matrix of all Cerbos resources and their supported actions.

## Products

- **qr** - QR Code
- **priceTags** - Pricing
- **compliance** - Compliance
- **product** - Product 
- **signage** - Signages
- **landing** - Landing
- **connect** - Connect
- **ppt** - People, Places, and Things

## Action Definitions

### Resource Actions (scope: `resource:`)
- `resource:list` — View collection of resources with filters and pagination
- `resource:view` — View individual resource details
- `resource:create` — Create new resources
- `resource:update` — Modify existing resources
- `resource:delete` — Remove resources
- `resource:export` — Download/export resource data
- `resource:import` — Upload/import data

### Settings Actions (scope: `settings:`)
- `settings:list` — View collection of settings
- `settings:create` — Create new settings
- `settings:update` — Modify existing settings
- `settings:delete` — Remove settings

---

## Non-Product Related Resources

These are the resources that doesn't need product and retailer validation.

### Settings - Admin

| Resource                     | Type       | Actions                                            |
| ---------------------------- | ---------- | -------------------------------------------------- |
| `settings:admin_users`       | Collection | list, view, create, update, delete, export, import |
| `settings:admin_users:item`  | Item       | view, update, delete                               |
| `settings:admin_teams`       | Collection | list, view, create, update, delete, export, import |
| `settings:admin_teams:item`  | Item       | view, update, delete                               |
| `settings:admin_cerbos`      | Collection | list, view, create, update, delete, export, import |
| `settings:admin_cerbos:item` | Item       | view, update, delete                               |

### Settings - User

| Resource                     | Type | Actions      |
| ---------------------------- | ---- | ------------ |
| `settings:user_profile:item` | Item | view, update |

## Product Related Resources

### Reports Resource

| Resource                              | Type       | Actions              |
| ------------------------------------- | ---------- | -------------------- |
| `reports:qr_performance`              | Collection | list, view, export   |
| `reports:qr_performance_site_to_site` | Collection | list, view, export   |
| `reports:campaign_compliance`         | Collection | list, view, export   |
| `reports:campaign_compliance_details` | Collection | list, view, export   |
| `reports:site_performance_maps`       | Collection | list, view, export   |
| `reports:media_performance_maps`      | Collection | list, view, export   |
| `reports:campaign_performance_maps`   | Collection | list, view, export   |
| `reports:content_proof_of_play`       | Collection | list, view, export   |
| `reports:export`                      | Collection | list, export, delete |

### Footprints Resource

| Resource                    | Type       | Actions                                            |
| --------------------------- | ---------- | -------------------------------------------------- |
| `footprints:sites`          | Collection | list, view, create, update, delete, export, import |
| `footprints:sites:item`     | Item       | view, update, delete                               |
| `footprints:endpoints`      | Collection | list, view, create, update, delete, export, import |
| `footprints:endpoints:item` | Item       | view, update, delete                               |
| `footprints:products`       | Collection | list, view, create, update, delete, export, import |
| `footprints:products:item`  | Item       | view, update, delete                               |
| `footprints:pricing`        | Collection | list, view, create, update, delete, export, import |

### Content Management Resource

| Resource                               | Type       | Actions                                            |
| -------------------------------------- | ---------- | -------------------------------------------------- |
| `contents:templates`                   | Collection | list, view, create, update, delete, export, import |
| `contents:templates:item`              | Item       | view, update, delete                               |
| `contents:assets`                      | Collection | list, view, create, update, delete, export, import |
| `contents:assets:item`                 | Item       | view, update, delete                               |
| `contents:playlists`                   | Collection | list, view, create, update, delete, export, import |
| `contents:playlists:item`              | Item       | view, update, delete                               |
| `contents:backgrounds`                 | Collection | list, view, create, update, delete, export, import |
| `contents:backgrounds:item`            | Item       | view, update, delete                               |
| `contents:backgrounds_transition`      | Collection | list, view, create, update, delete, export, import |
| `contents:backgrounds_transition:item` | Item       | view, update, delete                               |
| `contents:channels`                    | Collection | list, view, create, update, delete, export, import |
| `contents:channels:item`               | Item       | view, update, delete                               |
| `contents:tags`                        | Collection | list, view, create, update, delete, export, import |
| `contents:tags:item`                   | Item       | view, update, delete                               |
| `contents:tags_assignments`            | Collection | list, view, create, update, delete, export, import |
| `contents:tags_assignments:item`       | Item       | view, update, delete                               |
| `contents:content_groups`              | Collection | list, view, create, update, delete, export, import |
| `contents:content_groups:item`         | Item       | view, update, delete                               |

### Signage Resource

| Resource               | Type       | Actions                                            |
| ---------------------- | ---------- | -------------------------------------------------- |
| `signages:people`      | Collection | list, view, create, update, delete, export, import |
| `signages:people:item` | Item       | view, update, delete                               |
| `signages:places`      | Collection | list, view, create, update, delete, export, import |
| `signages:places:item` | Item       | view, update, delete                               |
| `signages:things`      | Collection | list, view, create, update, delete, export, import |
| `signages:things:item` | Item       | view, update, delete                               |

### Connect Resource

| Resource                | Type       | Actions                                            |
| ----------------------- | ---------- | -------------------------------------------------- |
| `connect:contacts`      | Collection | list, view, create, update, delete, export, import |
| `connect:contacts:item` | Item       | view, update, delete                               |

### QR Resource

| Resource            | Type       | Actions                                            |
| ------------------- | ---------- | -------------------------------------------------- |
| `qr:site`           | Collection | list, view, create, update, delete, export, import |
| `qr:site:item`      | Item       | view, update, delete                               |
| `qr:media`          | Collection | list, view, create, update, delete, export, import |
| `qr:media:item`     | Item       | view, update, delete                               |
| `qr:templates`      | Collection | list, view, create, update, delete, export, import |
| `qr:templates:item` | Item       | view, update, delete                               |
| `qr:campaigns`      | Collection | list, view, create, update, delete, export, import |
| `qr:campaigns:item` | Item       | view, update, delete                               |

## Product Settings Related Resources

### Settings - General
| Resource                               | Type | Actions              |
| -------------------------------------- | ---- | -------------------- |
| `settings:admin_general_agency:item`   | Item | view, update, delete |
| `settings:admin_general_retailer:item` | Item | view, update, delete |
| `settings:admin_general_brand:item`    | Item | view, update, delete |
| `settings:admin_general_ambient:item`  | Item | view, update, delete |

### Settings - Footprints

| Resource                                          | Type       | Actions                                            |
| ------------------------------------------------- | ---------- | -------------------------------------------------- |
| `settings:footprints_sites_property`              | Collection | list, view, create, update, delete, export, import |
| `settings:footprints_sites_property:item`         | Item       | view, update, delete                               |
| `settings:footprints_products_property`           | Collection | list, view, create, update, delete, export, import |
| `settings:footprints_products_property:item`      | Item       | view, update, delete                               |
| `settings:footprints_products_pricing_group`      | Collection | list, view, create, update, delete, export, import |
| `settings:footprints_products_pricing_group:item` | Item       | view, update, delete                               |

### Settings - QR

| Resource                            | Type       | Actions                                             |
| ----------------------------------- | ---------- | --------------------------------------------------- |
| `settings:qr_design`                | Collection | list, view, create, update, delete, export, import  |
| `settings:qr_design:item`           | Item       | view, update, delete                                |
| `settings:qr_power_tag`             | Collection | list, view, create, update, delete, export, import  |
| `settings:qr_power_tag:item`        | Item       | view, update, delete                                |
| `settings:qr_default_redirect`      | Collection | list, view, create, update, delete,  export, import |
| `settings:qr_default_redirect:item` | Item       | view, update, delete                                |
| `settings:qr_domain`                | Collection | list, view, create, update, delete, export, import  |
| `settings:qr_domain:item`           | Item       | view, update, delete                                |

### Settings - Signage

| Resource                                | Type       | Actions                                            |
| --------------------------------------- | ---------- | -------------------------------------------------- |
| `settings:signage_layout`               | Collection | list, view, create, update, delete, export, import |
| `settings:signage_layout:item`          | Item       | view, update, delete                               |
| `settings:signage_people_property`      | Collection | list, view, create, update, delete, export, import |
| `settings:signage_people_property:item` | Item       | view, update, delete                               |
| `settings:signage_places_property`      | Collection | list, view, create, update, delete, export, import |
| `settings:signage_places_property:item` | Item       | view, update, delete                               |
| `settings:signage_things_property`      | Collection | list, view, create, update, delete, export, import |
| `settings:signage_things_property:item` | Item       | view, update, delete                               |

---

## Resource Type Definitions

- **Collection**: Full CRUD operations (list, view, create, update, delete), plus export/import
- **Item**: Detail view and mutations (view, update, delete)
- **Action**: Specific operation triggers (e.g., create-template)

---

## Product × Resource Matrix

| Resource (policy file)                                                                                                           | default  | qr       | priceTags | compliance | product  | signage  | landing  | connect  | ppt      |
| -------------------------------------------------------------------------------------------------------------------------------- | -------- | -------- | --------- | ---------- | -------- | -------- | -------- | -------- | -------- |
| connect:contacts (k8s/base/policies/resource_connect_contacts.yaml)                                                              |          |          |           |            |          |          |          | required |          |
| connect:contacts:item (k8s/base/policies/resource_connect_contacts_item.yaml)                                                    |          |          |           |            |          |          |          | required |          |
| contents:assets (k8s/base/policies/resource_contents_assets.yaml)                                                                |          |          |           |            |          | required |          |          |          |
| contents:assets:item (k8s/base/policies/resource_contents_assets_item.yaml)                                                      |          |          |           |            |          | required |          |          |          |
| contents:backgrounds (k8s/base/policies/resource_contents_backgrounds.yaml)                                                      |          |          |           |            |          | required |          |          |          |
| contents:backgrounds:item (k8s/base/policies/resource_contents_backgrounds_item.yaml)                                            |          |          |           |            |          | required |          |          |          |
| contents:backgrounds_transistion (k8s/base/policies/resource_contents_backgrounds_transistion.yaml)                              |          |          |           |            |          | required |          |          |          |
| contents:backgrounds_transistion:item (k8s/base/policies/resource_contents_backgrounds_transistion_item.yaml)                    |          |          |           |            |          | required |          |          |          |
| contents:channels (k8s/base/policies/resource_contents_channels.yaml)                                                            |          |          |           |            |          | required |          |          |          |
| contents:channels:item (k8s/base/policies/resource_contents_channels_item.yaml)                                                  |          |          |           |            |          | required |          |          |          |
| contents:content_groups (k8s/base/policies/resource_contents_content_groups.yaml)                                                |          |          |           |            |          | required |          |          |          |
| contents:content_groups:item (k8s/base/policies/resource_contents_content_groups_item.yaml)                                      |          |          |           |            |          | required |          |          |          |
| contents:playlists (k8s/base/policies/resource_contents_playlists.yaml)                                                          |          |          |           |            |          | required |          |          |          |
| contents:playlists:item (k8s/base/policies/resource_contents_playlists_item.yaml)                                                |          |          |           |            |          | required |          |          |          |
| contents:tags (k8s/base/policies/resource_contents_tags.yaml)                                                                    |          | required | required  | required   | required | required |          |          |          |
| contents:tags_assignments (k8s/base/policies/resource_contents_tags_assignments.yaml)                                            |          | required | required  | required   | required | required |          |          |          |
| contents:tags_assignments:item (k8s/base/policies/resource_contents_tags_assignments_item.yaml)                                  |          | required | required  | required   | required | required |          |          |          |
| contents:tags:item (k8s/base/policies/resource_contents_tags_item.yaml)                                                          |          | required | required  | required   | required | required |          |          |          |
| contents:templates (k8s/base/policies/resource_contents_templates.yaml)                                                          |          |          | required  |            |          | required |          |          |          |
| contents:templates:item (k8s/base/policies/resource_contents_templates_item.yaml)                                                |          |          | required  |            |          | required |          |          |          |
| footprints:endpoints (k8s/base/policies/resource_footprints_endpoints.yaml)                                                      |          |          | required  |            |          | required |          |          |          |
| footprints:endpoints:item (k8s/base/policies/resource_footprints_endpoints_item.yaml)                                            |          |          | required  |            |          | required |          |          |          |
| footprints:pricing (k8s/base/policies/resource_footprints_pricing.yaml)                                                          |          |          | required  |            | required | required |          |          |          |
| footprints:products (k8s/base/policies/resource_footprints_products.yaml)                                                        |          |          | required  | required   | required | required |          |          |          |
| footprints:products:item (k8s/base/policies/resource_footprints_products_item.yaml)                                              |          |          | required  | required   | required | required |          |          |          |
| footprints:sites (k8s/base/policies/resource_footprints_sites.yaml)                                                              |          | required | required  | required   | required | required |          |          |          |
| footprints:sites:item (k8s/base/policies/resource_footprints_sites_item.yaml)                                                    |          | required | required  | required   | required | required |          |          |          |
| qr:campaigns (k8s/base/policies/resource_qr_campaigns.yaml)                                                                      |          | required | required  | required   | required | required | required | required | required |
| qr:campaigns:item (k8s/base/policies/resource_qr_campaigns_item.yaml)                                                            |          | required | required  | required   | required | required | required | required | required |
| qr:media (k8s/base/policies/resource_qr_media.yaml)                                                                              |          | required |           |            |          |          |          |          |          |
| qr:media:item (k8s/base/policies/resource_qr_media_item.yaml)                                                                    |          | required |           |            |          |          |          |          |          |
| qr:site (k8s/base/policies/resource_qr_site.yaml)                                                                                |          | required |           |            |          |          |          |          |          |
| qr:site:item (k8s/base/policies/resource_qr_site_item.yaml)                                                                      |          | required |           |            |          |          |          |          |          |
| qr:templates (k8s/base/policies/resource_qr_templates.yaml)                                                                      |          | required |           |            |          |          |          |          |          |
| qr:templates:item (k8s/base/policies/resource_qr_templates_item.yaml)                                                            |          | required |           |            |          |          |          |          |          |
| reports:campaign_compliance_details (k8s/base/policies/resource_reports_campaign_compliance_details.yaml)                        |          | required |           | required   |          | required |          |          |          |
| reports:campaign_compliance (k8s/base/policies/resource_reports_campaign_compliance.yaml)                                        |          | required |           | required   |          | required |          |          |          |
| reports:campaign_performance_maps (k8s/base/policies/resource_reports_campaign_performance_maps.yaml)                            |          | required |           | required   |          | required |          |          |          |
| reports:content_proof_of_play (k8s/base/policies/resource_reports_content_proof_of_play.yaml)                                    |          |          |           |            |          | required |          |          |          |
| reports:media_performance_maps (k8s/base/policies/resource_reports_media_performance_maps.yaml)                                  |          | required |           |            |          |          |          |          |          |
| reports:qr_performance_site_to_site (k8s/base/policies/resource_reports_qrperformance_sitetosite.yaml)                           |          | required |           |            |          |          |          |          |          |
| reports:qr_performance (k8s/base/policies/resource_reports_qrperformance.yaml)                                                   |          | required |           |            |          |          |          |          |          |
| reports:site_performance_maps (k8s/base/policies/resource_reports_site_performance_maps.yaml)                                    |          | required |           |            |          |          |          |          |          |
| reports:export (k8s/base/policies/resource_reports_export.yaml)                                                                  |          | required |           | required   | required | required |          | required |          |
| settings:admin_cerbos (k8s/base/policies/resource_settings_admin_cerbos.yaml)                                                    | required |          |           |            |          |          |          |          |          |
| settings:admin_cerbos:item (k8s/base/policies/resource_settings_admin_cerbos_item.yaml)                                          | required |          |           |            |          |          |          |          |          |
| settings:admin_general_agency:item (k8s/base/policies/resource_admin_settings_general_agency_item.yaml)                          | required |          |           |            |          |          |          |          |          |
| settings:admin_general_retailer:item (k8s/base/policies/resource_admin_settings_general_retailer_item.yaml)                      | required |          |           |            |          |          |          |          |          |
| settings:admin_general_brand:item (k8s/base/policies/resource_admin_settings_general_brand_item.yaml)                            | required |          |           |            |          |          |          |          |          |
| settings:admin_general_ambient:item (k8s/base/policies/resource_admin_settings_general_ambient_item.yaml)                        | required |          |           |            |          |          |          |          |          |
| settings:admin_teams (k8s/base/policies/resource_settings_admin_teams.yaml)                                                      | required |          |           |            |          |          |          |          |          |
| settings:admin_teams:item (k8s/base/policies/resource_settings_admin_teams_item.yaml)                                            | required |          |           |            |          |          |          |          |          |
| settings:admin_users (k8s/base/policies/resource_settings_admin_users.yaml)                                                      | required |          |           |            |          |          |          |          |          |
| settings:admin_users:item (k8s/base/policies/resource_settings_admin_users_item.yaml)                                            | required |          |           |            |          |          |          |          |          |
| settings:footprints_products_pricing_group (k8s/base/policies/resource_settings_footprints_products_pricinggroup.yaml)           |          |          | required  |            | required |          |          |          |          |
| settings:footprints_products_pricing_group:item (k8s/base/policies/resource_settings_footprints_products_pricinggroup_item.yaml) |          |          | required  |            | required |          |          |          |          |
| settings:footprints_products_property (k8s/base/policies/resource_settings_footprints_products_property.yaml)                    |          |          | required  | required   | required |          |          |          |          |
| settings:footprints_products_property:item (k8s/base/policies/resource_settings_footprints_products_property_item.yaml)          |          |          | required  | required   | required |          |          |          |          |
| settings:footprints_sites_property (k8s/base/policies/resource_settings_footprints_sites_property.yaml)                          |          | required | required  | required   |          |          |          |          |          |
| settings:footprints_sites_property:item (k8s/base/policies/resource_settings_footprints_sites_property_item.yaml)                |          | required | required  | required   |          |          |          |          |          |
| settings:qr_default_redirect (k8s/base/policies/resource_settings_qr_defaultredirect.yaml)                                       |          | required |           |            |          |          |          |          |          |
| settings:qr_default_redirect:item (k8s/base/policies/resource_settings_qr_defaultredirect_item.yaml)                             |          | required |           |            |          |          |          |          |          |
| settings:qr_design (k8s/base/policies/resource_settings_qr_design.yaml)                                                          |          | required |           |            |          |          |          |          |          |
| settings:qr_design:item (k8s/base/policies/resource_settings_qr_design_item.yaml)                                                |          | required |           |            |          |          |          |          |          |
| settings:qr_domain (k8s/base/policies/resource_settings_qr_domain.yaml)                                                          |          | required |           |            |          |          |          |          |          |
| settings:qr_domain:item (k8s/base/policies/resource_settings_qr_domain_item.yaml)                                                |          | required |           |            |          |          |          |          |          |
| settings:qr_power_tag (k8s/base/policies/resource_settings_qr_powertag.yaml)                                                     |          | required |           |            |          |          |          |          |          |
| settings:qr_power_tag:item (k8s/base/policies/resource_settings_qr_powertag_item.yaml)                                           |          | required |           |            |          |          |          |          |          |
| settings:signage_layout (k8s/base/policies/resource_settings_signage_layout.yaml)                                                |          |          |           |            |          | required |          |          |          |
| settings:signage_layout:item (k8s/base/policies/resource_settings_signage_layout_item.yaml)                                      |          |          |           |            |          | required |          |          |          |
| settings:signage_people_property (k8s/base/policies/resource_settings_signage_people_property.yaml)                              |          |          |           |            |          |          |          |          | required |
| settings:signage_people_property:item (k8s/base/policies/resource_settings_signage_people_property_item.yaml)                    |          |          |           |            |          |          |          |          | required |
| settings:signage_places_property (k8s/base/policies/resource_settings_signage_places_property.yaml)                              |          |          |           |            |          |          |          |          | required |
| settings:signage_places_property:item (k8s/base/policies/resource_settings_signage_places_property_item.yaml)                    |          |          |           |            |          |          |          |          | required |
| settings:signage_things_property (k8s/base/policies/resource_settings_signage_things_property.yaml)                              |          |          |           |            |          |          |          |          | required |
| settings:signage_things_property:item (k8s/base/policies/resource_settings_signage_things_property_item.yaml)                    |          |          |           |            |          |          |          |          | required |
| settings:user_profile:item (k8s/base/policies/resource_settings_user_profile_item.yaml)                                          | required |          |           |            |          |          |          |          |          |
| signages:people (k8s/base/policies/resource_signages_people.yaml)                                                                |          |          |           |            |          | required |          |          | required |
| signages:people:item (k8s/base/policies/resource_signages_people_item.yaml)                                                      |          |          |           |            |          | required |          |          | required |
| signages:places (k8s/base/policies/resource_signages_places.yaml)                                                                |          |          |           |            |          | required |          |          | required |
| signages:places:item (k8s/base/policies/resource_signages_places_item.yaml)                                                      |          |          |           |            |          | required |          |          | required |
| signages:things (k8s/base/policies/resource_signages_things.yaml)                                                                |          |          |           |            |          | required |          |          | required |
| signages:things:item (k8s/base/policies/resource_signages_things_item.yaml)                                                      |          |          |           |            |          | required |          |          | required |

---

## Access Control Notes

1. **Resource Segment** The first segment is called group, each features has its own groupings.

Example #1: `settings:signage_layout`
- `settings` is the group where `signage_layout` feature belongs to.

Example #2: `connect:contacts:item`
- `contacts` is a feature under the grouping `connect`
- `item` indicates that the resource is pertaining to a resource item, otherwise resource collection.

2. **Main Groupings**

- `footprints:*`
- `signages:*`
- `qr:*`
- `reports:*`
- `connect:*`
- `settings:*`
- `contents:*`
   
3. **Retailer-scoped** - A resource requires a retailer data. It is scoped to retailer-only resources.
4. **Product Validation** - A retailer-scoped resource also requires product validation. It means, the subject retailer must have the required products (listed in the Resource payload) to have access to it. See "Product x Resource Matrix" section.

5. **Cerbos Payload**

### Conditions

1. All product related resources must have product check/validation.

Example (see line 15):

```yaml
apiVersion: "api.cerbos.dev/v1"
resourcePolicy:
  version: "default"
  resource: "connect:contacts"
  importDerivedRoles:
    - conqrse_roles
  rules:
    # Retailer access with product subscription check
    - actions: ["resource:list", "resource:view", "resource:create", "resource:update", "resource:delete", "resource:export", "resource:import"]
      effect: EFFECT_ALLOW
      condition:
        match:
          all:
            of:
              - expr: '["connect"].exists(p, p in P.attr.products)'
              - expr: 'P.attr.retailerId == R.attr.retailerId'
      derivedRoles:
        - retailer_owner
        - retailer_manager
        - team_lead
        - staff_operator
```
2. All product related resources and type "Item" must have retailer ID check.

Example (see line 17):
```yaml
---
apiVersion: "api.cerbos.dev/v1"
resourcePolicy:
  version: "default"
  resource: "connect:contacts:item"
  importDerivedRoles:
    - conqrse_roles
  rules:
    # Retailer access with product subscription check
    - actions: ["resource:view", "resource:update", "resource:delete"]
      effect: EFFECT_ALLOW
      condition:
        match:
          all:
            of:
              - expr: '["connect"].exists(p, p in P.attr.products)'
              - expr: 'P.attr.retailerId == R.attr.retailerId'
      derivedRoles:
        - retailer_owner
        - retailer_manager
        - team_lead
        - staff_operator
```

## Cerbos Payload

Principal

```json
{
   "id": string - the ID of the logged in user,
   "roles": string[] - derived roles, see "k8s/base/policies/_derived_roles.yaml",
   "attr": {
      "userLevel": 'retailer', 'su', 'agency' or 'user',
      "userType": 'admin', 'collaborator', 'owner', 'lead', or 'member',
      "name": string,
      "products": string[] - list of known products (qr, priceTags, compliance, product, signage, landing, connect, ppt),
      "agencyId": string - retailer's agency ID,
      "retailerId": string - the retailer in subject,
   }
}
```
Resource

```json
{
   "id": string - the resource in subject,
   "kind": string - the resource in subject,
   "attr": {
      "retailerId": string - the retailer of the resource,
      "products": string[] - required products the retailer must have to have access to the resource,
   },
}
```