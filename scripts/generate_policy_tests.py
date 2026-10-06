#!/usr/bin/env python3
"""Generate Cerbos native compile tests from tests/test-cases.json."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys

import yaml


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "tests" / "test-cases.json"
OUTPUT = ROOT / "k8s" / "base" / "policies" / "_tests" / "matrix_test.yaml"


def key(value: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_]+", "_", value).strip("_")


def build() -> dict:
    source = json.loads(SOURCE.read_text())
    document = {
        "name": "GeneratedResourceMatrixTests",
        "description": "Generated from tests/test-cases.json; do not edit by hand.",
        "resources": {},
        "principals": {},
        "tests": [],
    }

    for suite in source["testSuites"]:
        for case in suite["tests"]:
            case_key = key(case["id"])
            principal_key = f"{case_key}_principal"
            resource_key = f"{case_key}_resource"
            document["principals"][principal_key] = case["principal"]
            document["resources"][resource_key] = case["resource"]
            effect = (
                "EFFECT_ALLOW"
                if case["expectedResult"] == "ALLOW"
                else "EFFECT_DENY"
            )
            document["tests"].append(
                {
                    "name": f"{case['id']} - {case['name']}",
                    "input": {
                        "principals": [principal_key],
                        "resources": [resource_key],
                        "actions": case["actions"],
                    },
                    "expected": [
                        {
                            "principal": principal_key,
                            "resource": resource_key,
                            "actions": {
                                action: effect for action in case["actions"]
                            },
                        }
                    ],
                }
            )

    return document


def render() -> str:
    return "---\n" + yaml.safe_dump(build(), sort_keys=False, width=120)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    expected = render()
    if args.check:
        if not OUTPUT.exists() or OUTPUT.read_text() != expected:
            print(f"Generated policy tests are stale: {OUTPUT.relative_to(ROOT)}")
            return 1
        print("Generated policy tests are current")
        return 0
    OUTPUT.write_text(expected)
    print(f"Wrote {OUTPUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
