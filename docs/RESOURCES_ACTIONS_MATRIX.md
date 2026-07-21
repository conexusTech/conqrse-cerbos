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
- **cms** - Content Management System
- **ssp** - Supply-Side Platform (Deal Desk)
- **trade** - Trade (Deal Desk)
- **brand_center** - Brand Center (Deal Desk)

> Note: `ssp`, `trade`, and `brand_center` are the three products that gate access to Deal Desk (`dealdesk:*`) resources. Each resource gates on the specific product(s) its surface belongs to (per-surface), not on all three together; some shared surfaces accept any of the three, and `sites`/`blueprints` are base (no product gate). `dealdesk` itself is a resource grouping/namespace — it is NOT a product. See "DealDesk Access Model" below.

## Action Definitions

### Resource Actions
- `list` — View collection of resources with filters and pagination
- `view` — View individual resource details
- `create` — Create new resources
- `update` — Modify existing resources
- `delete` — Remove resources
- `export` — Download/export resource data
- `import` — Upload/import data

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
| `contents:tags_taxonomy`               | Collection | create                                             |
| `contents:tags_taxonomy:item`          | Item       | update, delete                                     |
| `contents:content_groups`              | Collection | list, view, create, update, delete, export, import |
| `contents:content_groups:item`         | Item       | view, update, delete                               |
| `contents:landing_pages`               | Collection | list, view, create, update, delete, export, import |
| `contents:landing_pages:item`          | Item       | view, update, delete                               |

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

### DealDesk Resource

