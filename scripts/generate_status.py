#!/usr/bin/env python3
"""
Generate docs/CERBOS_STATUS.md — a single-source-of-truth status page for
Cerbos targeted at QA, PMs, and other non-coder consumers.

Reads:
    - docs/RESOURCES_ACTIONS_MATRIX.md via MatrixParser (products, resources)
    - docs/consumer_integrations.yaml (hand-maintained consumer coverage)
    - docs/cerbos_status_notes.md (optional; appended verbatim if present)
    - git HEAD for latest committed change
    - kubectl for live Cerbos deployment + cerbos-policies ConfigMap in
      each configured environment namespace (staging, production).

Usage:
    python3 scripts/generate_status.py
    python3 scripts/generate_status.py --skip-cluster   # dry-render without k8s
"""

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

# Reuse the matrix parser from the policy generator so we always agree on
# the enums and resource lists exposed to policies + the permission-types
# package.
sys.path.insert(0, str(Path(__file__).parent))
from generate_policies import MatrixParser  # noqa: E402


ENVIRONMENTS = ["staging", "production"]
POLICIES_DIR_NAME = "policies"


def run(cmd, check=False):
    """Run a shell command, capture stdout, return (rc, stdout, stderr)."""
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=30, check=False
        )
        if check and result.returncode != 0:
            raise RuntimeError(f"{' '.join(cmd)} failed: {result.stderr}")
        return result.returncode, result.stdout, result.stderr
    except FileNotFoundError:
        return 127, "", f"command not found: {cmd[0]}"
    except subprocess.TimeoutExpired:
        return 124, "", "timeout"


def git_head(repo_root):
    rc, sha, _ = run(["git", "-C", str(repo_root), "rev-parse", "HEAD"])
    if rc != 0:
        return {"sha": "unknown", "subject": "unknown", "author": "unknown", "date": "unknown"}
    rc, subject, _ = run(
        ["git", "-C", str(repo_root), "log", "-1", "--pretty=%s"]
    )
    rc, author, _ = run(
        ["git", "-C", str(repo_root), "log", "-1", "--pretty=%an"]
    )
    rc, date, _ = run(
        ["git", "-C", str(repo_root), "log", "-1", "--pretty=%ad", "--date=iso-strict"]
    )
    rc, ahead_str, _ = run(
        ["git", "-C", str(repo_root), "rev-list", "--count", "@{u}..HEAD"]
    )
    try:
        ahead = int(ahead_str.strip())
    except ValueError:
        ahead = None
    return {
        "sha": sha.strip()[:12],
        "subject": subject.strip(),
        "author": author.strip(),
        "date": date.strip(),
        "ahead": ahead,
    }


def kubectl_context():
    rc, ctx, _ = run(["kubectl", "config", "current-context"])
    return ctx.strip() if rc == 0 else "unknown"


def cluster_env_state(namespace):
    """Return dict with deployment readiness + ConfigMap policy file list."""
    state = {
        "namespace": namespace,
        "reachable": False,
        "deployment_ready": None,
        "deployment_replicas": None,
        "deployment_last_updated": None,
        "policy_files": [],
        "error": None,
    }

    rc, out, err = run(
        [
            "kubectl",
            "get",
            "deployment",
            "-n",
            namespace,
            "cerbos",
            "-o",
            "json",
        ]
    )
    if rc != 0:
        state["error"] = err.strip() or "unable to reach cluster / namespace"
        return state
    try:
        dep = json.loads(out)
        state["reachable"] = True
        state["deployment_ready"] = dep.get("status", {}).get("readyReplicas", 0) or 0
        state["deployment_replicas"] = dep.get("spec", {}).get("replicas", 0) or 0
        # last update = most recent condition transition time
        conds = dep.get("status", {}).get("conditions", [])
        times = [c.get("lastUpdateTime") for c in conds if c.get("lastUpdateTime")]
        state["deployment_last_updated"] = max(times) if times else None
    except json.JSONDecodeError as e:
        state["error"] = f"deployment json parse: {e}"
        return state

    rc, out, err = run(
        [
            "kubectl",
            "get",
            "configmap",
            "-n",
            namespace,
            "cerbos-policies",
            "-o",
            "json",
        ]
    )
    if rc != 0:
        state["error"] = (state["error"] or "") + f"; configmap: {err.strip()}"
        return state
    try:
        cm = json.loads(out)
        state["policy_files"] = sorted(cm.get("data", {}).keys())
    except json.JSONDecodeError as e:
        state["error"] = (state["error"] or "") + f"; configmap json parse: {e}"

    return state


