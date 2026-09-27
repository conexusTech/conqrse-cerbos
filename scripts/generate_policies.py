#!/usr/bin/env python3
"""
Generate Cerbos policy YAML files from the resource definition docs.

This script parses docs/RESOURCES_ACTIONS_MATRIX.md and generates all 73
policy files by reading resource definitions and the Product × Resource Matrix.
"""

import re
import sys
import argparse
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional
from collections import defaultdict


@dataclass
class ResourceDef:
    """A resource definition with metadata for policy generation."""
    name: str                    # "connect:contacts"
    filename: str                # "resource_connect_contacts.yaml"
    res_type: str                # "collection" | "item"
    actions: List[str]           # ["list", "view", "create", ...]
    products: List[str]          # ["connect"] or [] for default
    is_default: bool             # True if default=required
    is_all_required: bool = False  # True if any product marker was "required-all" (AND semantics)
    is_admin_only: bool = False  # True if any product marker was "required-admin" (owner/admin roles only)
    attr_guard: str = ""         # Guard name from the "Attribute-Guarded Resources" table, if any
    brand_excluded_actions: List[str] = field(default_factory=list)  # Actions withheld from the DealDesk brand path
    category: str = "unknown"    # "product_resource", "product_settings", "dealdesk_resource", etc.

    def __post_init__(self):
        """Determine category based on properties."""
        if self.is_default:
            if "user_profile" in self.name:
                self.category = "user_settings"
            else:
                self.category = "admin_settings"
        elif self.is_admin_only:
            # Owner/admin-tier product resource (e.g. dealdesk:inventory-provisioning,
            # contents:tags_taxonomy). Takes precedence over the dealdesk/product
            # namespace defaults so an admin-only resource in any namespace renders
            # the restricted role set (no collaborator, no brand path).
            self.category = "admin_product_resource"
        elif (
            self.name.startswith("dealdesk:")
            or self.name.startswith("dealdesk_brand:")
            or self.is_all_required
        ):
            self.category = "dealdesk_resource"
        elif self.name.startswith("settings:"):
            self.category = "product_settings"
        else:
            self.category = "product_resource"


