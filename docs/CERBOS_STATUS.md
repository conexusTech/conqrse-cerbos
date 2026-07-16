# Cerbos Status

**Purpose:** Single source of truth for what Cerbos policies are implemented, deployed, and consumed. Refreshed on demand by running `python3 scripts/generate_status.py`.

**Audience:** QA, PMs, operators — everyone who needs to see what's live vs what's in the repo without reading YAML.

> **See drift below?** Follow the [HOW TO — Update seeded policies](../README.md#how-to--update-seeded-policies-new--modified--removed) workflow in the README to bring an environment back in sync. Any policy change also requires bumping [`@conqrse/permission-types`](../README.md#how-to--update-conqrsepermission-types).

- **Last regenerated:** 2026-07-15T10:38:16+00:00
- **Repo HEAD:** `dacf3760ff98` — docs: consolidate cerbos docs and add CERBOS_STATUS SSoT
- **HEAD author / date:** Joe Lacerna · 2026-07-15T17:01:35+08:00
- **Unpushed commits on HEAD branch:** 2
- **kubectl context:** `arn:aws:eks:us-east-1:082585646836:cluster/conqrse`

| Environment | Cerbos ready | Deployment last updated | Policies in ConfigMap |
| --- | --- | --- | --- |
| staging | ✅ 1/1 | 2026-07-11T06:30:07Z | 114 |
| production | ✅ 1/1 | 2026-07-11T06:30:22Z | 114 |

## 1. Status by Consumer

Total resources declared in the matrix: **131**

| Consumer | Integrated | Planned | Coverage |
| --- | --- | --- | --- |
| **conqrse-api3** | 0 | 0 | 0/131 (0%) |
| **admin** | 0 | 0 | 0/131 (0%) |

### conqrse-api3

> Main API. Serves retailer, agency, and SU users. Expected to eventually cover every product-related resource kind.

_No resources integrated yet._

### admin

> Internal admin/back-office UI. Focuses on SU and Agency operations, admin_users/admin_teams/admin_cerbos, and platform-wide settings.

_No resources integrated yet._

## 2. Vocabulary

### Products

- `brand_center`
- `cms`
- `compliance`
- `connect`
- `landing`
- `ppt`
- `priceTags`
- `product`
- `qr`
- `signage`
- `ssp`
- `trade`

### User Levels

- `su`
- `agency`
- `retailer`
- `brand`

### User Types

- `owner`
- `admin`
- `lead`
- `member`
- `collaborator`

### Derived Roles (userLevel + userType matrix)

| Tier | Roles |
| --- | --- |
| **SU** | `root_user`, `platform_administrator`, `platform_lead`, `platform_member`, `platform_collaborator` |
| **Agency** | `agency_owner`, `agency_manager`, `agency_lead`, `agency_member`, `agency_collaborator` |
| **Retailer** | `retailer_owner`, `retailer_manager`, `team_lead`, `staff_operator`, `guest_collaborator` |
| **Brand** | `brand_owner`, `brand_manager`, `brand_lead`, `brand_member` |

## 3. Resources

Total: **131** resources across all groupings.

### `cms:*` (18)

| Resource | Type | Actions |
| --- | --- | --- |
| `cms:api_key` | collection | list, view, create, update, delete, export, import |
| `cms:api_key:item` | item | view, update, delete |
| `cms:block` | collection | list, view, create, update, delete, export, import |
| `cms:block:item` | item | view, update, delete |
| `cms:collection` | collection | list, view, create, update, delete, export, import |
| `cms:collection:item` | item | view, update, delete |
| `cms:entry` | collection | list, view, create, update, delete, export, import |
| `cms:entry:item` | item | view, update, delete |
| `cms:field` | collection | list, view, create, update, delete, export, import |
| `cms:field:item` | item | view, update, delete |
| `cms:invitation` | collection | list, view, create, update, delete, export, import |
| `cms:invitation:item` | item | view, update, delete |
| `cms:page` | collection | list, view, create, update, delete, export, import |
| `cms:page:item` | item | view, update, delete |
| `cms:section` | collection | list, view, create, update, delete, export, import |
| `cms:section:item` | item | view, update, delete |
| `cms:website` | collection | list, view, create, update, delete, export, import |
| `cms:website:item` | item | view, update, delete |

### `connect:*` (2)

| Resource | Type | Actions |
| --- | --- | --- |
| `connect:contacts` | collection | list, view, create, update, delete, export, import |
| `connect:contacts:item` | item | view, update, delete |

### `contents:*` (20)

| Resource | Type | Actions |
| --- | --- | --- |
| `contents:assets` | collection | list, view, create, update, delete, export, import |
| `contents:assets:item` | item | view, update, delete |
| `contents:backgrounds` | collection | list, view, create, update, delete, export, import |
| `contents:backgrounds:item` | item | view, update, delete |
| `contents:backgrounds_transition` | collection | list, view, create, update, delete, export, import |
| `contents:backgrounds_transition:item` | item | view, update, delete |
| `contents:channels` | collection | list, view, create, update, delete, export, import |
| `contents:channels:item` | item | view, update, delete |
| `contents:content_groups` | collection | list, view, create, update, delete, export, import |
| `contents:content_groups:item` | item | view, update, delete |
| `contents:landing_pages` | collection | list, view, create, update, delete, export, import |
| `contents:landing_pages:item` | item | view, update, delete |
| `contents:playlists` | collection | list, view, create, update, delete, export, import |
| `contents:playlists:item` | item | view, update, delete |
| `contents:tags` | collection | list, view, create, update, delete, export, import |
| `contents:tags:item` | item | view, update, delete |
| `contents:tags_assignments` | collection | list, view, create, update, delete, export, import |
| `contents:tags_assignments:item` | item | view, update, delete |
| `contents:templates` | collection | list, view, create, update, delete, export, import |
| `contents:templates:item` | item | view, update, delete |

### `dealdesk:*` (27)

| Resource | Type | Actions |
| --- | --- | --- |
| `dealdesk:blueprints` | collection | list, view, create, update, delete, export, import |
| `dealdesk:brand-users` | collection | list, view, create, update, delete, export, import |
| `dealdesk:brand-users:item` | item | view, update, delete |
| `dealdesk:brands` | collection | list, view, create, update, delete, export, import |
| `dealdesk:brands:item` | item | view, update, delete |
| `dealdesk:campaigns` | collection | list, view, create, update, delete, export, import |
| `dealdesk:campaigns:item` | item | view, update, delete |
| `dealdesk:dsp-blocks` | collection | list, view, create, update, delete, export, import |
| `dealdesk:dsp-blocks:item` | item | view, update, delete |
| `dealdesk:inventory` | collection | list, view, create, update, delete, export, import |
| `dealdesk:line-items` | collection | list, view, create, update, delete, export, import |
| `dealdesk:line-items:item` | item | view, update, delete |
| `dealdesk:media-packages` | collection | list, view, create, update, delete, export, import |
| `dealdesk:media-packages:item` | item | view, update, delete |
| `dealdesk:photo-verifications` | collection | list, view, create, update, delete, export, import |
| `dealdesk:photo-verifications:item` | item | view, update, delete |
| `dealdesk:placement-rules` | collection | list, view, create, update, delete, export, import |
| `dealdesk:placement-rules:item` | item | view, update, delete |
| `dealdesk:placement-types` | collection | list, view, create, update, delete, export, import |
| `dealdesk:placement-types:item` | item | view, update, delete |
| `dealdesk:rate-cards` | collection | list, view, create, update, delete, export, import |
| `dealdesk:reports` | collection | list, view, export |
| `dealdesk:sites` | collection | list, view, create, update, delete, export, import |
| `dealdesk:ssp` | collection | list, view, create |
| `dealdesk:store-traffic` | collection | list, view, create, update, delete, export, import |
| `dealdesk:trade-ledgers` | collection | list, view, create, update, delete, export, import |
| `dealdesk:trade-ledgers:item` | item | view, update, delete |

### `dealdesk_brand:*` (1)

| Resource | Type | Actions |
| --- | --- | --- |
| `dealdesk_brand:media-packages` | collection | list, view |

### `footprints:*` (7)

| Resource | Type | Actions |
| --- | --- | --- |
| `footprints:endpoints` | collection | list, view, create, update, delete, export, import |
| `footprints:endpoints:item` | item | view, update, delete |
| `footprints:pricing` | collection | list, view, create, update, delete, export, import |
| `footprints:products` | collection | list, view, create, update, delete, export, import |
| `footprints:products:item` | item | view, update, delete |
| `footprints:sites` | collection | list, view, create, update, delete, export, import |
| `footprints:sites:item` | item | view, update, delete |

### `qr:*` (8)

| Resource | Type | Actions |
| --- | --- | --- |
| `qr:campaigns` | collection | list, view, create, update, delete, export, import |
| `qr:campaigns:item` | item | view, update, delete |
| `qr:media` | collection | list, view, create, update, delete, export, import |
| `qr:media:item` | item | view, update, delete |
| `qr:site` | collection | list, view, create, update, delete, export, import |
| `qr:site:item` | item | view, update, delete |
| `qr:templates` | collection | list, view, create, update, delete, export, import |
| `qr:templates:item` | item | view, update, delete |

### `reports:*` (9)

| Resource | Type | Actions |
| --- | --- | --- |
| `reports:campaign_compliance` | collection | list, view, export |
| `reports:campaign_compliance_details` | collection | list, view, export |
| `reports:campaign_performance_maps` | collection | list, view, export |
| `reports:content_proof_of_play` | collection | list, view, export |
| `reports:export` | collection | list, export, delete |
| `reports:media_performance_maps` | collection | list, view, export |
| `reports:qr_performance` | collection | list, view, export |
| `reports:qr_performance_site_to_site` | collection | list, view, export |
| `reports:site_performance_maps` | collection | list, view, export |

### `settings:*` (33)

| Resource | Type | Actions |
| --- | --- | --- |
| `settings:admin_cerbos` | collection | list, view, create, update, delete, export, import |
| `settings:admin_cerbos:item` | item | view, update, delete |
| `settings:admin_general_agency:item` | item | view, update, delete |
| `settings:admin_general_ambient:item` | item | view, update, delete |
| `settings:admin_general_brand:item` | item | view, update, delete |
| `settings:admin_general_retailer:item` | item | view, update, delete |
| `settings:admin_teams` | collection | list, view, create, update, delete, export, import |
| `settings:admin_teams:item` | item | view, update, delete |
| `settings:admin_users` | collection | list, view, create, update, delete, export, import |
| `settings:admin_users:item` | item | view, update, delete |
| `settings:footprints_products_pricing_group` | collection | list, view, create, update, delete, export, import |
| `settings:footprints_products_pricing_group:item` | item | view, update, delete |
| `settings:footprints_products_property` | collection | list, view, create, update, delete, export, import |
| `settings:footprints_products_property:item` | item | view, update, delete |
| `settings:footprints_sites_property` | collection | list, view, create, update, delete, export, import |
| `settings:footprints_sites_property:item` | item | view, update, delete |
| `settings:qr_default_redirect` | collection | list, view, create, update, delete, export, import |
| `settings:qr_default_redirect:item` | item | view, update, delete |
| `settings:qr_design` | collection | list, view, create, update, delete, export, import |
| `settings:qr_design:item` | item | view, update, delete |
| `settings:qr_domain` | collection | list, view, create, update, delete, export, import |
| `settings:qr_domain:item` | item | view, update, delete |
| `settings:qr_power_tag` | collection | list, view, create, update, delete, export, import |
| `settings:qr_power_tag:item` | item | view, update, delete |
| `settings:signage_layout` | collection | list, view, create, update, delete, export, import |
| `settings:signage_layout:item` | item | view, update, delete |
| `settings:signage_people_property` | collection | list, view, create, update, delete, export, import |
| `settings:signage_people_property:item` | item | view, update, delete |
| `settings:signage_places_property` | collection | list, view, create, update, delete, export, import |
| `settings:signage_places_property:item` | item | view, update, delete |
| `settings:signage_things_property` | collection | list, view, create, update, delete, export, import |
| `settings:signage_things_property:item` | item | view, update, delete |
| `settings:user_profile:item` | item | view, update |

### `signages:*` (6)

| Resource | Type | Actions |
| --- | --- | --- |
| `signages:people` | collection | list, view, create, update, delete, export, import |
| `signages:people:item` | item | view, update, delete |
| `signages:places` | collection | list, view, create, update, delete, export, import |
| `signages:places:item` | item | view, update, delete |
| `signages:things` | collection | list, view, create, update, delete, export, import |
| `signages:things:item` | item | view, update, delete |

## 4. Product × Resource Matrix

For a resource with multiple product marks, refer to the source doc `docs/RESOURCES_ACTIONS_MATRIX.md` for whether the semantics are OR (`required`) or AND (`required-all`). Dealdesk rows use **per-surface OR semantics**: each resource is marked with the product(s) its surface gates on — a single product (e.g. `dealdesk:ssp` → `ssp`; `dealdesk:trade-ledgers` → `trade`; `dealdesk:brands` → `brand_center`), any of the three for shared surfaces (`dealdesk:campaigns`, `:inventory`, `:reports`, `:placement-rules`, `:placement-types`, `:rate-cards`), `ssp`+`trade` for `dealdesk:store-traffic`, or **no mark** for base resources (`dealdesk:sites`, `dealdesk:blueprints` — all retailers). The former all-three (AND) gate has been removed.

| Resource | brand_center | cms | compliance | connect | landing | ppt | priceTags | product | qr | signage | ssp | trade |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `cms:api_key` |  | ✓ |  |  |  |  |  |  |  |  |  |  |
| `cms:api_key:item` |  | ✓ |  |  |  |  |  |  |  |  |  |  |
| `cms:block` |  | ✓ |  |  |  |  |  |  |  |  |  |  |
| `cms:block:item` |  | ✓ |  |  |  |  |  |  |  |  |  |  |
| `cms:collection` |  | ✓ |  |  |  |  |  |  |  |  |  |  |
| `cms:collection:item` |  | ✓ |  |  |  |  |  |  |  |  |  |  |
| `cms:entry` |  | ✓ |  |  |  |  |  |  |  |  |  |  |
| `cms:entry:item` |  | ✓ |  |  |  |  |  |  |  |  |  |  |
| `cms:field` |  | ✓ |  |  |  |  |  |  |  |  |  |  |
| `cms:field:item` |  | ✓ |  |  |  |  |  |  |  |  |  |  |
| `cms:invitation` |  | ✓ |  |  |  |  |  |  |  |  |  |  |
| `cms:invitation:item` |  | ✓ |  |  |  |  |  |  |  |  |  |  |
| `cms:page` |  | ✓ |  |  |  |  |  |  |  |  |  |  |
| `cms:page:item` |  | ✓ |  |  |  |  |  |  |  |  |  |  |
| `cms:section` |  | ✓ |  |  |  |  |  |  |  |  |  |  |
| `cms:section:item` |  | ✓ |  |  |  |  |  |  |  |  |  |  |
| `cms:website` |  | ✓ |  |  |  |  |  |  |  |  |  |  |
| `cms:website:item` |  | ✓ |  |  |  |  |  |  |  |  |  |  |
| `connect:contacts` |  |  |  | ✓ |  |  |  |  |  |  |  |  |
| `connect:contacts:item` |  |  |  | ✓ |  |  |  |  |  |  |  |  |
| `contents:assets` |  |  |  |  |  |  |  |  |  | ✓ |  |  |
| `contents:assets:item` |  |  |  |  |  |  |  |  |  | ✓ |  |  |
| `contents:backgrounds` |  |  |  |  |  |  |  |  |  | ✓ |  |  |
| `contents:backgrounds:item` |  |  |  |  |  |  |  |  |  | ✓ |  |  |
| `contents:backgrounds_transition` |  |  |  |  |  |  |  |  |  | ✓ |  |  |
| `contents:backgrounds_transition:item` |  |  |  |  |  |  |  |  |  | ✓ |  |  |
| `contents:channels` |  |  |  |  |  |  |  |  |  | ✓ |  |  |
| `contents:channels:item` |  |  |  |  |  |  |  |  |  | ✓ |  |  |
| `contents:content_groups` |  |  |  |  |  |  |  |  |  | ✓ |  |  |
| `contents:content_groups:item` |  |  |  |  |  |  |  |  |  | ✓ |  |  |
| `contents:landing_pages` |  |  |  |  | ✓ |  |  |  |  |  |  |  |
| `contents:landing_pages:item` |  |  |  |  | ✓ |  |  |  |  |  |  |  |
| `contents:playlists` |  |  |  |  |  |  |  |  |  | ✓ |  |  |
| `contents:playlists:item` |  |  |  |  |  |  |  |  |  | ✓ |  |  |
| `contents:tags` |  |  | ✓ |  |  |  | ✓ | ✓ | ✓ | ✓ |  |  |
| `contents:tags:item` |  |  | ✓ |  |  |  | ✓ | ✓ | ✓ | ✓ |  |  |
| `contents:tags_assignments` |  |  | ✓ |  |  |  | ✓ | ✓ | ✓ | ✓ |  |  |
| `contents:tags_assignments:item` |  |  | ✓ |  |  |  | ✓ | ✓ | ✓ | ✓ |  |  |
| `contents:templates` |  |  |  |  |  |  | ✓ |  |  | ✓ |  |  |
| `contents:templates:item` |  |  |  |  |  |  | ✓ |  |  | ✓ |  |  |
| `dealdesk:blueprints` |  |  |  |  |  |  |  |  |  |  |  |  |
| `dealdesk:brand-users` | ✓ |  |  |  |  |  |  |  |  |  |  |  |
| `dealdesk:brand-users:item` | ✓ |  |  |  |  |  |  |  |  |  |  |  |
| `dealdesk:brands` | ✓ |  |  |  |  |  |  |  |  |  |  |  |
| `dealdesk:brands:item` | ✓ |  |  |  |  |  |  |  |  |  |  |  |
| `dealdesk:campaigns` | ✓ |  |  |  |  |  |  |  |  |  | ✓ | ✓ |
| `dealdesk:campaigns:item` | ✓ |  |  |  |  |  |  |  |  |  | ✓ | ✓ |
| `dealdesk:dsp-blocks` |  |  |  |  |  |  |  |  |  |  | ✓ |  |
| `dealdesk:dsp-blocks:item` |  |  |  |  |  |  |  |  |  |  | ✓ |  |
| `dealdesk:inventory` | ✓ |  |  |  |  |  |  |  |  |  | ✓ | ✓ |
| `dealdesk:line-items` |  |  |  |  |  |  |  |  |  |  |  | ✓ |
| `dealdesk:line-items:item` |  |  |  |  |  |  |  |  |  |  |  | ✓ |
| `dealdesk:media-packages` |  |  |  |  |  |  |  |  |  |  |  | ✓ |
| `dealdesk:media-packages:item` |  |  |  |  |  |  |  |  |  |  |  | ✓ |
| `dealdesk:photo-verifications` |  |  |  |  |  |  |  |  |  |  |  | ✓ |
| `dealdesk:photo-verifications:item` |  |  |  |  |  |  |  |  |  |  |  | ✓ |
| `dealdesk:placement-rules` | ✓ |  |  |  |  |  |  |  |  |  | ✓ | ✓ |
| `dealdesk:placement-rules:item` | ✓ |  |  |  |  |  |  |  |  |  | ✓ | ✓ |
| `dealdesk:placement-types` | ✓ |  |  |  |  |  |  |  |  |  | ✓ | ✓ |
| `dealdesk:placement-types:item` | ✓ |  |  |  |  |  |  |  |  |  | ✓ | ✓ |
| `dealdesk:rate-cards` | ✓ |  |  |  |  |  |  |  |  |  | ✓ | ✓ |
| `dealdesk:reports` | ✓ |  |  |  |  |  |  |  |  |  | ✓ | ✓ |
| `dealdesk:sites` |  |  |  |  |  |  |  |  |  |  |  |  |
| `dealdesk:ssp` |  |  |  |  |  |  |  |  |  |  | ✓ |  |
| `dealdesk:store-traffic` |  |  |  |  |  |  |  |  |  |  | ✓ | ✓ |
| `dealdesk:trade-ledgers` |  |  |  |  |  |  |  |  |  |  |  | ✓ |
| `dealdesk:trade-ledgers:item` |  |  |  |  |  |  |  |  |  |  |  | ✓ |
| `dealdesk_brand:media-packages` | ✓ |  |  |  |  |  |  |  |  |  |  |  |
| `footprints:endpoints` |  |  |  |  |  |  | ✓ |  |  | ✓ |  |  |
| `footprints:endpoints:item` |  |  |  |  |  |  | ✓ |  |  | ✓ |  |  |
| `footprints:pricing` |  |  |  |  |  |  | ✓ | ✓ |  | ✓ |  |  |
| `footprints:products` |  |  | ✓ |  |  |  | ✓ | ✓ |  | ✓ |  |  |
| `footprints:products:item` |  |  | ✓ |  |  |  | ✓ | ✓ |  | ✓ |  |  |
| `footprints:sites` |  |  | ✓ |  |  |  | ✓ | ✓ | ✓ | ✓ |  |  |
| `footprints:sites:item` |  |  | ✓ |  |  |  | ✓ | ✓ | ✓ | ✓ |  |  |
| `qr:campaigns` |  |  | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |  |  |
| `qr:campaigns:item` |  |  | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |  |  |
| `qr:media` |  |  |  |  |  |  |  |  | ✓ |  |  |  |
| `qr:media:item` |  |  |  |  |  |  |  |  | ✓ |  |  |  |
| `qr:site` |  |  |  |  |  |  |  |  | ✓ |  |  |  |
| `qr:site:item` |  |  |  |  |  |  |  |  | ✓ |  |  |  |
| `qr:templates` |  |  |  |  |  |  |  |  | ✓ |  |  |  |
| `qr:templates:item` |  |  |  |  |  |  |  |  | ✓ |  |  |  |
| `reports:campaign_compliance` |  |  | ✓ |  |  |  |  |  | ✓ | ✓ |  |  |
| `reports:campaign_compliance_details` |  |  | ✓ |  |  |  |  |  | ✓ | ✓ |  |  |
| `reports:campaign_performance_maps` |  |  | ✓ |  |  |  |  |  | ✓ | ✓ |  |  |
| `reports:content_proof_of_play` |  |  |  |  |  |  |  |  |  | ✓ |  |  |
| `reports:export` |  |  | ✓ | ✓ |  |  |  | ✓ | ✓ | ✓ |  |  |
| `reports:media_performance_maps` |  |  |  |  |  |  |  |  | ✓ |  |  |  |
| `reports:qr_performance` |  |  |  |  |  |  |  |  | ✓ |  |  |  |
| `reports:qr_performance_site_to_site` |  |  |  |  |  |  |  |  | ✓ |  |  |  |
| `reports:site_performance_maps` |  |  |  |  |  |  |  |  | ✓ |  |  |  |
| `settings:admin_cerbos` |  |  |  |  |  |  |  |  |  |  |  |  |
| `settings:admin_cerbos:item` |  |  |  |  |  |  |  |  |  |  |  |  |
| `settings:admin_general_agency:item` |  |  |  |  |  |  |  |  |  |  |  |  |
| `settings:admin_general_ambient:item` |  |  |  |  |  |  |  |  |  |  |  |  |
| `settings:admin_general_brand:item` |  |  |  |  |  |  |  |  |  |  |  |  |
| `settings:admin_general_retailer:item` |  |  |  |  |  |  |  |  |  |  |  |  |
| `settings:admin_teams` |  |  |  |  |  |  |  |  |  |  |  |  |
| `settings:admin_teams:item` |  |  |  |  |  |  |  |  |  |  |  |  |
| `settings:admin_users` |  |  |  |  |  |  |  |  |  |  |  |  |
| `settings:admin_users:item` |  |  |  |  |  |  |  |  |  |  |  |  |
| `settings:footprints_products_pricing_group` |  |  |  |  |  |  | ✓ | ✓ |  |  |  |  |
| `settings:footprints_products_pricing_group:item` |  |  |  |  |  |  | ✓ | ✓ |  |  |  |  |
| `settings:footprints_products_property` |  |  | ✓ |  |  |  | ✓ | ✓ |  |  |  |  |
| `settings:footprints_products_property:item` |  |  | ✓ |  |  |  | ✓ | ✓ |  |  |  |  |
| `settings:footprints_sites_property` |  |  | ✓ |  |  |  | ✓ |  | ✓ |  |  |  |
| `settings:footprints_sites_property:item` |  |  | ✓ |  |  |  | ✓ |  | ✓ |  |  |  |
| `settings:qr_default_redirect` |  |  |  |  |  |  |  |  | ✓ |  |  |  |
| `settings:qr_default_redirect:item` |  |  |  |  |  |  |  |  | ✓ |  |  |  |
| `settings:qr_design` |  |  |  |  |  |  |  |  | ✓ |  |  |  |
| `settings:qr_design:item` |  |  |  |  |  |  |  |  | ✓ |  |  |  |
| `settings:qr_domain` |  |  |  |  |  |  |  |  | ✓ |  |  |  |
| `settings:qr_domain:item` |  |  |  |  |  |  |  |  | ✓ |  |  |  |
| `settings:qr_power_tag` |  |  |  |  |  |  |  |  | ✓ |  |  |  |
| `settings:qr_power_tag:item` |  |  |  |  |  |  |  |  | ✓ |  |  |  |
| `settings:signage_layout` |  |  |  |  |  |  |  |  |  | ✓ |  |  |
| `settings:signage_layout:item` |  |  |  |  |  |  |  |  |  | ✓ |  |  |
| `settings:signage_people_property` |  |  |  |  |  | ✓ |  |  |  |  |  |  |
| `settings:signage_people_property:item` |  |  |  |  |  | ✓ |  |  |  |  |  |  |
| `settings:signage_places_property` |  |  |  |  |  | ✓ |  |  |  |  |  |  |
| `settings:signage_places_property:item` |  |  |  |  |  | ✓ |  |  |  |  |  |  |
| `settings:signage_things_property` |  |  |  |  |  | ✓ |  |  |  |  |  |  |
| `settings:signage_things_property:item` |  |  |  |  |  | ✓ |  |  |  |  |  |  |
| `settings:user_profile:item` |  |  |  |  |  |  |  |  |  |  |  |  |
| `signages:people` |  |  |  |  |  | ✓ |  |  |  | ✓ |  |  |
| `signages:people:item` |  |  |  |  |  | ✓ |  |  |  | ✓ |  |  |
| `signages:places` |  |  |  |  |  | ✓ |  |  |  | ✓ |  |  |
| `signages:places:item` |  |  |  |  |  | ✓ |  |  |  | ✓ |  |  |
| `signages:things` |  |  |  |  |  | ✓ |  |  |  | ✓ |  |  |
| `signages:things:item` |  |  |  |  |  | ✓ |  |  |  | ✓ |  |  |

## 5. Sync Status

- Policy files in `k8s/base/policies/`: **132**
- Policy files listed in `k8s/base/kustomization.yaml` configMapGenerator: **114**

> ⚠️ **18** policy file(s) exist in the repo but are NOT included in the kustomization allowlist. They will NEVER reach any cluster until added:
>    - `resource_cms_api_key.yaml`
>    - `resource_cms_api_key_item.yaml`
>    - `resource_cms_block.yaml`
>    - `resource_cms_block_item.yaml`
>    - `resource_cms_collection.yaml`
>    - `resource_cms_collection_item.yaml`
>    - `resource_cms_entry.yaml`
>    - `resource_cms_entry_item.yaml`
>    - `resource_cms_field.yaml`
>    - `resource_cms_field_item.yaml`
>    - `resource_cms_invitation.yaml`
>    - `resource_cms_invitation_item.yaml`
>    - `resource_cms_page.yaml`
>    - `resource_cms_page_item.yaml`
>    - `resource_cms_section.yaml`
>    - `resource_cms_section_item.yaml`
>    - `resource_cms_website.yaml`
>    - `resource_cms_website_item.yaml`

### staging

- Policies loaded in ConfigMap: **114**
- ✅ **In sync with repo** — staging ConfigMap matches the kustomization allowlist.

### production

- Policies loaded in ConfigMap: **114**
- ✅ **In sync with repo** — production ConfigMap matches the kustomization allowlist.

### staging ↔ production drift

- ✅ **staging and production are in sync** (114 policies each).

## 6. Special Cases & Notes

_No hand-maintained notes. Create `docs/cerbos_status_notes.md` to add persistent notes — its contents are appended verbatim to this section on each regeneration._