def repo_policy_files(repo_root):
    d = repo_root / "k8s" / "base" / POLICIES_DIR_NAME
    return sorted(f.name for f in d.glob("*.yaml"))


def kustomization_policy_files(repo_root):
    """Files listed in the configMapGenerator allowlist — what actually
    ships to clusters via kubectl apply."""
    kust = repo_root / "k8s" / "base" / "kustomization.yaml"
    if not kust.exists():
        return []
    files = []
    in_generator = False
    for line in kust.read_text().splitlines():
        stripped = line.strip()
        if stripped.startswith("- name: cerbos-policies"):
            in_generator = True
            continue
        if in_generator:
            if stripped.startswith("- ") and "policies/" in stripped:
                files.append(stripped.split("policies/", 1)[1])
            elif stripped and not stripped.startswith("-") and not stripped.startswith("files:") and not stripped.startswith("options:") and not stripped.startswith("disableNameSuffixHash"):
                # left the block
                if stripped[0].isalpha():
                    in_generator = False
    return sorted(files)


def load_consumer_integrations(repo_root):
    path = repo_root / "docs" / "consumer_integrations.yaml"
    if not path.exists():
        return None
    try:
        import yaml  # PyYAML — present because it's a runtime dep of the seed script
    except ImportError:
        return {"__error__": "PyYAML not installed — run `pip install pyyaml`"}
    with open(path) as f:
        return yaml.safe_load(f)


def load_notes(repo_root):
    path = repo_root / "docs" / "cerbos_status_notes.md"
    if not path.exists():
        return None
    return path.read_text()


def render_header(head, cluster_states, kctx):
    lines = [
        "# Cerbos Status",
        "",
        "**Purpose:** Single source of truth for what Cerbos policies are implemented, deployed, and consumed. Refreshed on demand by running `python3 scripts/generate_status.py`.",
        "",
        "**Audience:** QA, PMs, operators — everyone who needs to see what's live vs what's in the repo without reading YAML.",
        "",
        "> **See drift below?** Follow the [HOW TO — Update seeded policies](../README.md#how-to--update-seeded-policies-new--modified--removed) workflow in the README to bring an environment back in sync. Any policy change also requires bumping [`@conqrse/permission-types`](../README.md#how-to--update-conqrsepermission-types).",
        "",
        f"- **Last regenerated:** {datetime.now(timezone.utc).isoformat(timespec='seconds')}",
        f"- **Repo HEAD:** `{head['sha']}` — {head['subject']}",
        f"- **HEAD author / date:** {head['author']} · {head['date']}",
    ]
    if head.get("ahead") is not None and head["ahead"] > 0:
        lines.append(f"- **Unpushed commits on HEAD branch:** {head['ahead']}")
    lines.append(f"- **kubectl context:** `{kctx}`")
    lines.append("")

    lines.append("| Environment | Cerbos ready | Deployment last updated | Policies in ConfigMap |")
    lines.append("| --- | --- | --- | --- |")
    for env, s in cluster_states.items():
        if not s["reachable"]:
            lines.append(f"| {env} | ❌ unreachable | — | — |")
            continue
        ready = f"{s['deployment_ready']}/{s['deployment_replicas']}"
        lines.append(
            f"| {env} | {'✅' if s['deployment_ready'] == s['deployment_replicas'] and s['deployment_ready'] else '⚠️'} {ready} | {s['deployment_last_updated'] or 'unknown'} | {len(s['policy_files'])} |"
        )
    lines.append("")
    return "\n".join(lines)


def render_consumer_coverage(consumers_yaml, resources):
    lines = ["## 1. Status by Consumer", ""]
    if not consumers_yaml or "__error__" in (consumers_yaml or {}):
        err = (consumers_yaml or {}).get("__error__", "consumer_integrations.yaml missing")
        lines.append(f"> ⚠️ {err}")
        lines.append("")
        return "\n".join(lines)

    total_resources = len(resources)
    consumers = consumers_yaml.get("consumers", {})

    lines.append(f"Total resources declared in the matrix: **{total_resources}**")
    lines.append("")
    lines.append("| Consumer | Integrated | Planned | Coverage |")
    lines.append("| --- | --- | --- | --- |")
    for name, meta in consumers.items():
        integrated = meta.get("integrated", []) or []
        planned = meta.get("planned", []) or []
        coverage = (
            f"{len(integrated)}/{total_resources} ({100 * len(integrated) // total_resources}%)"
            if total_resources
            else "—"
        )
        lines.append(f"| **{name}** | {len(integrated)} | {len(planned)} | {coverage} |")
    lines.append("")

    for name, meta in consumers.items():
        integrated = meta.get("integrated", []) or []
        planned = meta.get("planned", []) or []
        description = (meta.get("description") or "").strip()
        lines.append(f"### {name}")
        lines.append("")
        if description:
            lines.append(f"> {description}")
            lines.append("")
        if integrated:
            lines.append(f"**Integrated ({len(integrated)}):**")
            lines.append("")
            for r in sorted(integrated):
                lines.append(f"- `{r}`")
            lines.append("")
        else:
            lines.append("_No resources integrated yet._")
            lines.append("")
        if planned:
            lines.append(f"**Planned ({len(planned)}):**")
            lines.append("")
            for r in sorted(planned):
                lines.append(f"- `{r}`")
            lines.append("")

    return "\n".join(lines)


