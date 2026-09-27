---
type: Capability
title: Team-based resource access enforcement
description: Cerbos and API3 enforce retailer and trusted team membership for protected playlists, channels, zones, sites, and endpoints; user department metadata is ignored.
owners: [jody@conexus-tech.com]
tags: [authorization, teams, playlists, channels, zones, sites, endpoints]
---

#### Scenario: A restricted resource is available only to an assigned team member
- GIVEN a playlist, channel, zone, site, or endpoint assigned to one or more teams
- WHEN an ordinary retailer user accesses it
- THEN access is allowed only when the user's trusted team memberships intersect the assignments
- AND removing the membership removes access

**Checked by:** restricted-resource-team-membership

#### Scenario: An all-access resource remains available to retailer members
- GIVEN a playlist, channel, zone, site, or endpoint configured for all retailer users
- WHEN an ordinary user from its retailer accesses it
- THEN the team rule allows access

**Checked by:** all-resource-access

#### Scenario: Team authorization cannot cross tenant boundaries
- GIVEN a resource or team owned by another retailer
- WHEN a retailer user attempts to access or change it
- THEN the request is denied before the resource operation runs

**Checked by:** team-enforcement-tenant-boundary

#### Scenario: Authorized managers retain complete retailer access
- GIVEN a restricted resource in the manager's permitted tenant
- WHEN a super-user, agency user, retailer owner, or retailer administrator accesses it
- THEN the team membership restriction does not hide the resource

**Checked by:** department-manager-access

#### Scenario: Department metadata cannot grant access
- GIVEN a principal whose `department` value matches a restricted resource's assigned team name or identifier
- WHEN the principal has no matching trusted `teamIds` membership
- THEN access is denied
- AND only changing trusted team membership can change that decision

**Checked by:** department-metadata-ignored