class MatrixParser:
    """Parse the Product × Resource Matrix markdown file."""

    def __init__(self, matrix_path: str):
        self.matrix_path = Path(matrix_path)
        if not self.matrix_path.exists():
            raise FileNotFoundError(f"Matrix file not found: {matrix_path}")

        with open(matrix_path, 'r') as f:
            self.content = f.read()

    def parse_resource_actions(self) -> Dict[str, tuple]:
        """
        Parse resource tables to get {resource_name: (type, actions)}.

        Returns:
            Dict mapping resource names to (res_type, actions_list)
        """
        resources = {}

        # Parse all table rows
        # Matches: | `resource:name` | Collection | actions, actions, ... |
        #      or: | resource:name | Collection | actions, actions, ... |
        lines = self.content.split('\n')

        for line in lines:
            # Skip non-table lines
            if not line.strip().startswith('|') or '---' in line:
                continue

            # Skip header rows
            if 'Resource' in line and 'Type' in line and 'Actions' in line:
                continue

            # Split by |
            parts = [p.strip() for p in line.split('|')]
            # Remove empty first and last elements
            parts = parts[1:-1] if len(parts) > 2 else parts

            if len(parts) < 3:
                continue

            # Extract resource name (remove backticks if present)
            resource_name = parts[0].strip('` ').strip()

            # Extract type
            type_str = parts[1].strip().lower()
            if type_str not in ['collection', 'item']:
                continue

            res_type = type_str

            # Extract actions (everything after type)
            if len(parts) > 2:
                actions_str = parts[2].strip()
            else:
                continue

            # Skip header/separator rows (contains table header keywords)
            if resource_name.startswith('-') or not resource_name or resource_name == 'Resource':
                continue

            # Parse actions: split by comma, strip whitespace
            actions = [a.strip() for a in actions_str.split(',') if a.strip()]

            if resource_name and actions:
                resources[resource_name] = (res_type, actions)

        return resources

    def parse_product_matrix(self) -> Dict[str, tuple]:
        """
        Parse the Product × Resource Matrix.

        Returns:
            Dict mapping resource names to (filename, products_list, is_default, is_all_required)
        """
        products = [
            "qr", "priceTags", "compliance", "product", "signage", "landing", "connect", "ppt", "cms",
            "ssp", "trade", "brand_center"
        ]

        # Find the "Product × Resource Matrix" section
        # Look for the section header and parse lines after it
        lines = self.content.split('\n')
        start_idx = None

        for i, line in enumerate(lines):
            if '## Product × Resource Matrix' in line:
                start_idx = i
                break

        if start_idx is None:
            raise ValueError("Could not find Product × Resource Matrix in markdown")

        # Parse lines after the header
        resource_matrix: Dict[str, tuple] = {}
        in_matrix = False

        for i in range(start_idx, len(lines)):
            line = lines[i]

            # Skip empty lines and the section header
            if not line.strip() or i == start_idx:
                continue

            # Stop at end of file or next section
            if line.startswith('#') and i > start_idx:
                break

            # Skip separator lines and non-table lines
            if not line.startswith('|') or '---' in line:
                continue

            # Split by |
            parts = [p.strip() for p in line.split('|')]
            # Remove empty first and last elements
            parts = parts[1:-1] if len(parts) > 2 else parts

            if len(parts) < 3:
                continue

            resource_name = parts[0]
            filename = parts[1] if len(parts) > 1 else ""

            # Skip header rows
            if resource_name == 'Resource' or resource_name.startswith('-'):
                continue

            # Check if default column is "required"
            default_col = parts[2].strip().lower() if len(parts) > 2 else ""
            is_default = default_col == "required"

            # Extract required products; track required-all (AND) and required-admin (owner/admin only)
            required_products = []
            is_all_required = False
            is_admin_only = False
            if not is_default:
                # product values start at column 3 (after default)
                for i, product in enumerate(products):
                    col_index = 3 + i
                    if col_index >= len(parts):
                        continue
                    val = parts[col_index].strip().lower()
                    if val == "required":
                        required_products.append(product)
                    elif val == "required-all":
                        required_products.append(product)
                        is_all_required = True
                    elif val == "required-admin":
                        required_products.append(product)
                        is_admin_only = True

            if resource_name and filename:
                resource_matrix[resource_name] = (filename, required_products, is_default, is_all_required, is_admin_only)

        return resource_matrix

    def parse_attribute_guards(self) -> Dict[str, str]:
        """
        Parse the "Attribute-Guarded Resources" table into {resource_name: guard_name}.

        Rows look like: | `contents:tags_taxonomy` | `protected_taxonomy_key` |
        Absent section, or no matching rows, yields an empty mapping — the guard
        mechanism is strictly opt-in.
        """
        guards: Dict[str, str] = {}
        lines = self.content.split('\n')

        start_idx = None
        for i, line in enumerate(lines):
            if line.strip().startswith('## Attribute-Guarded Resources'):
                start_idx = i
                break
        if start_idx is None:
            return guards

        for line in lines[start_idx + 1:]:
            # Stop at the next section of equal or higher level
            if line.startswith('## '):
                break
            if not line.startswith('|') or '---' in line:
                continue

            parts = [p.strip().strip('`') for p in line.split('|')]
            parts = parts[1:-1] if len(parts) > 2 else parts
            if len(parts) < 2:
                continue

            resource_name, guard_name = parts[0], parts[1]
            # Skip the header row
            if resource_name.lower() == 'resource' or not guard_name:
                continue
            if guard_name not in ATTR_GUARDS:
                print(
                    f"Warning: unknown guard '{guard_name}' for {resource_name} — ignored",
                    file=sys.stderr,
                )
                continue
            guards[resource_name] = guard_name

        return guards

    def parse_brand_exclusions(self) -> Dict[str, List[str]]:
        """
        Parse "Brand-Path Action Exclusions" into {resource_name: [actions]}.

        Rows look like: | `dealdesk:ssp` | `update` | Waterfall config ... |
        Absent section yields an empty mapping — exclusions are strictly opt-in.
        """
        exclusions: Dict[str, List[str]] = {}
        lines = self.content.split('\n')

        start_idx = None
        for i, line in enumerate(lines):
            if line.strip().startswith('## Brand-Path Action Exclusions'):
                start_idx = i
                break
        if start_idx is None:
            return exclusions

        for line in lines[start_idx + 1:]:
            if line.startswith('## '):
                break
            if not line.startswith('|') or '---' in line:
                continue

            parts = [p.strip() for p in line.split('|')]
            parts = parts[1:-1] if len(parts) > 2 else parts
            if len(parts) < 2:
                continue

            resource_name = parts[0].strip('`')
            if resource_name.lower() == 'resource' or not resource_name:
                continue

            actions = [a.strip().strip('`') for a in parts[1].split(',') if a.strip()]
            actions = [a for a in actions if a]
            if actions:
                exclusions[resource_name] = actions

        return exclusions

    def merge_data(self) -> List[ResourceDef]:
        """
        Merge resource actions and matrix data to create ResourceDefs.

        Returns:
            List of ResourceDef objects
        """
        resource_actions = self.parse_resource_actions()
        product_matrix = self.parse_product_matrix()
        attribute_guards = self.parse_attribute_guards()
        brand_exclusions = self.parse_brand_exclusions()

        resources = []

        for resource_name, (filename, products, is_default, is_all_required, is_admin_only) in product_matrix.items():
            if resource_name not in resource_actions:
                print(f"Warning: No action definition found for {resource_name}", file=sys.stderr)
                continue

            res_type, actions = resource_actions[resource_name]

            resource = ResourceDef(
                name=resource_name,
                filename=filename,
                res_type=res_type,
                actions=actions,
                products=products,
                is_default=is_default,
                is_all_required=is_all_required,
                is_admin_only=is_admin_only,
                attr_guard=attribute_guards.get(resource_name, ""),
                brand_excluded_actions=brand_exclusions.get(resource_name, []),
            )
            resources.append(resource)

        return sorted(resources, key=lambda r: r.filename)


