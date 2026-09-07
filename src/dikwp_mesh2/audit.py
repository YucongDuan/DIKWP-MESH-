from __future__ import annotations

from collections import Counter
from typing import Dict, Iterable, List, Mapping, Sequence

import networkx as nx

from .models import DIKWPType


class HierarchyLeakageAudit:
    """Detects when an implementation silently turns DIKWP into a pyramid/pipeline."""

    REQUIRED_TYPES = {t.value for t in DIKWPType.ordered()}

    def audit_spec(self, spec: Mapping[str, object]) -> Dict[str, object]:
        edges = [tuple(e) for e in spec.get("edges", [])]
        privileged = set(str(x).upper() for x in spec.get("privileged_types", []))
        controllers = set(str(x).upper() for x in spec.get("global_controllers", []))
        concept_sources = list(spec.get("concept_sources", []))
        graph = nx.DiGraph()
        graph.add_nodes_from(self.REQUIRED_TYPES)
        graph.add_edges_from(edges)

        findings: List[Dict[str, object]] = []
        canonical_chain = [("D", "I"), ("I", "K"), ("K", "W"), ("W", "P")]
        edge_set = set(edges)
        if edge_set and edge_set.issubset(set(canonical_chain)):
            findings.append({
                "code": "LINEAR_PIPELINE",
                "severity": "critical",
                "message": "Only the D→I→K→W→P chain is implemented; this is a hierarchy, not a DIKWP network.",
            })
        if graph.number_of_edges() and not list(nx.simple_cycles(graph)):
            findings.append({
                "code": "NO_FEEDBACK_CYCLES",
                "severity": "high",
                "message": "The graph has no directed cycle, so later semantic resources cannot revise earlier ones.",
            })
        missing_pairs = []
        for src in self.REQUIRED_TYPES:
            for dst in self.REQUIRED_TYPES:
                if (src, dst) not in edge_set:
                    missing_pairs.append(f"{src}->{dst}")
        if len(missing_pairs) >= 15:
            findings.append({
                "code": "POOR_TRANSFORMATION_COVERAGE",
                "severity": "high",
                "message": f"{len(missing_pairs)} of 25 DIKWP×DIKWP transformation classes are absent.",
                "examples": missing_pairs[:10],
            })
        if privileged:
            findings.append({
                "code": "PRIVILEGED_TYPE",
                "severity": "high",
                "message": f"The following DIKWP types are treated as ontologically superior: {sorted(privileged)}.",
            })
        if "P" in controllers:
            findings.append({
                "code": "PURPOSE_MONARCHY",
                "severity": "high",
                "message": "Purpose is a global controller. Full DIKWP networking requires purposes themselves to be inferred, contested, revised, and sometimes suspended.",
            })
        if len(concept_sources) <= 1:
            findings.append({
                "code": "SINGLE_OBSERVER_DEFINITION",
                "severity": "high",
                "message": "The concept is defined from one observer or authority, preventing intersubjective semantic construction.",
            })
        if not any(src == "P" and dst != "P" for src, dst in edges):
            findings.append({
                "code": "PURPOSE_CANNOT_GENERATE_OTHER_TYPES",
                "severity": "medium",
                "message": "Purpose cannot select observations, distinctions, knowledge, or value audits.",
            })
        incoming_to_p = {src for src, dst in edges if dst == "P" and src != "P"}
        if not incoming_to_p:
            findings.append({
                "code": "PURPOSE_CANNOT_BE_REVISED",
                "severity": "critical",
                "message": "No other DIKWP resource can revise Purpose, making P dogmatic rather than semantic.",
            })
        elif len(incoming_to_p) < 3:
            findings.append({
                "code": "PURPOSE_REVISION_BOTTLENECK",
                "severity": "high",
                "message": f"Purpose is revisable from only {sorted(incoming_to_p)}; networked DIKWP should permit multiple evidential, relational, model and value routes to contest purpose.",
            })

        severity_weight = {"critical": 1.0, "high": 0.7, "medium": 0.4, "low": 0.2}
        leakage = min(1.0, sum(severity_weight[f["severity"]] for f in findings) / 4.0)
        return {
            "hierarchy_leakage_score": round(leakage, 6),
            "finding_count": len(findings),
            "findings": findings,
            "transformation_coverage": round((25 - len(missing_pairs)) / 25, 6),
            "cycle_count": len(list(nx.simple_cycles(graph))),
            "verdict": "REJECT_AS_HIERARCHICAL" if leakage >= 0.65 else "REVIEW" if leakage >= 0.30 else "NETWORK_COMPATIBLE",
        }

    def audit_mesh(self, edges: Sequence[tuple[str, str]], observer_count: int, centrality: Mapping[str, float]) -> Dict[str, object]:
        spec = {
            "edges": edges,
            "privileged_types": [k for k, v in centrality.items() if v > 0.55],
            "global_controllers": [],
            "concept_sources": [f"observer_{i}" for i in range(observer_count)],
        }
        result = self.audit_spec(spec)
        result["type_centrality"] = dict(centrality)
        return result
