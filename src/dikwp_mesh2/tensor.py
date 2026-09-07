from __future__ import annotations

from collections import Counter, defaultdict
from math import log2
from typing import Dict, List, Mapping, Tuple

from .mesh import SemanticMesh
from .models import DIKWPType


class TransformationTensor:
    """Context-indexed view of DIKWP×DIKWP activity.

    The primitive 5×5 matrix is only the first two axes. Real transformations are
    indexed by observer, context, time, modality, scale and provenance. This class
    makes that higher-dimensional structure explicit without pretending it is a
    fixed universal tensor of truth.
    """

    def __init__(self, mesh: SemanticMesh) -> None:
        self.mesh = mesh

    @staticmethod
    def _entropy(counter: Mapping[str, int]) -> float:
        total = sum(counter.values())
        if total <= 0:
            return 0.0
        return -sum((v / total) * log2(v / total) for v in counter.values() if v)

    def compile(self) -> Dict[str, object]:
        entries: List[Dict[str, object]] = []
        pair_counts: Counter[str] = Counter()
        observer_counts: Counter[str] = Counter()
        context_counts: Counter[str] = Counter()
        scale_counts: Counter[str] = Counter()
        modality_counts: Counter[str] = Counter()
        higher_order = 0

        for event in self.mesh.transformations.values():
            src_atoms = [self.mesh.atom(x) for x in event.source_atoms]
            dst_atoms = [self.mesh.atom(x) for x in event.target_atoms]
            scales = sorted({a.scale for a in src_atoms + dst_atoms})
            modalities = sorted({a.modality for a in src_atoms + dst_atoms})
            times = sorted({a.time for a in src_atoms + dst_atoms})
            path = list(event.metadata.get("higher_order_path", []))
            if path:
                higher_order += 1
            pair_counts[event.transformation_type] += 1
            observer_counts[event.observer] += 1
            context_counts[event.context] += 1
            for x in scales:
                scale_counts[x] += 1
            for x in modalities:
                modality_counts[x] += 1
            entries.append({
                "event_id": event.id,
                "source_type": event.source_type.value,
                "target_type": event.target_type.value,
                "operator": event.operator,
                "observer": event.observer,
                "context": event.context,
                "scales": scales,
                "modalities": modalities,
                "times": times,
                "semantic_gain": event.semantic_gain,
                "semantic_loss": event.semantic_loss,
                "reversibility": event.reversibility,
                "higher_order_path": path,
            })

        matrix = {
            s.value: {t.value: int(pair_counts.get(f"{s.value}->{t.value}", 0)) for t in DIKWPType.ordered()}
            for s in DIKWPType.ordered()
        }
        active_pairs = sum(1 for v in pair_counts.values() if v > 0)
        return {
            "axes": ["source_type", "target_type", "observer", "context", "time", "modality", "scale", "provenance"],
            "primitive_matrix": matrix,
            "entries": entries,
            "event_count": len(entries),
            "active_primitive_pairs": active_pairs,
            "primitive_coverage": round(active_pairs / 25.0, 6),
            "higher_order_event_count": higher_order,
            "observer_diversity_entropy": round(self._entropy(observer_counts), 6),
            "context_diversity_entropy": round(self._entropy(context_counts), 6),
            "scale_diversity_entropy": round(self._entropy(scale_counts), 6),
            "modality_diversity_entropy": round(self._entropy(modality_counts), 6),
            "interpretation": "The 5×5 operator matrix is a base alphabet; actual meaning is indexed by observer, context, time, modality, scale and provenance.",
        }