# Roles permitted to act on attribute-protected rows. Deliberately narrower than
# the full SU tier: platform_lead/member/collaborator are excluded, because a
# protected row is protected from self-service, not merely from retailers.
_SUPERUSER_ROLES = [
    "root_user",
    "platform_administrator",
]

# Attribute guards, keyed by the name used in the matrix's
# "Attribute-Guarded Resources" table. Each guard narrows a subset of a
# resource's actions to _SUPERUSER_ROLES for rows matching `protected_expr`,
# while leaving every other row on the resource's normal role tier.
#
# `protected_expr` must be has()-guarded so that routes which send no such
# attribute (every read) evaluate cleanly rather than erroring.
ATTR_GUARDS = {
    "protected_taxonomy_key": {
        "actions": ["create", "update", "delete"],
        "protected_expr": (
            '(has(R.attr.source) && R.attr.source == "dynamic") || '
            '(has(R.attr.origin) && R.attr.origin == "system")'
        ),
        "label": "dynamic or system taxonomy keys",
    },
    "team_resource_access": {
        "access_expr": (
            'P.attr.userLevel == "su" || P.attr.userLevel == "agency" || '
            'P.attr.userType == "owner" || P.attr.userType == "admin" || '
            '(has(R.attr.accessMode) && R.attr.accessMode == "all") || '
            '(!has(R.attr.accessMode) && '
            '(!has(R.attr.teamIds) || size(R.attr.teamIds) == 0)) || '
            '((!has(R.attr.accessMode) || R.attr.accessMode == "restricted") && '
            'has(R.attr.teamIds) && has(P.attr.teamIds) && '
            'R.attr.teamIds.exists(teamId, teamId in P.attr.teamIds))'
        ),
    },
    "team_tenant_scope": {
        "access_expr": (
            '!has(R.attr.retailerId) || P.attr.userLevel == "su" || '
            '(P.attr.userLevel == "agency" && P.attr.agencyId == R.attr.agencyId) || '
            '(P.attr.userLevel == "retailer" && P.attr.retailerId == R.attr.retailerId)'
        ),
    },
}


