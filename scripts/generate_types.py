#!/usr/bin/env python3
"""
Generate TypeScript enums and types from the resource definition docs.

This script parses docs/RESOURCES_ACTIONS_MATRIX.md and generates TypeScript
enums for resources, actions, roles, and product types in packages/permission-types/.
"""

import re
import sys
import argparse
from pathlib import Path
from dataclasses import dataclass
from typing import Dict, List, Set, Optional


@dataclass
class ResourceDef:
    """A resource definition with metadata for type generation."""
    name: str                    # "connect:contacts"
    res_type: str                # "collection" | "item"
    actions: List[str]           # ["list", "view", "create", ...]
    products: List[str]          # ["connect"] or [] for default


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

            # Extract resource name
            resource_name = parts[0].strip('` ').strip()

            # Extract type
            type_str = parts[1].strip().lower()
            if type_str not in ['collection', 'item']:
                continue

            res_type = type_str

            # Extract actions
            if len(parts) > 2:
                actions_str = parts[2].strip()
            else:
                continue

            # Skip header/separator rows
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
            Dict mapping resource names to (products_list, is_default)
        """
        products = [
            "qr", "priceTags", "compliance", "product", "signage", "landing", "connect", "ppt"
        ]

        # Find the "Product × Resource Matrix" section
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

            if resource_name:
                resource_matrix[resource_name] = (required_products, is_default)

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

        for resource_name, (products, is_default) in product_matrix.items():
            if resource_name not in resource_actions:
                print(f"Warning: No action definition found for {resource_name}", file=sys.stderr)
                continue

            res_type, actions = resource_actions[resource_name]

            resource = ResourceDef(
                name=resource_name,
                res_type=res_type,
                actions=actions,
                products=products
            )
            resources.append(resource)

        return sorted(resources, key=lambda r: r.name)


class TypeScriptGenerator:
    """Generate TypeScript enum and type files."""

    def __init__(self, output_dir: Path):
        self.output_dir = output_dir

    def to_enum_key(self, value: str) -> str:
        """Convert a value string to SCREAMING_SNAKE_CASE enum key."""
        # Handle already snake_case or colon-separated strings
        # e.g., "settings:admin_users" -> "SETTINGS_ADMIN_USERS"
        # e.g., "root_user" -> "ROOT_USER"
        # e.g., "priceTags" -> "PRICE_TAGS"
        key = re.sub(r'[:-]', '_', value)  # Replace colons and hyphens with underscores
        key = re.sub(r'(?<=[a-z])(?=[A-Z])', '_', key)  # Insert underscore before capitals
        return key.upper()

    def generate_resource_enum(self, resources: List[ResourceDef]) -> str:
        """Generate the Resource enum."""
        lines = ["// Auto-generated enum from docs/RESOURCES_ACTIONS_MATRIX.md", "export enum Resource {"]

        for resource in resources:
            key = self.to_enum_key(resource.name)
            lines.append(f"  {key} = '{resource.name}',")

        lines.append("}")
        return "\n".join(lines) + "\n"

    def generate_action_enum(self) -> str:
        """Generate the Action enum."""
        actions = ["list", "view", "create", "update", "delete", "export", "import"]
        lines = ["// Auto-generated enum from docs/RESOURCES_ACTIONS_MATRIX.md", "export enum Action {"]

        for action in actions:
            key = self.to_enum_key(action)
            lines.append(f"  {key} = '{action}',")

        lines.append("}")
        return "\n".join(lines) + "\n"

    def generate_role_enum(self) -> str:
        """Generate the DerivedRole enum with all 15 roles."""
        roles = [
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
        lines = ["// Auto-generated enum from docs/RESOURCES_ACTIONS_MATRIX.md", "export enum DerivedRole {"]

        for role in roles:
            key = self.to_enum_key(role)
            lines.append(f"  {key} = '{role}',")

        lines.append("}")
        return "\n".join(lines) + "\n"

    def generate_user_level_enum(self) -> str:
        """Generate the UserLevel enum."""
        levels = ["su", "agency", "retailer"]
        lines = ["// Auto-generated enum from docs/RESOURCES_ACTIONS_MATRIX.md", "export enum UserLevel {"]

        for level in levels:
            key = self.to_enum_key(level)
            lines.append(f"  {key} = '{level}',")

        lines.append("}")
        return "\n".join(lines) + "\n"

    def generate_user_type_enum(self) -> str:
        """Generate the UserType enum."""
        types = ["owner", "admin", "lead", "member", "collaborator"]
        lines = ["// Auto-generated enum from docs/RESOURCES_ACTIONS_MATRIX.md", "export enum UserType {"]

        for user_type in types:
            key = self.to_enum_key(user_type)
            lines.append(f"  {key} = '{user_type}',")

        lines.append("}")
        return "\n".join(lines) + "\n"

    def generate_product_enum(self) -> str:
        """Generate the Product enum."""
        products = ["qr", "priceTags", "compliance", "product", "signage", "landing", "connect", "ppt"]
        lines = ["// Auto-generated enum from docs/RESOURCES_ACTIONS_MATRIX.md", "export enum Product {"]

        for product in products:
            key = self.to_enum_key(product)
            lines.append(f"  {key} = '{product}',")

        lines.append("}")
        return "\n".join(lines) + "\n"

    def generate_resource_action_type(self, resources: List[ResourceDef]) -> str:
        """Generate the resource-action type file with ResourceMeta mapping."""
        lines = [
            "// Auto-generated type from docs/RESOURCES_ACTIONS_MATRIX.md",
            "import { Resource } from '../enums/resource.enum';",
            "import { Action } from '../enums/action.enum';",
            "",
            "export type ResourceType = 'collection' | 'item';",
            "",
            "export type ResourceMeta = {",
            "  type: ResourceType;",
            "  actions: Action[];",
            "};",
            "",
            "export const RESOURCE_META: Record<Resource, ResourceMeta> = {",
        ]

        for resource in resources:
            key = self.to_enum_key(resource.name)
            actions_list = ", ".join([f"Action.{self.to_enum_key(a)}" for a in resource.actions])
            lines.append(f"  Resource.{key}: {{ type: '{resource.res_type}', actions: [{actions_list}] }},")

        lines.append("};")
        return "\n".join(lines) + "\n"

    def generate_all(
        self,
        resources: List[ResourceDef],
        force: bool = False,
        dry_run: bool = False
    ) -> tuple:
        """
        Generate all TypeScript files.

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

        # Define all files to generate
        files = [
            ("enums/resource.enum.ts", self.generate_resource_enum(resources)),
            ("enums/action.enum.ts", self.generate_action_enum()),
            ("enums/role.enum.ts", self.generate_role_enum()),
            ("enums/user-level.enum.ts", self.generate_user_level_enum()),
            ("enums/user-type.enum.ts", self.generate_user_type_enum()),
            ("enums/product.enum.ts", self.generate_product_enum()),
            ("types/resource-action.type.ts", self.generate_resource_action_type(resources)),
        ]

        for filename, content in files:
            filepath = self.output_dir / filename

            # Check if file exists
            if filepath.exists() and not force:
                print(f"  SKIP {filename} (already exists, use --force to overwrite)")
                skipped_count += 1
                continue

            # Write file
            if not dry_run:
                try:
                    filepath.parent.mkdir(parents=True, exist_ok=True)
                    filepath.write_text(content)
                except Exception as e:
                    errors.append(f"Failed to write {filepath}: {str(e)}")
                    print(f"  ERROR Writing {filename}: {str(e)}")
                    continue

            print(f"  {'PREVIEW' if dry_run else 'GENERATE'} {filename}")
            generated_count += 1

        return generated_count, skipped_count, errors


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Generate TypeScript enums and types from resource matrix"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing enum files"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview files without writing"
    )

    args = parser.parse_args()

    # Resolve paths
    script_dir = Path(__file__).parent
    project_root = script_dir.parent

    matrix_file = project_root / "docs" / "RESOURCES_ACTIONS_MATRIX.md"
    types_dir = project_root / "packages" / "permission-types"

    # Validate files exist
    if not matrix_file.exists():
        print(f"Error: Matrix file not found: {matrix_file}", file=sys.stderr)
        return 1

    if not types_dir.exists():
        print(f"Error: Types directory not found: {types_dir}", file=sys.stderr)
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

    # Generate files
    print("Generating TypeScript enums and types...")
    generator = TypeScriptGenerator(types_dir)
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
