from __future__ import annotations

from collections import Counter
from pathlib import Path
from statistics import mean
from typing import Dict, List, Mapping, Sequence, Tuple

from .audit import HierarchyLeakageAudit
from .concept_escape import ConceptEscapeEngine
from .gluing import SemanticGluingEngine
from .invariants import InvariantMiner
from .mesh import SemanticMesh
from .models import DIKWPType, SemanticBundleResult
from .tensor import TransformationTensor
from .higher_order import MetaOperatorEvolutionEngine
from .contracts import SemanticContractCompiler


class MeshAnalyzer:
    def __init__(self, mesh: SemanticMesh) -> None:
        self.mesh = mesh

    def analyze(self) -> SemanticBundleResult:
        mined = InvariantMiner(self.mesh).mine(min_support=0.38)
        gluing = SemanticGluingEngine(self.mesh).analyze(support_threshold=0.38)
        escape = ConceptEscapeEngine(self.mesh).propose()
        alignments = self.mesh.alignment_edges(min_similarity=0.12)
        observer_similarity = self.mesh.observer_similarity()
        cycles = self.mesh.cycles()
        type_centrality = self.mesh.centrality_by_type()
        edge_type_pairs = []
        for event in self.mesh.transformations.values():
            edge_type_pairs.append((event.source_type.value, event.target_type.value))
        hierarchy_audit = HierarchyLeakageAudit().audit_mesh(edge_type_pairs, len(self.mesh.views), type_centrality)
        transformation_tensor = TransformationTensor(self.mesh).compile()
        meta_operators = MetaOperatorEvolutionEngine().propose(
            mined["conflicts"], mined["residuals"], escape, gluing
        )
        semantic_contracts = SemanticContractCompiler().compile(
            self.mesh.concept, mined["invariant_kernel"], mined["conflicts"], mined["residuals"], escape
        )

        if alignments:
            mean_alignment = mean(e.similarity for e in alignments)
            mean_compat = mean(e.compatibility for e in alignments)
        else:
            mean_alignment = 0.0
            mean_compat = 0.0

        observer_contrib = Counter(atom.observer for atom in self.mesh.atoms())
        total_atoms = sum(observer_contrib.values()) or 1
        dominance = max(observer_contrib.values(), default=0) / total_atoms
        transformation_coverage = sum(1 for v in self.mesh.transformation_usage().values() if v > 0) / 25.0
        cross_type_span = mean(
            sum(1 for v in atom.type_weights.values() if v >= 0.12) / 5.0 for atom in self.mesh.atoms()
        ) if self.mesh.atoms() else 0.0
        subjectivity_escape = max(
            0.0,
            min(
                1.0,
                0.26 * (1.0 - dominance)
                + 0.24 * mean_compat
                + 0.20 * (1.0 - gluing["obstruction_score"])
                + 0.16 * cross_type_span
                + 0.14 * min(1.0, len(mined["invariant_kernel"]) / 8.0),
            ),
        )
        concept_escape_readiness = min(
            1.0,
            0.45 * (len(mined["conflicts"]) / max(1, len(mined["invariant_kernel"]) + len(mined["conflicts"])))
            + 0.30 * (len(mined["residuals"]) / max(1, len(self.mesh.atoms())))
            + 0.25 * (sum(c["escape_need"] for c in escape) / max(1, len(escape))),
        )
        metrics = {
            "mean_cross_observer_alignment": round(mean_alignment, 6),
            "mean_cross_observer_compatibility": round(mean_compat, 6),
            "observer_dominance": round(dominance, 6),
            "subjectivity_escape_score": round(subjectivity_escape, 6),
            "concept_escape_readiness": round(concept_escape_readiness, 6),
            "transformation_type_coverage": round(transformation_coverage, 6),
            "cross_DIKWP_atom_span": round(cross_type_span, 6),
            "directed_cycle_count": float(len(cycles)),
            "gluing_obstruction_score": float(gluing["obstruction_score"]),
        }
        return SemanticBundleResult(
            concept=self.mesh.concept,
            observer_count=len(self.mesh.views),
            atom_count=len(self.mesh.atoms()),
            invariant_kernel=mined["invariant_kernel"],
            perspective_branches=mined["perspective_branches"],
            conflicts=mined["conflicts"],
            residuals=mined["residuals"],
            escape_candidates=escape,
            gluing=gluing,
            metrics=metrics,
            transformation_usage=self.mesh.transformation_usage(),
            hierarchy_audit=hierarchy_audit,
            transformation_tensor=transformation_tensor,
            meta_operator_proposals=meta_operators,
            semantic_contracts=semantic_contracts,
        )