class PolicyRenderer:
    """Render Cerbos policy YAML for resources."""

    @staticmethod
    def render(resource: ResourceDef) -> str:
        """
        Render a complete Cerbos policy YAML for the resource.

        Args:
            resource: ResourceDef to render

        Returns:
            YAML string
        """
        yaml = "---\n"
        yaml += "apiVersion: \"api.cerbos.dev/v1\"\n"
        yaml += "resourcePolicy:\n"
        yaml += "  version: \"default\"\n"
        yaml += f"  resource: \"{resource.name}\"\n"
        yaml += "  importDerivedRoles:\n"
        yaml += "    - conqrse_roles\n"
        yaml += "  rules:\n"

        if resource.category == "product_resource":
            yaml += PolicyRenderer._render_product_resource(resource)
        elif resource.category == "admin_product_resource":
            yaml += PolicyRenderer._render_admin_product_resource(resource)
        elif resource.category == "dealdesk_resource":
            yaml += PolicyRenderer._render_dealdesk_resource(resource)
        elif resource.category == "product_settings":
            yaml += PolicyRenderer._render_product_settings(resource)
        elif resource.category == "admin_settings":
            yaml += PolicyRenderer._render_admin_settings(resource)
        elif resource.category == "user_settings":
            yaml += PolicyRenderer._render_user_settings(resource)
        else:
            raise ValueError(f"Unknown category: {resource.category}")

        return yaml

    # Role hierarchies (kept in declaration order to match hand-curated policies).
    _PRODUCT_OPERATOR_ROLES = [
        "root_user",
        "platform_administrator",
        "platform_lead",
        "platform_member",
        "agency_owner",
        "agency_manager",
        "agency_lead",
        "agency_member",
        "retailer_owner",
        "retailer_manager",
        "team_lead",
        "staff_operator",
    ]
    _PRODUCT_COLLABORATOR_ROLES = [
        "root_user",
        "platform_administrator",
        "platform_lead",
        "platform_member",
        "platform_collaborator",
        "agency_owner",
        "agency_manager",
        "agency_lead",
        "agency_member",
        "agency_collaborator",
        "guest_collaborator",
    ]
    # Everyone holding the product, regardless of tier — operators plus the
    # read-only collaborator tier. Used for reads on admin-gated resources, where
    # the write tier is deliberately narrow but the read must not be: key pickers,
    # assignment panels and the rule builder are used by team_lead / staff_operator,
    # who appear in neither _PRODUCT_SETTINGS_ROLES nor _PRODUCT_COLLABORATOR_ROLES.
    _PRODUCT_READER_ROLES = [
        "root_user",
        "platform_administrator",
        "platform_lead",
        "platform_member",
        "platform_collaborator",
        "agency_owner",
        "agency_manager",
        "agency_lead",
        "agency_member",
        "agency_collaborator",
        "retailer_owner",
        "retailer_manager",
        "team_lead",
        "staff_operator",
        "guest_collaborator",
    ]
    _PRODUCT_SETTINGS_ROLES = [
        "root_user",
        "platform_administrator",
        "platform_lead",
        "agency_owner",
        "agency_manager",
        "agency_lead",
        "retailer_owner",
        "retailer_manager",
    ]
    # DealDesk retailer path: SU + Agency + Retailer tiers gated by a
    # per-surface product check (single `in`, multi `.exists`, or none for base).
    _DEALDESK_RETAILER_ROLES = [
        "root_user",
        "platform_administrator",
        "platform_lead",
        "platform_member",
        "platform_collaborator",
        "agency_owner",
        "agency_manager",
        "agency_lead",
        "agency_member",
        "agency_collaborator",
        "retailer_owner",
        "retailer_manager",
        "team_lead",
        "staff_operator",
    ]
    # DealDesk brand path: Brand tier only, gated by brand_center product
    # and R.attr.retailerId in P.attr.retailerIds.
    _DEALDESK_BRAND_ROLES = [
        "brand_owner",
        "brand_manager",
        "brand_lead",
        "brand_member",
    ]

    @staticmethod
    def _render_product_resource(resource: ResourceDef) -> str:
        """Render product resource rules (product check + retailer scope on items)."""
        yaml = ""

        # Build the product condition
        if resource.products:
            products_str = ', '.join(f'"{p}"' for p in sorted(resource.products))
            product_condition = f'[{products_str}].exists(p, p in P.attr.products)'
        else:
            product_condition = 'true'

        is_item = resource.res_type == "item"
        guard = ATTR_GUARDS.get(resource.attr_guard) if resource.attr_guard else None
        access_expr = guard.get("access_expr") if guard else None
        scoped_tenant_expr = (
            'P.attr.userLevel == "su" || '
            '(P.attr.userLevel == "agency" && ('
            '(has(R.attr.agencyId) && P.attr.agencyId == R.attr.agencyId) || '
            '(has(R.attr.retailerId) && has(P.attr.retailerId) && '
            'P.attr.retailerId == R.attr.retailerId))) || '
            '(P.attr.userLevel == "retailer" && has(R.attr.retailerId) && '
            'P.attr.retailerId == R.attr.retailerId)'
        )
        # Collection checks may be intentionally unscoped while navigation is
        # being resolved. Item checks never may: the API guard must hydrate the
        # stored owner and the policy denies a missing tenant context.
        tenant_scope_expr = (
            scoped_tenant_expr
            if is_item
            else '(!has(R.attr.retailerId) && !has(R.attr.agencyId)) || '
            + scoped_tenant_expr
        )

        # Determine operator actions based on type
        if is_item:
            operator_actions = ["view", "update", "delete"]
            collaborator_actions = ["view"]
        else:
            operator_actions = resource.actions
            collaborator_actions = [a for a in resource.actions if a in ["list", "view", "export"]]

        # Operator rule
        yaml += "    # Retailer access with product subscription check\n"
        yaml += "    - actions: [" + ", ".join(f'"{PolicyRenderer._action_prefix(a)}{a}"' for a in operator_actions) + "]\n"
        yaml += "      effect: EFFECT_ALLOW\n"
        yaml += "      condition:\n"
        yaml += "        match:\n"
        yaml += "          all:\n"
        yaml += "            of:\n"
        yaml += f"              - expr: '{product_condition}'\n"
        yaml += f"              - expr: '{tenant_scope_expr}'\n"
        if access_expr:
            yaml += f"              - expr: '{access_expr}'\n"
        yaml += "      derivedRoles:\n"
        for role in PolicyRenderer._PRODUCT_OPERATOR_ROLES:
            yaml += f"        - {role}\n"

        # Collaborator rule (if different actions)
        if collaborator_actions and collaborator_actions != operator_actions:
            yaml += "\n    # Collaborators with product subscription check\n"
            yaml += "    - actions: [" + ", ".join(f'"{PolicyRenderer._action_prefix(a)}{a}"' for a in collaborator_actions) + "]\n"
            yaml += "      effect: EFFECT_ALLOW\n"
            yaml += "      condition:\n"
            yaml += "        match:\n"
            yaml += "          all:\n"
            yaml += "            of:\n"
            yaml += f"              - expr: '{product_condition}'\n"
            yaml += f"              - expr: '{tenant_scope_expr}'\n"
            if access_expr:
                yaml += f"              - expr: '{access_expr}'\n"
            yaml += "      derivedRoles:\n"
            for role in PolicyRenderer._PRODUCT_COLLABORATOR_ROLES:
                yaml += f"        - {role}\n"

        return yaml

    @staticmethod
    def _render_dealdesk_resource(resource: ResourceDef) -> str:
        """Render DealDesk resource rules — three rule blocks.

        1. Retailer operators: full actions, PER-SURFACE product check + retailerId== on items.
        2. Retailer collaborators (guest_collaborator only): read-only subset, same gates.
        3. Brand path: full actions, gated by brand_center + retailerId in retailerIds.

        Product gating is per-surface (OR / `.exists`), not all-three (`.all`):
          - 0 products  -> base: no product check at all (all retailers).
          - 1 product   -> `"<p>" in P.attr.products`.
          - 2+ products -> `[...].exists(p, p in P.attr.products)` (any one grants).
        Product order follows the matrix column order (ssp, trade, brand_center), not sorted.
        """
        yaml = ""

        # Per-surface retailer product check (None for base resources).
        if not resource.products:
            retailer_product_condition = None
            gate_desc = "base (all retailers, no product gate)"
        elif len(resource.products) == 1:
            p = resource.products[0]
            retailer_product_condition = f'"{p}" in P.attr.products'
            gate_desc = f"requires {p} product"
        else:
            products_str = ', '.join(f'"{p}"' for p in resource.products)
            retailer_product_condition = f'[{products_str}].exists(p, p in P.attr.products)'
            if set(resource.products) == {"ssp", "trade", "brand_center"}:
                gate_desc = "requires any of ssp/trade/brand_center"
            else:
                gate_desc = "requires " + " or ".join(resource.products)

        brand_product_condition = '["brand_center"].exists(p, p in P.attr.products)'

        is_item = resource.res_type == "item"

        # Determine actions per tier (mirrors _render_product_resource split)
        if is_item:
            operator_actions = ["view", "update", "delete"]
            collaborator_actions = ["view"]
        else:
            operator_actions = resource.actions
            collaborator_actions = [a for a in resource.actions if a in ["list", "view", "export"]]

        # Filter to declared actions only (some collections omit update/delete etc.)
        operator_actions = [a for a in operator_actions if a in resource.actions]

        def _emit_condition() -> str:
            """Emit the shared retailer-path condition block (product + item tenancy).

            Omitted entirely when there is no product check and no item tenancy
            (base collection resources), matching the hand-curated policies.
            """
            exprs = []
            if retailer_product_condition:
                exprs.append(retailer_product_condition)
            if is_item:
                exprs.append('P.attr.retailerId == R.attr.retailerId')
            if not exprs:
                return ""
            block = "      condition:\n"
            block += "        match:\n"
            block += "          all:\n"
            block += "            of:\n"
            for expr in exprs:
                block += f"              - expr: '{expr}'\n"
            return block

        # Rule 1 — Retailer operators (SU / Agency / Retailer full tier)
        yaml += f"    # DealDesk retailer path — {gate_desc}\n"
        yaml += "    - actions: [" + ", ".join(f'"{a}"' for a in operator_actions) + "]\n"
        yaml += "      effect: EFFECT_ALLOW\n"
        yaml += _emit_condition()
        yaml += "      derivedRoles:\n"
        for role in PolicyRenderer._DEALDESK_RETAILER_ROLES:
            yaml += f"        - {role}\n"

        # Rule 2 — Retailer collaborators (guest_collaborator, read-only subset)
        if collaborator_actions:
            collab_note = " (base, no product gate)" if retailer_product_condition is None else ""
            yaml += f"\n    # DealDesk retailer collaborator path — read-only{collab_note}\n"
            yaml += "    - actions: [" + ", ".join(f'"{a}"' for a in collaborator_actions) + "]\n"
            yaml += "      effect: EFFECT_ALLOW\n"
            yaml += _emit_condition()
            yaml += "      derivedRoles:\n"
            yaml += "        - guest_collaborator\n"

        # Rule 3 — Brand path (Brand tier only, cross-retailer via retailerIds[])
        # Some actions are deliberately withheld here while staying available to
        # the retailer path — see "Brand-Path Action Exclusions" in the matrix.
        brand_actions = [a for a in operator_actions if a not in resource.brand_excluded_actions]
        if brand_actions:
            excluded_note = ""
            if resource.brand_excluded_actions:
                withheld = ", ".join(resource.brand_excluded_actions)
                excluded_note = f"\n    # `{withheld}` withheld from the brand path — see the matrix for the reason."
            yaml += f"\n    # DealDesk brand path — brand_center product + cross-retailer scoping via P.attr.retailerIds{excluded_note}\n"
            yaml += "    - actions: [" + ", ".join(f'"{a}"' for a in brand_actions) + "]\n"
            yaml += "      effect: EFFECT_ALLOW\n"
            yaml += "      condition:\n"
            yaml += "        match:\n"
            yaml += "          all:\n"
            yaml += "            of:\n"
            yaml += f"              - expr: '{brand_product_condition}'\n"
            yaml += "              - expr: 'R.attr.retailerId in P.attr.retailerIds'\n"
            yaml += "      derivedRoles:\n"
            for role in PolicyRenderer._DEALDESK_BRAND_ROLES:
                yaml += f"        - {role}\n"

        return yaml

    @staticmethod
    def _render_admin_product_resource(resource: ResourceDef) -> str:
        """Render an owner/admin-only product resource (no collaborator, no brand path).

        Used for admin-gated surfaces outside the settings namespace — e.g.
        dealdesk:inventory-provisioning (SSP sync trigger) and
        contents:tags_taxonomy (taxonomy-key administration). Same shape as
        product_settings: per-surface product `.exists()` gate, retailerId check
        on items, restricted to the owner/admin role tier. Brand roles are
        intentionally excluded (PRD §6.4).
        """
        products_str = ', '.join(f'"{p}"' for p in sorted(resource.products))
        product_condition = f'[{products_str}].exists(p, p in P.attr.products)'

        is_item = resource.res_type == "item"
        actions = resource.actions

        def _rule(comment: str, acts, roles, extra_exprs=()) -> str:
            """Emit one ALLOW rule, or nothing when it would have no actions."""
            if not acts:
                return ""
            block = f"    # {comment}\n"
            block += "    - actions: [" + ", ".join(f'"{a}"' for a in acts) + "]\n"
            block += "      effect: EFFECT_ALLOW\n"
            block += "      condition:\n"
            block += "        match:\n"
            block += "          all:\n"
            block += "            of:\n"
            block += f"              - expr: '{product_condition}'\n"
            if is_item:
                block += "              - expr: 'P.attr.retailerId == R.attr.retailerId'\n"
            for expr in extra_exprs:
                block += f"              - expr: '{expr}'\n"
            block += "      derivedRoles:\n"
            for role in roles:
                block += f"        - {role}\n"
            return block

        # Reads open to everyone holding the product; writes stay owner/admin.
        # An admin-gated resource nobody may list is unusable — key pickers,
        # assignment panels and the rule builder all read a vocabulary they may
        # not edit. Resources whose actions are all writes (e.g.
        # dealdesk:inventory-provisioning) render exactly as before, because the
        # read split below leaves nothing on one side.
        read_actions = [a for a in actions if a in ["list", "view", "export"]]
        write_actions = [a for a in actions if a not in read_actions]

        guard = ATTR_GUARDS.get(resource.attr_guard) if resource.attr_guard else None
        guarded = [a for a in write_actions if guard and a in guard["actions"]]
        plain = [a for a in write_actions if a not in guarded]

        yaml = ""

        if read_actions:
            yaml += _rule(
                "Read access for any tier holding the product",
                read_actions,
                PolicyRenderer._PRODUCT_READER_ROLES,
            )
            if plain or guarded:
                yaml += "\n"

        yaml += _rule(
            "Admin-only access with product subscription check (owner/admin only)",
            plain,
            PolicyRenderer._PRODUCT_SETTINGS_ROLES,
        )

        if guarded:
            if plain:
                yaml += "\n"
            # Same tier as above, but only for rows the guard does not protect.
            yaml += _rule(
                f"Owner/admin tier — everything except {guard['label']}",
                guarded,
                PolicyRenderer._PRODUCT_SETTINGS_ROLES,
                (f"!({guard['protected_expr']})",),
            )
            # Protected rows: superuser only. No protection expression here, so
            # this rule also covers unprotected rows for these roles.
            yaml += "\n" + _rule(
                f"Superuser only — {guard['label']}",
                guarded,
                _SUPERUSER_ROLES,
            )

        return yaml

    @staticmethod
    def _render_product_settings(resource: ResourceDef) -> str:
        """Render product settings rules (owner/admin/lead tiers, retailer scope on items)."""
        yaml = ""

        # Build the product condition
        products_str = ', '.join(f'"{p}"' for p in sorted(resource.products))
        product_condition = f'[{products_str}].exists(p, p in P.attr.products)'

        is_item = resource.res_type == "item"

        # Settings actions (all defined actions)
        actions = resource.actions

        guard = ATTR_GUARDS.get(resource.attr_guard) if resource.attr_guard else None
        access_expr = guard.get("access_expr") if guard else None

        # Signage layouts are also the policy taxonomy for zones. Once a layout
        # or zone carries team access attributes, use the same operator/read-only
        # collaborator split as the other team-scoped signage resources. Other
        # product settings retain their established manager-only role tier.
        if access_expr:
            scoped_tenant_expr = (
                'P.attr.userLevel == "su" || '
                '(P.attr.userLevel == "agency" && ('
                '(has(R.attr.agencyId) && P.attr.agencyId == R.attr.agencyId) || '
                '(has(R.attr.retailerId) && has(P.attr.retailerId) && '
                'P.attr.retailerId == R.attr.retailerId))) || '
                '(P.attr.userLevel == "retailer" && has(R.attr.retailerId) && '
                'P.attr.retailerId == R.attr.retailerId)'
            )
            tenant_scope_expr = (
                scoped_tenant_expr
                if is_item
                else '(!has(R.attr.retailerId) && !has(R.attr.agencyId)) || '
                + scoped_tenant_expr
            )
            collaborator_actions = [
                action for action in actions if action in ["list", "view", "export"]
            ]

            def _team_rule(comment: str, rule_actions, roles) -> str:
                if not rule_actions:
                    return ""
                block = f"    # {comment}\n"
                block += "    - actions: [" + ", ".join(
                    f'"{PolicyRenderer._action_prefix(action)}{action}"'
                    for action in rule_actions
                ) + "]\n"
                block += "      effect: EFFECT_ALLOW\n"
                block += "      condition:\n"
                block += "        match:\n"
                block += "          all:\n"
                block += "            of:\n"
                block += f"              - expr: '{product_condition}'\n"
                block += f"              - expr: '{tenant_scope_expr}'\n"
                block += f"              - expr: '{access_expr}'\n"
                block += "      derivedRoles:\n"
                for role in roles:
                    block += f"        - {role}\n"
                return block

            yaml += _team_rule(
                "Team-scoped settings access with product subscription check",
                actions,
                PolicyRenderer._PRODUCT_OPERATOR_ROLES,
            )
            if collaborator_actions:
                yaml += "\n" + _team_rule(
                    "Team-scoped settings collaborator access (read-only)",
                    collaborator_actions,
                    PolicyRenderer._PRODUCT_COLLABORATOR_ROLES,
                )
            return yaml

        yaml += "    # Settings access with product subscription check (owner/admin only)\n"
        yaml += "    - actions: [" + ", ".join(f'"{PolicyRenderer._action_prefix(a)}{a}"' for a in actions) + "]\n"
        yaml += "      effect: EFFECT_ALLOW\n"
        yaml += "      condition:\n"
        yaml += "        match:\n"
        yaml += "          all:\n"
        yaml += "            of:\n"
        yaml += f"              - expr: '{product_condition}'\n"
        if is_item:
            yaml += "              - expr: 'P.attr.retailerId == R.attr.retailerId'\n"
        yaml += "      derivedRoles:\n"
        for role in PolicyRenderer._PRODUCT_SETTINGS_ROLES:
            yaml += f"        - {role}\n"

        return yaml

    @staticmethod
    def _render_admin_settings(resource: ResourceDef) -> str:
        """Render admin settings rules (no condition, all owner/admin roles)."""
        yaml = ""

        # All defined actions
        actions = resource.actions
        guard = ATTR_GUARDS.get(resource.attr_guard) if resource.attr_guard else None
        access_expr = guard.get("access_expr") if guard else None

        is_platform_only = resource.name in {
            "settings:admin_cerbos",
            "settings:admin_cerbos:item",
        }
        if is_platform_only:
            yaml += "    # Cerbos policy settings are restricted to platform administrators\n"
        else:
            yaml += "    # Admin settings access (all owner/admin at all levels)\n"
        yaml += "    - actions: [" + ", ".join(f'"{PolicyRenderer._action_prefix(a)}{a}"' for a in actions) + "]\n"
        yaml += "      effect: EFFECT_ALLOW\n"
        if access_expr:
            yaml += "      condition:\n"
            yaml += "        match:\n"
            yaml += f"          expr: '{access_expr}'\n"
        yaml += "      derivedRoles:\n"
        yaml += "        - root_user\n"
        yaml += "        - platform_administrator\n"
        if not is_platform_only:
            yaml += "        - agency_owner\n"
            yaml += "        - agency_manager\n"
            yaml += "        - retailer_owner\n"
            yaml += "        - retailer_manager\n"

        return yaml

    @staticmethod
    def _render_user_settings(resource: ResourceDef) -> str:
        """Render user profile settings (no condition, all 15 roles)."""
        yaml = ""

        # Only view and update for user profile
        actions = ["view", "update"]

        yaml += "    # User profile access (all users can view/update own profile)\n"
        yaml += "    - actions: [" + ", ".join(f'"{PolicyRenderer._action_prefix(a)}{a}"' for a in actions) + "]\n"
        yaml += "      effect: EFFECT_ALLOW\n"
        yaml += "      derivedRoles:\n"
        yaml += "        - root_user\n"
        yaml += "        - platform_administrator\n"
        yaml += "        - platform_lead\n"
        yaml += "        - platform_member\n"
        yaml += "        - platform_collaborator\n"
        yaml += "        - agency_owner\n"
        yaml += "        - agency_manager\n"
        yaml += "        - agency_lead\n"
        yaml += "        - agency_member\n"
        yaml += "        - agency_collaborator\n"
        yaml += "        - retailer_owner\n"
        yaml += "        - retailer_manager\n"
        yaml += "        - team_lead\n"
        yaml += "        - staff_operator\n"
        yaml += "        - guest_collaborator\n"

        return yaml

    @staticmethod
    def _action_prefix(action: str) -> str:
        """
        Return empty string; Cerbos has no requirement for action name prefixes.

        Actions are arbitrary strings that must match between policies and
        authorization requests. The matrix defines actions without prefixes
        (e.g., 'list', 'view', 'create'), and they are used as-is in policies.
        """
        return ""


