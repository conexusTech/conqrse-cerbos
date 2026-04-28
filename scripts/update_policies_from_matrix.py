#!/usr/bin/env python3
"""
Update Cerbos policy YAML files based on the Product × Resource Matrix.

This script reads the Product × Resource Matrix from RESOURCES_ACTIONS_MATRIX.md
and updates the corresponding YAML files in k8s/base/policies with the correct
product requirements.
"""

import re
import os
import sys
import yaml
from pathlib import Path
from typing import Dict, List, Set, Tuple


class MatrixParser:
    """Parse the Product × Resource Matrix from markdown."""

    def __init__(self, markdown_path: str):
        self.markdown_path = markdown_path
        self.products = [
            "qr", "priceTags", "compliance", "product", "signage", "landing", "connect", "ppt"
        ]

    def parse(self) -> Dict[str, Set[str]]:
        """
        Parse the matrix and return a mapping of resource names to required products.

        Returns:
            Dict mapping resource names (e.g., "qr:campaigns") to set of required products.
        """
        with open(self.markdown_path, 'r') as f:
            content = f.read()

        # Find the "Product × Resource Matrix" section
        match = re.search(
            r'## Product × Resource Matrix\n\n\| Resource.*?\n(.*?)(?=\n---|\Z)',
            content,
            re.DOTALL
        )
        if not match:
            raise ValueError("Could not find Product × Resource Matrix in markdown")

        table_content = match.group(1)
        lines = table_content.strip().split('\n')

        # Skip the separator line after headers
        data_lines = [line for line in lines[1:] if line.strip()]

        resource_products: Dict[str, Set[str]] = {}

        for line in data_lines:
            parts = [p.strip() for p in line.split('|')]
            # Remove empty first and last elements from split
            parts = parts[1:-1] if len(parts) > 2 else parts

            if len(parts) < 2:
                continue

            resource = parts[0]
            values = parts[1:]

            # Need at least resource + 1 default column + 8 product columns = 10 total
            if len(parts) < 10:
                continue

            # Find which products are marked as "required"
            required = set()
            # Skip the first value (default column) and iterate through product columns
            for i, product in enumerate(self.products):
                # Product values start at index 1 (after default column)
                col_index = i + 1
                if col_index < len(values) and values[col_index].strip().lower() == "required":
                    required.add(product)

            # Special handling: if default column is "required", skip product check
            if values[0].strip().lower() == "required":
                required = set()

            # Only process if resource name is not empty
            if not resource or resource.startswith('-'):
                continue

            # Get base resource name (remove :list, :item, :assignments suffixes)
            # Note: :export is NOT removed as it's part of the resource identifier (reports:export)
            base_resource = re.sub(r':(list|item|assignments)$', '', resource)

            # Store the mapping
            resource_products[base_resource] = required

        return resource_products


class YAMLUpdater:
    """Update YAML policy files with product requirements."""

    # Special mappings for resources where the filename doesn't follow the standard pattern
    SPECIAL_MAPPINGS = {
        "reports:qr-performance": "resource_reports_qr_performance.yaml",
        "reports:qr-performance-site-to-site": "resource_reports_qr_performance_site_to_site.yaml",
        "settings:qr_power-tag": "resource_settings_qr_power_tag.yaml",
        "settings:qr_default-redirect": "resource_settings_qr_default_redirect.yaml",
        "settings:footprints_products_pricing_group": None,  # No corresponding file
        "reports:export": "resource_reports_export.yaml",
    }

    def __init__(self, policies_dir: str):
        self.policies_dir = Path(policies_dir)

    @staticmethod
    def resource_to_filename(resource: str) -> str:
        """
        Convert a resource name to its YAML filename.

        Examples:
            "qr:campaigns" -> "resource_qr_campaigns.yaml"
            "settings:admin:general" -> "resource_settings_admin_general.yaml"
            "contents:content-groups" -> "resource_contents_content_groups.yaml"
        """
        # Check special mappings first
        if resource in YAMLUpdater.SPECIAL_MAPPINGS:
            return YAMLUpdater.SPECIAL_MAPPINGS[resource]

        # Replace colons and hyphens with underscores
        normalized = resource.replace(':', '_').replace('-', '_')
        return f"resource_{normalized}.yaml"

    def find_yaml_file(self, resource: str) -> Path:
        """Find the YAML file for a given resource."""
        filename = self.resource_to_filename(resource)
        if filename is None:
            return None
        filepath = self.policies_dir / filename
        return filepath

    def update_file(self, resource: str, products: Set[str]) -> Tuple[bool, str]:
        """
        Update a YAML file with the correct product list.

        Returns:
            Tuple of (success: bool, message: str)
        """
        filepath = self.find_yaml_file(resource)

        if filepath is None:
            return False, f"No YAML file mapped for resource: {resource}"

        if not filepath.exists():
            return False, f"File not found: {filepath}"

        # Read the YAML file
        with open(filepath, 'r') as f:
            content = f.read()

        # Convert products set to sorted list for consistent output
        product_list = sorted(list(products))

        # Generate the product condition string
        if product_list:
            products_str = ', '.join(f'"{p}"' for p in product_list)
            product_condition = f'[{products_str}].exists(p, p in P.attr.products)'
        else:
            # If no products required, use a condition that always passes
            product_condition = 'true'

        # Update all product condition expressions in the file
        # Pattern: matches product check expressions in conditions
        pattern = r'\[.*?\]\.exists\(p, p in P\.attr\.products\)'

        # If no products, replace with "true"
        if not product_list:
            updated_content = re.sub(pattern, product_condition, content)
        else:
            updated_content = re.sub(pattern, product_condition, content)

        # Write back to file
        with open(filepath, 'w') as f:
            f.write(updated_content)

        return True, f"Updated {filepath.name} with products: {product_list if product_list else 'none (always allowed)'}"


def main():
    """Main entry point."""
    # Get paths relative to script location
    script_dir = Path(__file__).parent
    project_root = script_dir.parent

    matrix_file = project_root / "docs" / "RESOURCES_ACTIONS_MATRIX.md"
    policies_dir = project_root / "k8s" / "base" / "policies"

    if not matrix_file.exists():
        print(f"Error: Matrix file not found: {matrix_file}")
        sys.exit(1)

    if not policies_dir.exists():
        print(f"Error: Policies directory not found: {policies_dir}")
        sys.exit(1)

    # Parse the matrix
    print("Parsing Product × Resource Matrix...")
    parser = MatrixParser(str(matrix_file))
    resource_products = parser.parse()
    print(f"Found {len(resource_products)} resources in matrix\n")

    # Update YAML files
    print("Updating policy YAML files...")
    updater = YAMLUpdater(str(policies_dir))

    updated_count = 0
    skipped_count = 0
    errors = []

    for resource, products in sorted(resource_products.items()):
        success, message = updater.update_file(resource, products)
        print(f"  {message}")

        if success:
            updated_count += 1
        else:
            skipped_count += 1
            errors.append(message)

    # Print summary
    print(f"\n{'='*60}")
    print(f"Summary:")
    print(f"  Updated: {updated_count}")
    print(f"  Skipped: {skipped_count}")
    if errors:
        print(f"\nErrors:")
        for error in errors:
            print(f"  - {error}")

    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