def render_vocabulary(resources):
    # Derive from the ResourceDef list
    products = set()
    for r in resources:
        for p in r.products:
            products.add(p)
    products = sorted(products)

    user_levels = ["su", "agency", "retailer", "brand"]
    user_types = ["owner", "admin", "lead", "member", "collaborator"]

    lines = [
        "## 2. Vocabulary",
        "",
        "### Products",
        "",
    ]
    for p in products:
        lines.append(f"- `{p}`")
    lines.append("")

    lines.append("### User Levels")
    lines.append("")
    for lv in user_levels:
        lines.append(f"- `{lv}`")
    lines.append("")

    lines.append("### User Types")
    lines.append("")
    for ut in user_types:
        lines.append(f"- `{ut}`")
    lines.append("")

    lines.append("### Derived Roles (userLevel + userType matrix)")
    lines.append("")
    roles = [
        ("SU", ["root_user", "platform_administrator", "platform_lead", "platform_member", "platform_collaborator"]),
        ("Agency", ["agency_owner", "agency_manager", "agency_lead", "agency_member", "agency_collaborator"]),
        ("Retailer", ["retailer_owner", "retailer_manager", "team_lead", "staff_operator", "guest_collaborator"]),
        ("Brand", ["brand_owner", "brand_manager", "brand_lead", "brand_member"]),
    ]
    lines.append("| Tier | Roles |")
    lines.append("| --- | --- |")
    for tier, r in roles:
        lines.append(f"| **{tier}** | {', '.join(f'`{x}`' for x in r)} |")
    lines.append("")
    return "\n".join(lines)


def render_resources(resources):
    lines = [
        "## 3. Resources",
        "",
        f"Total: **{len(resources)}** resources across all groupings.",
        "",
    ]
    grouped = {}
    for r in resources:
        prefix = r.name.split(":", 1)[0]
        grouped.setdefault(prefix, []).append(r)
    for prefix in sorted(grouped.keys()):
        items = grouped[prefix]
        lines.append(f"### `{prefix}:*` ({len(items)})")
        lines.append("")
        lines.append("| Resource | Type | Actions |")
        lines.append("| --- | --- | --- |")
        for r in sorted(items, key=lambda x: x.name):
            lines.append(f"| `{r.name}` | {r.res_type} | {', '.join(r.actions)} |")
        lines.append("")
    return "\n".join(lines)


def render_matrix(resources):
    products = set()
    for r in resources:
        for p in r.products:
            products.add(p)
    products = sorted(products)

    lines = [
        "## 4. Product × Resource Matrix",
        "",
        "For a resource with multiple product marks, refer to the source doc `docs/RESOURCES_ACTIONS_MATRIX.md` for whether the semantics are OR (`required`) or AND (`required-all`). Dealdesk rows use AND semantics across `ssp`, `trade`, `brand_center`.",
        "",
    ]
    # Header
    lines.append("| Resource | " + " | ".join(products) + " |")
    lines.append("| --- | " + " | ".join("---" for _ in products) + " |")
    for r in sorted(resources, key=lambda x: x.name):
        cells = []
        for p in products:
            cells.append("✓" if p in r.products else "")
        lines.append(f"| `{r.name}` | " + " | ".join(cells) + " |")
    lines.append("")
    return "\n".join(lines)