class PolicyGenerator:
    """Generate and write policy files."""

    def __init__(self, output_dir: Path):
        self.output_dir = output_dir

    def generate_all(
        self,
        resources: List[ResourceDef],
        force: bool = False,
        dry_run: bool = False
    ) -> tuple:
        """
        Generate all policy files.

        Args:
            resources: List of ResourceDef objects
            force: Overwrite existing files
            dry_run: Don't write files, just report

        Returns:
            Tuple of (generated_count, skipped_count, errors)
        """
        generated_count = 0
        skipped_count = 0
        errors = []

        for resource in resources:
            filepath = self.output_dir / resource.filename

            # Check if file exists
            if filepath.exists() and not force:
                print(f"  SKIP {resource.filename} (already exists, use --force to overwrite)")
                skipped_count += 1
                continue

            # Render YAML
            try:
                yaml_content = PolicyRenderer.render(resource)
            except Exception as e:
                errors.append(f"Failed to render {resource.name}: {str(e)}")
                print(f"  ERROR {resource.filename}: {str(e)}")
                continue

            # Write file
            if not dry_run:
                try:
                    filepath.write_text(yaml_content)
                except Exception as e:
                    errors.append(f"Failed to write {filepath}: {str(e)}")
                    print(f"  ERROR Writing {resource.filename}: {str(e)}")
                    continue

            print(f"  {'PREVIEW' if dry_run else 'GENERATE'} {resource.filename} [{resource.category}]")
            generated_count += 1

        return generated_count, skipped_count, errors


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Generate Cerbos policy YAML files from resource matrix"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing policy files"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview files without writing"
    )
    parser.add_argument(
        "--resource",
        help="Generate only a specific resource"
    )

    args = parser.parse_args()

    # Resolve paths
    script_dir = Path(__file__).parent
    project_root = script_dir.parent

    matrix_file = project_root / "docs" / "RESOURCES_ACTIONS_MATRIX.md"
    policies_dir = project_root / "k8s" / "base" / "policies"

    # Validate files exist
    if not matrix_file.exists():
        print(f"Error: Matrix file not found: {matrix_file}", file=sys.stderr)
        return 1

    if not policies_dir.exists():
        print(f"Error: Policies directory not found: {policies_dir}", file=sys.stderr)
        return 1

    # Parse matrix
    print("Parsing Resource Matrix...")
    try:
        matrix_parser = MatrixParser(str(matrix_file))
        resources = matrix_parser.merge_data()
    except Exception as e:
        print(f"Error parsing matrix: {str(e)}", file=sys.stderr)
        return 1

    print(f"Found {len(resources)} resources\n")

    # Filter by specific resource if requested
    if args.resource:
        resources = [r for r in resources if r.name == args.resource]
        if not resources:
            print(f"Error: Resource '{args.resource}' not found", file=sys.stderr)
            return 1

    # Generate files
    print("Generating policy files...")
    generator = PolicyGenerator(policies_dir)
    generated, skipped, errors = generator.generate_all(resources, args.force, args.dry_run)

    # Summary
    print(f"\n{'='*60}")
    print(f"Summary:")
    print(f"  Generated: {generated}")
    print(f"  Skipped: {skipped}")

    if errors:
        print(f"\nErrors ({len(errors)}):")
        for error in errors:
            print(f"  - {error}")
        return 1

    print(f"\nAll {'previewed' if args.dry_run else 'generated'} successfully!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