Deal Desk is a resource grouping — NOT a product. Access is gated per-surface by the `ssp`, `trade`, and/or `brand_center` products (see the Product × Resource Matrix for each resource's gate). See "DealDesk Access Model" for the two-rule structure.

| Resource                              | Type       | Actions                                            |
| ------------------------------------- | ---------- | -------------------------------------------------- |
| `dealdesk:blueprints`                 | Collection | list, view, create, update, delete, export, import |
| `dealdesk:brand-users`                | Collection | list, view, create, update, delete, export, import |
| `dealdesk:brand-users:item`           | Item       | view, update, delete                               |
| `dealdesk:brands`                     | Collection | list, view, create, update, delete, export, import |
| `dealdesk:brands:item`                | Item       | view, update, delete                               |
| `dealdesk:campaigns`                  | Collection | list, view, create, update, delete, export, import |
| `dealdesk:campaigns:item`             | Item       | view, update, delete                               |
| `dealdesk:dsp-blocks`                 | Collection | list, view, create, update, delete, export, import |
| `dealdesk:dsp-blocks:item`            | Item       | view, update, delete                               |
| `dealdesk:inventory`                  | Collection | list, view, create, update, delete, export, import |
| `dealdesk:inventory-provisioning`     | Collection | create                                             |
| `dealdesk:line-items`                 | Collection | list, view, create, update, delete, export, import |
| `dealdesk:line-items:item`            | Item       | view, update, delete                               |
| `dealdesk:media-packages`             | Collection | list, view, create, update, delete, export, import |
| `dealdesk:media-packages:item`        | Item       | view, update, delete                               |
| `dealdesk:photo-verifications`        | Collection | list, view, create, update, delete, export, import |
| `dealdesk:photo-verifications:item`   | Item       | view, update, delete                               |
| `dealdesk:placement-rules`            | Collection | list, view, create, update, delete, export, import |
| `dealdesk:placement-rules:item`       | Item       | view, update, delete                               |
| `dealdesk:placement-types`            | Collection | list, view, create, update, delete, export, import |
| `dealdesk:placement-types:item`       | Item       | view, update, delete                               |
| `dealdesk:rate-cards`                 | Collection | list, view, create, update, delete, export, import |
| `dealdesk:reports`                    | Collection | list, view, export                                 |
| `dealdesk:sites`                      | Collection | list, view, create, update, delete, export, import |
| `dealdesk:ssp`                        | Collection | list, view, create, update                         |
| `dealdesk:store-traffic`              | Collection | list, view, create, update, delete, export, import |
| `dealdesk:trade-ledgers`              | Collection | list, view, create, update, delete, export, import |
| `dealdesk:trade-ledgers:item`         | Item       | view, update, delete                               |
| `dealdesk_brand:media-packages`       | Collection | list, view                                         |

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

### CMS Resource

| Resource              | Type       | Actions                                            |
| --------------------- | ---------- | -------------------------------------------------- |
| `cms:collection`      | Collection | list, view, create, update, delete, export, import |
| `cms:collection:item` | Item       | view, update, delete                               |
| `cms:entry`           | Collection | list, view, create, update, delete, export, import |
| `cms:entry:item`      | Item       | view, update, delete                               |
| `cms:field`           | Collection | list, view, create, update, delete, export, import |
| `cms:field:item`      | Item       | view, update, delete                               |
| `cms:invitation`      | Collection | list, view, create, update, delete, export, import |
| `cms:invitation:item` | Item       | view, update, delete                               |
| `cms:website`         | Collection | list, view, create, update, delete, export, import |
| `cms:website:item`    | Item       | view, update, delete                               |
| `cms:page`            | Collection | list, view, create, update, delete, export, import |
| `cms:page:item`       | Item       | view, update, delete                               |
| `cms:section`         | Collection | list, view, create, update, delete, export, import |
| `cms:section:item`    | Item       | view, update, delete                               |
| `cms:block`           | Collection | list, view, create, update, delete, export, import |
| `cms:block:item`      | Item       | view, update, delete                               |
| `cms:api_key`         | Collection | list, view, create, update, delete, export, import |
| `cms:api_key:item`    | Item       | view, update, delete                               |

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

| Resource                                        | File Name                                                    | default  | qr       | priceTags | compliance | product  | signage  | landing  | connect  | ppt      | cms      | ssp          | trade        | brand_center |
| ----------------------------------------------- | ------------------------------------------------------------ | -------- | -------- | --------- | ---------- | -------- | -------- | -------- | -------- | -------- | -------- | ------------ | ------------ | ------------ |
| cms:api_key                                     | resource_cms_api_key.yaml                                    |          |          |           |            |          |          |          |          |          | required |              |              |              |
| cms:api_key:item                                | resource_cms_api_key_item.yaml                               |          |          |           |            |          |          |          |          |          | required |              |              |              |
| cms:block                                       | resource_cms_block.yaml                                      |          |          |           |            |          |          |          |          |          | required |              |              |              |
| cms:block:item                                  | resource_cms_block_item.yaml                                 |          |          |           |            |          |          |          |          |          | required |              |              |              |
| cms:collection                                  | resource_cms_collection.yaml                                 |          |          |           |            |          |          |          |          |          | required |              |              |              |
| cms:collection:item                             | resource_cms_collection_item.yaml                            |          |          |           |            |          |          |          |          |          | required |              |              |              |
| cms:entry                                       | resource_cms_entry.yaml                                      |          |          |           |            |          |          |          |          |          | required |              |              |              |
| cms:entry:item                                  | resource_cms_entry_item.yaml                                 |          |          |           |            |          |          |          |          |          | required |              |              |              |
| cms:field                                       | resource_cms_field.yaml                                      |          |          |           |            |          |          |          |          |          | required |              |              |              |
| cms:field:item                                  | resource_cms_field_item.yaml                                 |          |          |           |            |          |          |          |          |          | required |              |              |              |
| cms:invitation                                  | resource_cms_invitation.yaml                                 |          |          |           |            |          |          |          |          |          | required |              |              |              |
| cms:invitation:item                             | resource_cms_invitation_item.yaml                            |          |          |           |            |          |          |          |          |          | required |              |              |              |
| cms:page                                        | resource_cms_page.yaml                                       |          |          |           |            |          |          |          |          |          | required |              |              |              |
| cms:page:item                                   | resource_cms_page_item.yaml                                  |          |          |           |            |          |          |          |          |          | required |              |              |              |
| cms:section                                     | resource_cms_section.yaml                                    |          |          |           |            |          |          |          |          |          | required |              |              |              |
| cms:section:item                                | resource_cms_section_item.yaml                               |          |          |           |            |          |          |          |          |          | required |              |              |              |
| cms:website                                     | resource_cms_website.yaml                                    |          |          |           |            |          |          |          |          |          | required |              |              |              |
| cms:website:item                                | resource_cms_website_item.yaml                               |          |          |           |            |          |          |          |          |          | required |              |              |              |
| connect:contacts                                | resource_connect_contacts.yaml                               |          |          |           |            |          |          |          | required |          |          |              |              |              |
| connect:contacts:item                           | resource_connect_contacts_item.yaml                          |          |          |           |            |          |          |          | required |          |          |              |              |              |
| contents:assets                                 | resource_contents_assets.yaml                                |          |          |           |            |          | required |          |          |          |          |              |              |              |
| contents:assets:item                            | resource_contents_assets_item.yaml                           |          |          |           |            |          | required |          |          |          |          |              |              |              |
| contents:backgrounds                            | resource_contents_backgrounds.yaml                           |          |          |           |            |          | required |          |          |          |          |              |              |              |
| contents:backgrounds:item                       | resource_contents_backgrounds_item.yaml                      |          |          |           |            |          | required |          |          |          |          |              |              |              |
| contents:backgrounds_transition                 | resource_contents_backgrounds_transition.yaml                |          |          |           |            |          | required |          |          |          |          |              |              |              |
| contents:backgrounds_transition:item            | resource_contents_backgrounds_transition_item.yaml           |          |          |           |            |          | required |          |          |          |          |              |              |              |
| contents:channels                               | resource_contents_channels.yaml                              |          |          |           |            |          | required |          |          |          |          |              |              |              |
| contents:channels:item                          | resource_contents_channels_item.yaml                         |          |          |           |            |          | required |          |          |          |          |              |              |              |
| contents:content_groups                         | resource_contents_content_groups.yaml                        |          |          |           |            |          | required |          |          |          |          |              |              |              |
| contents:content_groups:item                    | resource_contents_content_groups_item.yaml                   |          |          |           |            |          | required |          |          |          |          |              |              |              |
| contents:landing_pages                          | resource_contents_landing_pages.yaml                         |          |          |           |            |          |          | required |          |          |          |              |              |              |
| contents:landing_pages:item                     | resource_contents_landing_pages_item.yaml                    |          |          |           |            |          |          | required |          |          |          |              |              |              |
| contents:playlists                              | resource_contents_playlists.yaml                             |          |          |           |            |          | required |          |          |          |          |              |              |              |
| contents:playlists:item                         | resource_contents_playlists_item.yaml                        |          |          |           |            |          | required |          |          |          |          |              |              |              |
| contents:tags                                   | resource_contents_tags.yaml                                  |          | required | required  | required   | required | required |          |          |          |          | required     | required     | required     |
| contents:tags:item                              | resource_contents_tags_item.yaml                             |          | required | required  | required   | required | required |          |          |          |          | required     | required     | required     |
| contents:tags_assignments                       | resource_contents_tags_assignments.yaml                      |          | required | required  | required   | required | required |          |          |          |          | required     | required     | required     |
| contents:tags_assignments:item                  | resource_contents_tags_assignments_item.yaml                 |          | required | required  | required   | required | required |          |          |          |          | required     | required     | required     |
| contents:tags_taxonomy                          | resource_contents_tags_taxonomy.yaml                         |          | required-admin | required-admin | required-admin | required-admin | required-admin |          |          |          |          | required-admin | required-admin | required-admin |
| contents:tags_taxonomy:item                     | resource_contents_tags_taxonomy_item.yaml                    |          | required-admin | required-admin | required-admin | required-admin | required-admin |          |          |          |          | required-admin | required-admin | required-admin |
| contents:templates                              | resource_contents_templates.yaml                             |          |          | required  |            |          | required |          |          |          |          |              |              |              |
| contents:templates:item                         | resource_contents_templates_item.yaml                        |          |          | required  |            |          | required |          |          |          |          |              |              |              |
| dealdesk:blueprints                             | resource_dealdesk_blueprints.yaml                            |          |          |           |            |          |          |          |          |          |          |              |              |              |
| dealdesk:brand-users                            | resource_dealdesk_brand-users.yaml                           |          |          |           |            |          |          |          |          |          |          |              |              | required     |
| dealdesk:brand-users:item                       | resource_dealdesk_brand-users_item.yaml                      |          |          |           |            |          |          |          |          |          |          |              |              | required     |
| dealdesk:brands                                 | resource_dealdesk_brands.yaml                                |          |          |           |            |          |          |          |          |          |          |              |              | required     |
| dealdesk:brands:item                            | resource_dealdesk_brands_item.yaml                           |          |          |           |            |          |          |          |          |          |          |              |              | required     |
| dealdesk:campaigns                              | resource_dealdesk_campaigns.yaml                             |          |          |           |            |          |          |          |          |          |          | required     | required     | required     |
| dealdesk:campaigns:item                         | resource_dealdesk_campaigns_item.yaml                        |          |          |           |            |          |          |          |          |          |          | required     | required     | required     |
| dealdesk:dsp-blocks                             | resource_dealdesk_dsp-blocks.yaml                            |          |          |           |            |          |          |          |          |          |          | required     |              |              |
| dealdesk:dsp-blocks:item                        | resource_dealdesk_dsp-blocks_item.yaml                       |          |          |           |            |          |          |          |          |          |          | required     |              |              |
| dealdesk:inventory                              | resource_dealdesk_inventory.yaml                             |          |          |           |            |          |          |          |          |          |          | required     | required     | required     |
| dealdesk:inventory-provisioning                 | resource_dealdesk_inventory-provisioning.yaml                |          |          |           |            |          |          |          |          |          |          | required-admin |              |              |
| dealdesk:line-items                             | resource_dealdesk_line-items.yaml                            |          |          |           |            |          |          |          |          |          |          |              | required     |              |
| dealdesk:line-items:item                        | resource_dealdesk_line-items_item.yaml                       |          |          |           |            |          |          |          |          |          |          |              | required     |              |
| dealdesk:media-packages                         | resource_dealdesk_media-packages.yaml                        |          |          |           |            |          |          |          |          |          |          |              | required     |              |
| dealdesk:media-packages:item                    | resource_dealdesk_media-packages_item.yaml                   |          |          |           |            |          |          |          |          |          |          |              | required     |              |
| dealdesk:photo-verifications                    | resource_dealdesk_photo-verifications.yaml                   |          |          |           |            |          |          |          |          |          |          |              | required     |              |
| dealdesk:photo-verifications:item               | resource_dealdesk_photo-verifications_item.yaml              |          |          |           |            |          |          |          |          |          |          |              | required     |              |
| dealdesk:placement-rules                        | resource_dealdesk_placement-rules.yaml                       |          |          |           |            |          |          |          |          |          |          | required     | required     | required     |
| dealdesk:placement-rules:item                   | resource_dealdesk_placement-rules_item.yaml                  |          |          |           |            |          |          |          |          |          |          | required     | required     | required     |
| dealdesk:placement-types                        | resource_dealdesk_placement-types.yaml                       |          |          |           |            |          |          |          |          |          |          | required     | required     | required     |
| dealdesk:placement-types:item                   | resource_dealdesk_placement-types_item.yaml                  |          |          |           |            |          |          |          |          |          |          | required     | required     | required     |
| dealdesk:rate-cards                             | resource_dealdesk_rate-cards.yaml                            |          |          |           |            |          |          |          |          |          |          | required     | required     | required     |
| dealdesk:reports                                | resource_dealdesk_reports.yaml                               |          |          |           |            |          |          |          |          |          |          | required     | required     | required     |
| dealdesk:sites                                  | resource_dealdesk_sites.yaml                                 |          |          |           |            |          |          |          |          |          |          |              |              |              |
| dealdesk:ssp                                    | resource_dealdesk_ssp.yaml                                   |          |          |           |            |          |          |          |          |          |          | required     |              |              |
| dealdesk:store-traffic                          | resource_dealdesk_store-traffic.yaml                         |          |          |           |            |          |          |          |          |          |          | required     | required     |              |
| dealdesk:trade-ledgers                          | resource_dealdesk_trade-ledgers.yaml                         |          |          |           |            |          |          |          |          |          |          |              | required     |              |
| dealdesk:trade-ledgers:item                     | resource_dealdesk_trade-ledgers_item.yaml                    |          |          |           |            |          |          |          |          |          |          |              | required     |              |
| dealdesk_brand:media-packages                   | resource_dealdesk_brand_media-packages.yaml                  |          |          |           |            |          |          |          |          |          |          |              |              | required     |
| footprints:endpoints                            | resource_footprints_endpoints.yaml                           |          |          | required  |            |          | required |          |          |          |          |              |              |              |
| footprints:endpoints:item                       | resource_footprints_endpoints_item.yaml                      |          |          | required  |            |          | required |          |          |          |          |              |              |              |
| footprints:pricing                              | resource_footprints_pricing.yaml                             |          |          | required  |            | required | required |          |          |          |          |              |              |              |
| footprints:products                             | resource_footprints_products.yaml                            |          |          | required  | required   | required | required |          |          |          |          |              |              |              |
| footprints:products:item                        | resource_footprints_products_item.yaml                       |          |          | required  | required   | required | required |          |          |          |          |              |              |              |
| footprints:sites                                | resource_footprints_sites.yaml                               |          | required | required  | required   | required | required |          |          |          |          |              |              |              |
| footprints:sites:item                           | resource_footprints_sites_item.yaml                          |          | required | required  | required   | required | required |          |          |          |          |              |              |              |
| qr:campaigns                                    | resource_qr_campaigns.yaml                                   |          | required | required  | required   | required | required | required | required | required |          |              |              |              |
| qr:campaigns:item                               | resource_qr_campaigns_item.yaml                              |          | required | required  | required   | required | required | required | required | required |          |              |              |              |
| qr:media                                        | resource_qr_media.yaml                                       |          | required |           |            |          |          |          |          |          |          |              |              |              |
| qr:media:item                                   | resource_qr_media_item.yaml                                  |          | required |           |            |          |          |          |          |          |          |              |              |              |
| qr:site                                         | resource_qr_site.yaml                                        |          | required |           |            |          |          |          |          |          |          |              |              |              |
| qr:site:item                                    | resource_qr_site_item.yaml                                   |          | required |           |            |          |          |          |          |          |          |              |              |              |
| qr:templates                                    | resource_qr_templates.yaml                                   |          | required |           |            |          |          |          |          |          |          |              |              |              |
| qr:templates:item                               | resource_qr_templates_item.yaml                              |          | required |           |            |          |          |          |          |          |          |              |              |              |
| reports:campaign_compliance                     | resource_reports_campaign_compliance.yaml                    |          | required |           | required   |          | required |          |          |          |          |              |              |              |
| reports:campaign_compliance_details             | resource_reports_campaign_compliance_details.yaml            |          | required |           | required   |          | required |          |          |          |          |              |              |              |
| reports:campaign_performance_maps               | resource_reports_campaign_performance_maps.yaml              |          | required |           | required   |          | required |          |          |          |          |              |              |              |
| reports:content_proof_of_play                   | resource_reports_content_proof_of_play.yaml                  |          |          |           |            |          | required |          |          |          |          |              |              |              |
| reports:export                                  | resource_reports_export.yaml                                 |          | required |           | required   | required | required |          | required |          |          |              |              |              |
| reports:media_performance_maps                  | resource_reports_media_performance_maps.yaml                 |          | required |           |            |          |          |          |          |          |          |              |              |              |
| reports:qr_performance                          | resource_reports_qr_performance.yaml                          |          | required |           |            |          |          |          |          |          |          |              |              |              |
| reports:qr_performance_site_to_site             | resource_reports_qr_performance_site_to_site.yaml             |          | required |           |            |          |          |          |          |          |          |              |              |              |
| reports:site_performance_maps                   | resource_reports_site_performance_maps.yaml                  |          | required |           |            |          |          |          |          |          |          |              |              |              |
| settings:admin_cerbos                           | resource_settings_admin_cerbos.yaml                          | required |          |           |            |          |          |          |          |          |          |              |              |              |
| settings:admin_cerbos:item                      | resource_settings_admin_cerbos_item.yaml                     | required |          |           |            |          |          |          |          |          |          |              |              |              |
| settings:admin_general_agency:item              | resource_admin_settings_general_agency_item.yaml             | required |          |           |            |          |          |          |          |          |          |              |              |              |
| settings:admin_general_ambient:item             | resource_admin_settings_general_ambient_item.yaml            | required |          |           |            |          |          |          |          |          |          |              |              |              |
| settings:admin_general_brand:item               | resource_admin_settings_general_brand_item.yaml              | required |          |           |            |          |          |          |          |          |          |              |              |              |
| settings:admin_general_retailer:item            | resource_admin_settings_general_retailer_item.yaml           | required |          |           |            |          |          |          |          |          |          |              |              |              |
| settings:admin_teams                            | resource_settings_admin_teams.yaml                           | required |          |           |            |          |          |          |          |          |          |              |              |              |
| settings:admin_teams:item                       | resource_settings_admin_teams_item.yaml                      | required |          |           |            |          |          |          |          |          |          |              |              |              |
| settings:admin_users                            | resource_settings_admin_users.yaml                           | required |          |           |            |          |          |          |          |          |          |              |              |              |
| settings:admin_users:item                       | resource_settings_admin_users_item.yaml                      | required |          |           |            |          |          |          |          |          |          |              |              |              |
| settings:footprints_products_pricing_group      | resource_settings_footprints_products_pricing_group.yaml      |          |          | required  |            | required |          |          |          |          |          |              |              |              |
| settings:footprints_products_pricing_group:item | resource_settings_footprints_products_pricing_group_item.yaml |          |          | required  |            | required |          |          |          |          |          |              |              |              |
| settings:footprints_products_property           | resource_settings_footprints_products_property.yaml          |          |          | required  | required   | required |          |          |          |          |          |              |              |              |
| settings:footprints_products_property:item      | resource_settings_footprints_products_property_item.yaml     |          |          | required  | required   | required |          |          |          |          |          |              |              |              |
| settings:footprints_sites_property              | resource_settings_footprints_sites_property.yaml             |          | required | required  | required   |          |          |          |          |          |          |              |              |              |
| settings:footprints_sites_property:item         | resource_settings_footprints_sites_property_item.yaml        |          | required | required  | required   |          |          |          |          |          |          |              |              |              |
| settings:qr_default_redirect                    | resource_settings_qr_default_redirect.yaml                    |          | required |           |            |          |          |          |          |          |          |              |              |              |
| settings:qr_default_redirect:item               | resource_settings_qr_default_redirect_item.yaml               |          | required |           |            |          |          |          |          |          |          |              |              |              |
| settings:qr_design                              | resource_settings_qr_design.yaml                             |          | required |           |            |          |          |          |          |          |          |              |              |              |
| settings:qr_design:item                         | resource_settings_qr_design_item.yaml                        |          | required |           |            |          |          |          |          |          |          |              |              |              |
| settings:qr_domain                              | resource_settings_qr_domain.yaml                             |          | required |           |            |          |          |          |          |          |          |              |              |              |
| settings:qr_domain:item                         | resource_settings_qr_domain_item.yaml                        |          | required |           |            |          |          |          |          |          |          |              |              |              |
| settings:qr_power_tag                           | resource_settings_qr_power_tag.yaml                           |          | required |           |            |          |          |          |          |          |          |              |              |              |
| settings:qr_power_tag:item                      | resource_settings_qr_power_tag_item.yaml                      |          | required |           |            |          |          |          |          |          |          |              |              |              |
| settings:signage_layout                         | resource_settings_signage_layout.yaml                        |          |          |           |            |          | required |          |          |          |          |              |              |              |
| settings:signage_layout:item                    | resource_settings_signage_layout_item.yaml                   |          |          |           |            |          | required |          |          |          |          |              |              |              |
| settings:signage_people_property                | resource_settings_signage_people_property.yaml               |          |          |           |            |          |          |          |          | required |          |              |              |              |
| settings:signage_people_property:item           | resource_settings_signage_people_property_item.yaml          |          |          |           |            |          |          |          |          | required |          |              |              |              |
| settings:signage_places_property                | resource_settings_signage_places_property.yaml               |          |          |           |            |          |          |          |          | required |          |              |              |              |
| settings:signage_places_property:item           | resource_settings_signage_places_property_item.yaml          |          |          |           |            |          |          |          |          | required |          |              |              |              |
| settings:signage_things_property                | resource_settings_signage_things_property.yaml               |          |          |           |            |          |          |          |          | required |          |              |              |              |
| settings:signage_things_property:item           | resource_settings_signage_things_property_item.yaml          |          |          |           |            |          |          |          |          | required |          |              |              |              |
| settings:user_profile:item                      | resource_settings_user_profile_item.yaml                     | required |          |           |            |          |          |          |          |          |          |              |              |              |
| signages:people                                 | resource_signages_people.yaml                                |          |          |           |            |          | required |          |          | required |          |              |              |              |
| signages:people:item                            | resource_signages_people_item.yaml                           |          |          |           |            |          | required |          |          | required |          |              |              |              |
| signages:places                                 | resource_signages_places.yaml                                |          |          |           |            |          | required |          |          | required |          |              |              |              |
| signages:places:item                            | resource_signages_places_item.yaml                           |          |          |           |            |          | required |          |          | required |          |              |              |              |
| signages:things                                 | resource_signages_things.yaml                                |          |          |           |            |          | required |          |          | required |          |              |              |              |
| signages:things:item                            | resource_signages_things_item.yaml                           |          |          |           |            |          | required |          |          | required |          |              |              |              |

---

## Access Control Notes

1. **Resource Segment** The first segment is called group, each features has its own groupings.

Example #1: `settings:signage_layout`
- `settings` is the group where `signage_layout` feature belongs to.

Example #2: `connect:contacts:item`
- `contacts` is a feature under the grouping `connect`
- `item` indicates that the resource is pertaining to a resource item, otherwise resource collection.

**Settings as a cross-cutting concern.** Settings resources use the `settings:{context}_{feature}` pattern (underscore-separated) — deliberately separate from product-namespaced resources. Adding a new product doesn't require adding new settings policies; every product/admin setting follows the same semantic structure. Patterns in use:

- `settings:admin_*` — Platform/system-level settings (owners/admins only)
- `settings:user_*` — User-specific settings (personal profile, preferences)
- `settings:{product}_{feature}` — Product-specific configuration (e.g., `settings:qr_design`, `settings:signage_layout`)
- `settings:{product}_{feature}_{category}` — Sub-categories within product settings

2. **Main Groupings**

- `footprints:*`
- `signages:*`
- `qr:*`
- `reports:*`
- `connect:*`
- `settings:*`
- `contents:*`
- `dealdesk:*` (and legacy `dealdesk_brand:*`)
- `cms:*`

3. **Retailer-scoped** - A resource requires a retailer data. It is scoped to retailer-only resources.
4. **Product Validation** - A retailer-scoped resource also requires product validation. It means, the subject retailer must have the required products (listed in the Resource payload) to have access to it. See "Product x Resource Matrix" section.

5. **Role Hierarchy** - Product-related resources support hierarchical role access:
   - **SU Level (Super User)**: root_user, platform_administrator, platform_lead, platform_member, platform_collaborator
   - **Agency Level**: agency_owner, agency_manager, agency_lead, agency_member, agency_collaborator
   - **Retailer Level**: retailer_owner, retailer_manager, team_lead, staff_operator, guest_collaborator
   - **Brand Level** (Deal Desk only): brand_owner, brand_manager, brand_lead, brand_member

   SU and Agency-level roles have access to all product-scoped resources (when retailerId matches and required products are present) with the same permissions as Retailer-level owners/managers. Brand-level roles are scoped to Deal Desk (`dealdesk:*`) resources only.

6. **Product Marker Semantics** - The Product × Resource Matrix uses two markers:
   - `required` — OR semantics. When a row has multiple `required` cells, the generated CEL is `["p1","p2",...].exists(p, p in P.attr.products)` (any one product grants access).
   - `required-all` — AND semantics. When a row has multiple `required-all` cells, the generated CEL is `["p1","p2",...].all(p, p in P.attr.products)` (all listed products are required simultaneously). **Deprecated / no longer used:** DealDesk originally used this to require `ssp` + `trade` + `brand_center` together, but as of the per-surface gating change each DealDesk resource now gates on its own product(s) via `required` (OR) semantics. No resource currently uses `required-all`.

7. **DealDesk Access Model** - Every `dealdesk:*` policy has two rule blocks that OR together at the policy level:

   **Retailer path** — for principals with `userLevel` ∈ {su, agency, retailer}:
   - Product check: **per-surface** — each resource gates on the product(s) its surface belongs to, not on all three together. The gate is one of:
     - single product: `"ssp" in P.attr.products` (SSP: `ssp`, `dsp-blocks`), `"trade" in P.attr.products` (Trade: `trade-ledgers`, `media-packages`, `line-items`, `photo-verifications`), `"brand_center" in P.attr.products` (Brand Center: `brands`, `brand-users`, `dealdesk_brand:media-packages`).
     - any-of-three (shared shell): `["ssp","trade","brand_center"].exists(p, p in P.attr.products)` (`campaigns`, `inventory`, `reports`, `placement-rules`, `placement-types`, `rate-cards`).
     - ssp-or-trade: `["ssp","trade"].exists(p, p in P.attr.products)` (`store-traffic`).
     - base — no product check at all (all retailers): `sites`, `blueprints` (Footprint store-map / blueprint).
   - SU/agency do **not** bypass the product check — they follow the same per-surface gate as retailer roles (confirmed against existing policy convention).
   - Tenancy check (for `:item` resources): `P.attr.retailerId == R.attr.retailerId`.
   - Derived roles: SU tier, Agency tier, and Retailer tier as usual.

   **Brand path** — for principals with `userLevel == "brand"`:
   - Product check: `["brand_center"].exists(p, p in P.attr.products)` — the brand user's own products must include brand_center.
   - Cross-retailer scoping: `R.attr.retailerId in P.attr.retailerIds` — the brand's linked retailers list must include the resource's retailer.
   - Derived roles: `brand_owner`, `brand_manager`, `brand_lead`, `brand_member`.

   **Entity relationships**:
   - Retailer.Brands[] — a Retailer has many Brands (mirrors Agency.Retailers[]).
   - Brand.Retailers[] — a Brand has many Retailers. This is the source list for `P.attr.retailerIds` when a Brand user is the principal.

6. **Cerbos Payload**

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
    - actions: ["list", "view", "create", "update", "delete", "export", "import"]
      effect: EFFECT_ALLOW
      condition:
        match:
          all:
            of:
              - expr: '["connect"].exists(p, p in P.attr.products)'
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
    - actions: ["view", "update", "delete"]
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
      "userLevel": 'su', 'agency', 'retailer', 'brand', or 'user',
      "userType": 'owner', 'admin', 'lead', 'member', or 'collaborator',
      "name": string,
      "products": string[] - list of known products (qr, priceTags, compliance, product, signage, landing, connect, ppt, cms, ssp, trade, brand_center),
      "agencyId": string - retailer's agency ID,
      "retailerId": string - the retailer in subject (SU/Agency/Retailer users),
      "brandId": string - the brand in subject (Brand users only),
      "retailerIds": string[] - retailers linked to the brand via Brand.Retailers[] (Brand users only; used for cross-retailer dealdesk access),
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