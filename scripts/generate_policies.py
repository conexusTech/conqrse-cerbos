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
from dataclasses import dataclass
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
    category: str                # "product_resource", "product_settings", etc.

    def __post_init__(self):
        """Determine category based on properties."""
        if self.is_default:
            if "user_profile" in self.name:
                self.category = "user_settings"
            else:
                self.category = "admin_settings"
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
            Dict mapping resource names to (filename, products_list, is_default)
        """
        products = [
            "qr", "priceTags", "compliance", "product", "signage", "landing", "connect", "ppt"
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

            # Extract required products
            required_products = []
            if not is_default:
                # product values start at column 3 (after default)
                for i, product in enumerate(products):
                    col_index = 3 + i
                    if col_index < len(parts) and parts[col_index].strip().lower() == "required":
                        required_products.append(product)

            if resource_name and filename:
                resource_matrix[resource_name] = (filename, required_products, is_default)

        return resource_matrix

    def merge_data(self) -> List[ResourceDef]:
        """
        Merge resource actions and matrix data to create ResourceDefs.

        Returns:
            List of ResourceDef objects
        """
        resource_actions = self.parse_resource_actions()
        product_matrix = self.parse_product_matrix()

        resources = []

        for resource_name, (filename, products, is_default) in product_matrix.items():
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
                category="unknown"  # Will be set in __post_init__
            )
            resources.append(resource)

        return sorted(resources, key=lambda r: r.filename)


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
        elif resource.category == "product_settings":
            yaml += PolicyRenderer._render_product_settings(resource)
        elif resource.category == "admin_settings":
            yaml += PolicyRenderer._render_admin_settings(resource)
        elif resource.category == "user_settings":
            yaml += PolicyRenderer._render_user_settings(resource)
        else:
            raise ValueError(f"Unknown category: {resource.category}")

        return yaml

    @staticmethod
    def _render_product_resource(resource: ResourceDef) -> str:
        """Render product resource rules (product check + retailer scope)."""
        yaml = ""

        # Build the product condition
        if resource.products:
            products_str = ', '.join(f'"{p}"' for p in sorted(resource.products))
            product_condition = f'[{products_str}].exists(p, p in P.attr.products)'
        else:
            product_condition = 'true'

        # Determine operator actions based on type
        if resource.res_type == "item":
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
        yaml += "              - expr: 'P.attr.retailerId == R.attr.retailerId'\n"
        yaml += "      derivedRoles:\n"
        yaml += "        - retailer_owner\n"
        yaml += "        - retailer_manager\n"
        yaml += "        - team_lead\n"
        yaml += "        - staff_operator\n"

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
            yaml += "              - expr: 'P.attr.retailerId == R.attr.retailerId'\n"
            yaml += "      derivedRoles:\n"
            yaml += "        - guest_collaborator\n"

        return yaml

    @staticmethod
    def _render_product_settings(resource: ResourceDef) -> str:
        """Render product settings rules (settings owner/admin only, with product check)."""
        yaml = ""

        # Build the product condition
        products_str = ', '.join(f'"{p}"' for p in sorted(resource.products))
        product_condition = f'[{products_str}].exists(p, p in P.attr.products)'

        # Settings actions (all defined actions)
        actions = resource.actions

        yaml += "    # Settings access with product subscription check (owner/admin only)\n"
        yaml += "    - actions: [" + ", ".join(f'"{PolicyRenderer._action_prefix(a)}{a}"' for a in actions) + "]\n"
        yaml += "      effect: EFFECT_ALLOW\n"
        yaml += "      condition:\n"
        yaml += "        match:\n"
        yaml += "          all:\n"
        yaml += "            of:\n"
        yaml += f"              - expr: '{product_condition}'\n"
        yaml += "              - expr: 'P.attr.retailerId == R.attr.retailerId'\n"
        yaml += "      derivedRoles:\n"
        yaml += "        - retailer_owner\n"
        yaml += "        - retailer_manager\n"

        return yaml

    @staticmethod
    def _render_admin_settings(resource: ResourceDef) -> str:
        """Render admin settings rules (no condition, all owner/admin roles)."""
        yaml = ""

        # All defined actions
        actions = resource.actions

        yaml += "    # Admin settings access (all owner/admin at all levels)\n"
        yaml += "    - actions: [" + ", ".join(f'"{PolicyRenderer._action_prefix(a)}{a}"' for a in actions) + "]\n"
        yaml += "      effect: EFFECT_ALLOW\n"
        yaml += "      derivedRoles:\n"
        yaml += "        - root_user\n"
        yaml += "        - platform_administrator\n"
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
        """Get the action prefix (resource: or settings:)."""
        return "resource:"


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
