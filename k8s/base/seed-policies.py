#!/usr/bin/env python3
import os
import json
import time
import yaml
import glob
import base64
import urllib.request
import urllib.error
from pathlib import Path

CERBOS_URL = os.getenv('CERBOS_BASE_URL', 'http://localhost:3592')
USERNAME = os.getenv('CERBOS_ADMIN_USERNAME', 'cerbos')
PASSWORD = os.getenv('CERBOS_ADMIN_PASSWORD', 'conqrseCerbos')
POLICIES_DIR = '/policies-seed'
MAX_RETRIES = 30
RETRY_DELAY = 1

def make_auth_header():
    credentials = f"{USERNAME}:{PASSWORD}"
    encoded = base64.b64encode(credentials.encode()).decode()
    return f"Basic {encoded}"

def wait_for_cerbos():
    """Wait for Cerbos to be ready"""
    for i in range(MAX_RETRIES):
        try:
            req = urllib.request.Request(
                f"{CERBOS_URL}/_cerbos/health",
                headers={'Authorization': make_auth_header()}
            )
            with urllib.request.urlopen(req, timeout=5) as response:
                if response.status == 200:
                    print("✓ Cerbos is ready")
                    return
        except (urllib.error.URLError, urllib.error.HTTPError):
            if i < MAX_RETRIES - 1:
                print(f"Waiting for Cerbos... ({i + 1}/{MAX_RETRIES})")
                time.sleep(RETRY_DELAY)
    raise RuntimeError("Cerbos did not become ready in time")

def seed_policy(file_path):
    """Read policy file and POST to Cerbos Admin API"""
    try:
        with open(file_path, 'r') as f:
            policy = yaml.safe_load(f)

        if not policy:
            print(f"⚠ Empty policy file: {os.path.basename(file_path)}")
            return

        body = json.dumps({"policies": [policy]}).encode()
        req = urllib.request.Request(
            f"{CERBOS_URL}/admin/policy",
            data=body,
            headers={
                'Authorization': make_auth_header(),
                'Content-Type': 'application/json',
            },
            method='POST'
        )

        with urllib.request.urlopen(req, timeout=30) as response:
            if response.status in (200, 201):
                print(f"✓ Seeded: {os.path.basename(file_path)}")
                return

        raise RuntimeError(f"HTTP {response.status}")
    except Exception as error:
        print(f"✗ Failed to seed {os.path.basename(file_path)}: {error}")
        raise

def main():
    print("Cerbos Policy Seeding Script")
    print("=============================\n")

    if not os.path.exists(POLICIES_DIR):
        print(f"ℹ No policies directory found ({POLICIES_DIR}). Skipping seeding.")
        return

    print("Waiting for Cerbos to be ready...")
    wait_for_cerbos()

    policy_files = sorted([
        f for f in glob.glob(os.path.join(POLICIES_DIR, '*.yaml')) +
               glob.glob(os.path.join(POLICIES_DIR, '*.yml'))
    ])

    if not policy_files:
        print("No policy files found. Skipping seeding.")
        return

    print(f"\nSeeding {len(policy_files)} policy file(s)...\n")

    for file_path in policy_files:
        seed_policy(file_path)

    print("\n✓ Policy seeding completed successfully")

if __name__ == '__main__':
    try:
        main()
    except Exception as error:
        print(f"\n✗ Policy seeding failed: {error}")
        exit(1)
