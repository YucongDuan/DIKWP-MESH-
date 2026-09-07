from pathlib import Path

from dikwp_mesh2.analysis import MeshAnalyzer
from dikwp_mesh2.audit import HierarchyLeakageAudit
from dikwp_mesh2.higher_order import compose_types
from dikwp_mesh2.io import load_bundle
from dikwp_mesh2.operators import TransformRegistry
from dikwp_mesh2.router import TransformationRouter
from dikwp_mesh2.tensor import TransformationTensor

ROOT = Path(__file__).resolve().parents[1]
BUNDLE = ROOT / "examples" / "life_semantic_bundle.json"


def test_registry_contains_all_25_operators():
    registry = TransformRegistry()
    assert len(registry.all()) == 25
    assert registry.get("P", "D").key == "P->D"
    assert registry.get("D", "P").key == "D->P"


def test_life_bundle_is_network_not_hierarchy():
    mesh = load_bundle(BUNDLE)
    result = MeshAnalyzer(mesh).analyze()
    assert result.transformation_usage["D->P"] >= 1
    assert result.transformation_usage["P->D"] >= 1
    assert result.transformation_usage["P->P"] >= 1
    assert result.metrics["transformation_type_coverage"] == 1.0
    assert result.hierarchy_audit["verdict"] == "NETWORK_COMPATIBLE"
    assert result.hierarchy_audit["hierarchy_leakage_score"] == 0.0


def test_bad_pyramid_spec_is_rejected():
    spec = {
        "edges": [["D", "I"], ["I", "K"], ["K", "W"], ["W", "P"]],
        "privileged_types": ["P"],
        "global_controllers": ["P"],
        "concept_sources": ["single_expert"],
    }
    result = HierarchyLeakageAudit().audit_spec(spec)
    codes = {x["code"] for x in result["findings"]}
    assert result["verdict"] == "REJECT_AS_HIERARCHICAL"
    assert "LINEAR_PIPELINE" in codes
    assert "PURPOSE_MONARCHY" in codes
    assert "PURPOSE_REVISION_BOTTLENECK" in codes


def test_composition_is_nontrivial_and_revisable():
    composite = compose_types(["P", "D", "K", "P", "W"])
    assert composite.path == ["P", "D", "K", "P", "W"]
    assert len(composite.primitive_operators) == 4
    assert 0 < composite.cumulative_loss < 1
    assert 0 < composite.reversibility < 1
    assert composite.generativity > 0.5


def test_router_returns_multiple_paths_not_single_chain():
    paths = TransformationRouter().top_paths("D", "W", top_k=6, max_hops=4)
    assert len(paths) >= 4
    assert any("P" in p["path"] for p in paths)
    assert any(p["path"] == ["D", "W"] for p in paths)


def test_gluing_preserves_obstructions_and_residuals():
    result = MeshAnalyzer(load_bundle(BUNDLE)).analyze()
    conflict_names = {x["semantic_feature"] for x in result.conflicts}
    assert "cellular_only" in conflict_names
    assert "observer_relative" in conflict_names
    assert result.gluing["obstruction_score"] > 0
    assert len(result.residuals) > 0
    assert len(result.meta_operator_proposals) >= 3


def test_concept_escape_and_task_contracts_are_generated():
    result = MeshAnalyzer(load_bundle(BUNDLE)).analyze()
    axes = {x["candidate_dimension_en"] for x in result.escape_candidates}
    assert "concept-projection-loss" in axes
    assert "rule-self-modification" in axes
    assert len(result.semantic_contracts) == 3
    assert all(x["prohibited_output"] for x in result.semantic_contracts)


def test_tensor_has_context_axes_and_higher_order_events():
    mesh = load_bundle(BUNDLE)
    tensor = TransformationTensor(mesh).compile()
    assert tensor["primitive_coverage"] == 1.0
    assert tensor["higher_order_event_count"] >= 2
    assert "observer" in tensor["axes"]
    assert "provenance" in tensor["axes"]
