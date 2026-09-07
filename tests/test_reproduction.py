import copy
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("mesh2_reproduce", ROOT / "scripts" / "reproduce.py")
reproduce = importlib.util.module_from_spec(spec)
spec.loader.exec_module(reproduce)


def expected():
    return json.loads((ROOT / "outputs" / "semantic_bundle_result.json").read_text(encoding="utf-8"))


def test_matching_semantic_snapshot_passes():
    snapshot = expected()
    assert reproduce.compare_snapshot(snapshot, copy.deepcopy(snapshot)) == []


def test_dropped_conflict_is_detected():
    snapshot = expected()
    changed = copy.deepcopy(snapshot)
    changed["conflicts"].pop()
    assert "conflicts" in reproduce.compare_snapshot(snapshot, changed)


def test_declared_coverage_without_matching_value_fails():
    snapshot = expected()
    changed = copy.deepcopy(snapshot)
    changed["metrics"]["transformation_type_coverage"] = 0.5
    assert "metrics.transformation_type_coverage" in reproduce.compare_snapshot(snapshot, changed)