def render_sync(repo_root, cluster_states):
    lines = ["## 5. Sync Status", ""]

    repo_files = set(repo_policy_files(repo_root))
    kust_files = set(kustomization_policy_files(repo_root))

    lines.append(f"- Policy files in `k8s/base/policies/`: **{len(repo_files)}**")
    lines.append(f"- Policy files listed in `k8s/base/kustomization.yaml` configMapGenerator: **{len(kust_files)}**")

    missing_from_kust = repo_files - kust_files
    if missing_from_kust:
        lines.append("")
        lines.append(f"> ⚠️ **{len(missing_from_kust)}** policy file(s) exist in the repo but are NOT included in the kustomization allowlist. They will NEVER reach any cluster until added:")
        for f in sorted(missing_from_kust):
            lines.append(f">    - `{f}`")

    orphan_in_kust = kust_files - repo_files
    if orphan_in_kust:
        lines.append("")
        lines.append(f"> ⚠️ **{len(orphan_in_kust)}** entries in kustomization reference files that don't exist in the repo:")
        for f in sorted(orphan_in_kust):
            lines.append(f">    - `{f}`")

    lines.append("")

    for env, s in cluster_states.items():
        lines.append(f"### {env}")
        lines.append("")
        if not s["reachable"]:
            lines.append(f"> ❌ Unable to query — {s.get('error') or 'cluster unreachable'}")
            lines.append("")
            continue
        deployed = set(s["policy_files"])
        missing_on_env = kust_files - deployed
        extra_on_env = deployed - kust_files
        lines.append(f"- Policies loaded in ConfigMap: **{len(deployed)}**")
        if missing_on_env:
            lines.append(f"- ⚠️ Missing on {env} (in repo/kustomization but not deployed): **{len(missing_on_env)}**")
            for f in sorted(missing_on_env):
                lines.append(f"    - `{f}`")
        if extra_on_env:
            lines.append(f"- ⚠️ Present on {env} but not in current repo/kustomization: **{len(extra_on_env)}**")
            for f in sorted(extra_on_env):
                lines.append(f"    - `{f}`")
        if not missing_on_env and not extra_on_env:
            lines.append(f"- ✅ **In sync with repo** — {env} ConfigMap matches the kustomization allowlist.")
        lines.append("")

    # Env-to-env drift
    reachable = [(env, s) for env, s in cluster_states.items() if s["reachable"]]
    if len(reachable) == 2:
        (env_a, s_a), (env_b, s_b) = reachable
        set_a = set(s_a["policy_files"])
        set_b = set(s_b["policy_files"])
        only_a = set_a - set_b
        only_b = set_b - set_a
        lines.append(f"### {env_a} ↔ {env_b} drift")
        lines.append("")
        if not only_a and not only_b:
            lines.append(f"- ✅ **{env_a} and {env_b} are in sync** ({len(set_a)} policies each).")
        else:
            if only_a:
                lines.append(f"- Only on **{env_a}** ({len(only_a)}):")
                for f in sorted(only_a):
                    lines.append(f"    - `{f}`")
            if only_b:
                lines.append(f"- Only on **{env_b}** ({len(only_b)}):")
                for f in sorted(only_b):
                    lines.append(f"    - `{f}`")
        lines.append("")

    return "\n".join(lines)


def render_notes(notes):
    lines = ["## 6. Special Cases & Notes", ""]
    if notes:
        lines.append(notes.rstrip())
        lines.append("")
    else:
        lines.append("_No hand-maintained notes. Create `docs/cerbos_status_notes.md` to add persistent notes — its contents are appended verbatim to this section on each regeneration._")
        lines.append("")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Generate docs/CERBOS_STATUS.md")
    parser.add_argument("--skip-cluster", action="store_true", help="Skip kubectl queries — render repo-only view")
    parser.add_argument("--output", default=None, help="Override output path")
    args = parser.parse_args()

    script_dir = Path(__file__).resolve().parent
    repo_root = script_dir.parent
    matrix_file = repo_root / "docs" / "RESOURCES_ACTIONS_MATRIX.md"
    output = Path(args.output) if args.output else repo_root / "docs" / "CERBOS_STATUS.md"

    matrix = MatrixParser(str(matrix_file))
    resources = matrix.merge_data()

    head = git_head(repo_root)
    kctx = kubectl_context()

    cluster_states = {}
    if args.skip_cluster:
        for env in ENVIRONMENTS:
            cluster_states[env] = {
                "namespace": env,
                "reachable": False,
                "policy_files": [],
                "error": "skipped by --skip-cluster",
            }
    else:
        for env in ENVIRONMENTS:
            cluster_states[env] = cluster_env_state(env)

    consumers_yaml = load_consumer_integrations(repo_root)
    notes = load_notes(repo_root)

    sections = [
        render_header(head, cluster_states, kctx),
        render_consumer_coverage(consumers_yaml, resources),
        render_vocabulary(resources),
        render_resources(resources),
        render_matrix(resources),
        render_sync(repo_root, cluster_states),
        render_notes(notes),
    ]
    body = "\n".join(sections).rstrip() + "\n"
    output.write_text(body)
    print(f"Wrote {output} ({len(body.splitlines())} lines)")


if __name__ == "__main__":
    main()
