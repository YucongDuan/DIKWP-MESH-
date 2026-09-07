from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any, Dict

from .analysis import MeshAnalyzer
from .audit import HierarchyLeakageAudit
from .dashboard import render_dashboard
from .io import load_bundle, write_json
from .operators import TransformRegistry
from .router import TransformationRouter
from .visualize import plot_dikwp_network, plot_observer_similarity, plot_semantic_mesh, plot_transformation_usage


def command_analyze(args: argparse.Namespace) -> int:
    mesh = load_bundle(args.input)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    result = MeshAnalyzer(mesh).analyze()
    write_json(out / "semantic_bundle_result.json", result.to_dict())
    write_json(out / "operator_registry.json", TransformRegistry().as_matrix())
    write_json(out / "observer_similarity.json", mesh.observer_similarity())
    write_json(out / "alignment_edges.json", [e.to_dict() for e in mesh.alignment_edges(min_similarity=0.12)])
    write_json(out / "gluing_report.json", result.gluing)
    write_json(out / "concept_escape_candidates.json", result.escape_candidates)
    write_json(out / "hierarchy_audit.json", result.hierarchy_audit)
    write_json(out / "transformation_tensor.json", result.transformation_tensor)
    write_json(out / "meta_operator_proposals.json", result.meta_operator_proposals)
    write_json(out / "semantic_contracts.json", result.semantic_contracts)

    with (out / "transformation_usage.csv").open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(["source", "target", "type", "count"])
        for key, count in result.transformation_usage.items():
            src, dst = key.split("->")
            writer.writerow([src, dst, key, count])
    with (out / "invariant_kernel.csv").open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(["feature", "support", "confidence", "disagreement", "observers"])
        for item in result.invariant_kernel:
            writer.writerow([item["semantic_feature"], item["support"], item["mean_confidence"], item["disagreement"], "|".join(item["observers"])])

    plot_dikwp_network(out / "dikwp_network.png")
    plot_observer_similarity(mesh, out / "observer_similarity.png")
    plot_transformation_usage(result, out / "transformation_usage.png")
    plot_semantic_mesh(mesh, out / "semantic_mesh.png")
    render_dashboard(result, mesh, out / "dashboard.html")
    print(json.dumps({
        "concept": result.concept,
        "observer_count": result.observer_count,
        "atom_count": result.atom_count,
        "subjectivity_escape_score": result.metrics["subjectivity_escape_score"],
        "concept_escape_readiness": result.metrics["concept_escape_readiness"],
        "dashboard": str(out / "dashboard.html"),
    }, ensure_ascii=False, indent=2))
    return 0


def command_route(args: argparse.Namespace) -> int:
    router = TransformationRouter()
    result = router.top_paths(args.source, args.target, top_k=args.top_k, max_hops=args.max_hops)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


def command_audit(args: argparse.Namespace) -> int:
    spec = json.loads(Path(args.input).read_text(encoding="utf-8"))
    result = HierarchyLeakageAudit().audit_spec(spec)
    if args.out:
        write_json(args.out, result)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="dikwp-mesh2")
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("analyze", help="Analyze a multi-observer semantic bundle")
    p.add_argument("input")
    p.add_argument("--out", default="outputs")
    p.set_defaults(func=command_analyze)
    p = sub.add_parser("route", help="Find non-hierarchical DIKWP transformation paths")
    p.add_argument("source")
    p.add_argument("target")
    p.add_argument("--top-k", type=int, default=5)
    p.add_argument("--max-hops", type=int, default=4)
    p.set_defaults(func=command_route)
    p = sub.add_parser("audit", help="Audit a system specification for hierarchy leakage")
    p.add_argument("input")
    p.add_argument("--out")
    p.set_defaults(func=command_audit)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
