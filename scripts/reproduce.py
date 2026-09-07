"""Recompute MESH2 semantics and check its historical fixture and dashboard.

Dependencies must already be installed. This command makes no network requests.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
from importlib.metadata import PackageNotFoundError, version
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def compare_snapshot(expected: dict, actual: dict) -> list[str]:
    mismatches = []
    for field in ("concept", "observer_count", "atom_count", "transformation_usage"):
        if expected.get(field) != actual.get(field):
            mismatches.append(field)
    for field, value in expected["metrics"].items():
        current = actual.get("metrics", {}).get(field)
        if not isinstance(current, (int, float)) or abs(current - value) > 1e-6:
            mismatches.append(f"metrics.{field}")
    if expected["hierarchy_audit"]["verdict"] != actual.get("hierarchy_audit", {}).get("verdict"):
        mismatches.append("hierarchy_audit.verdict")
    for field in ("invariant_kernel", "conflicts"):
        left = sorted(item["semantic_feature"] for item in expected[field])
        right = sorted(item["semantic_feature"] for item in actual.get(field, []))
        if left != right:
            mismatches.append(field)
    return mismatches


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=ROOT / ".reproduction")
    args = parser.parse_args()
    out = args.out.resolve() / datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S.%fZ")
    out.mkdir(parents=True, exist_ok=False)
    env = {**os.environ, "PYTHONPATH": str(ROOT / "src"), "MPLBACKEND": "Agg", "MPLCONFIGDIR": str(out / "matplotlib"), "PYTHONDONTWRITEBYTECODE": "1", "PYTEST_DISABLE_PLUGIN_AUTOLOAD": "1"}
    receipt = {"project": "DIKWP-MESH-", "python": sys.version, "utc": datetime.now(timezone.utc).isoformat(), "steps": [], "status": "failed", "boundary": "Local semantic-fixture reproduction and artifact generation; not formal proof, observer-independent truth, or consciousness certification. PNG files are existence-checked, not byte-identical claims."}
    commands = [
        ["-m", "pytest", "-q", "-p", "no:cacheprovider"],
        ["-m", "dikwp_mesh2.cli", "analyze", "examples/life_semantic_bundle.json", "--out", str(out / "fresh")],
        ["-m", "dikwp_mesh2.cli", "audit", "examples/hierarchical_spec.json", "--out", str(out / "negative-audit.json")],
        ["-m", "dikwp_mesh2.cli", "route", "D", "W", "--top-k", "5"],
    ]
    try:
        receipt["dependencies"] = {name: version(name) for name in ("networkx", "scipy", "numpy", "pandas", "matplotlib", "jinja2", "pytest")}
        for index, command in enumerate(commands, 1):
            result = subprocess.run([sys.executable, *command], cwd=ROOT, env=env, text=True, encoding="utf-8", capture_output=True, timeout=180)
            (out / f"step-{index}.log").write_text(result.stdout + result.stderr, encoding="utf-8")
            receipt["steps"].append({"command": command, "returncode": result.returncode})
            if result.returncode:
                raise RuntimeError(f"Step {index} failed; inspect step-{index}.log")
        expected = json.loads((ROOT / "outputs" / "semantic_bundle_result.json").read_text(encoding="utf-8"))
        actual = json.loads((out / "fresh" / "semantic_bundle_result.json").read_text(encoding="utf-8"))
        mismatches = compare_snapshot(expected, actual)
        negative = json.loads((out / "negative-audit.json").read_text(encoding="utf-8"))
        if negative.get("verdict") != "REJECT_AS_HIERARCHICAL":
            mismatches.append("negative_hierarchy_fixture")
        for name in ("dashboard.html", "dikwp_network.png", "observer_similarity.png", "transformation_usage.png", "semantic_mesh.png"):
            path = out / "fresh" / name
            if not path.is_file() or path.stat().st_size == 0:
                mismatches.append(name)
        receipt["snapshot_comparison"] = {"mismatches": mismatches, "numeric_tolerance": 1e-6, "metrics": actual.get("metrics"), "observer_count": actual.get("observer_count"), "atom_count": actual.get("atom_count")}
        if mismatches:
            raise RuntimeError(f"Fresh result or required artifact mismatch: {mismatches}")
        receipt["status"] = "passed"
    except (OSError, ValueError, RuntimeError, PackageNotFoundError, subprocess.TimeoutExpired) as exc:
        receipt["error"] = str(exc)
    finally:
        receipt["source_sha256"] = {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest() for folder in ("src", "tests", "examples", "scripts") for path in sorted((ROOT / folder).rglob("*")) if path.is_file() and "__pycache__" not in path.parts}
        receipt["baseline_snapshot_sha256"] = hashlib.sha256((ROOT / "outputs" / "semantic_bundle_result.json").read_bytes()).hexdigest()
        receipt["configuration_sha256"] = {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in ("pyproject.toml", "requirements.txt", "requirements-reproduction.txt", "requirements.lock")}
        (out / "receipt.json").write_text(json.dumps(receipt, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(json.dumps({"status": receipt["status"], "receipt": str(out / "receipt.json")}, indent=2))
    return 0 if receipt["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
