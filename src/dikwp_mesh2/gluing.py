from __future__ import annotations

from collections import Counter, defaultdict
from typing import Dict, Iterable, List, Mapping, Sequence, Tuple

from .mesh import SemanticMesh


class SemanticGluingEngine:
    """A pragmatic local-to-global consistency engine.

    Each observer view is a local semantic section. Compatible overlaps may be
    glued into a shared invariant section. Incompatible overlaps are retained as
    obstructions rather than silently averaged.
    """

    def __init__(self, mesh: SemanticMesh) -> None:
        self.mesh = mesh

    def analyze(self, support_threshold: float = 0.45, contradiction_threshold: float = 0.35) -> Dict[str, object]:
        observers = sorted(self.mesh.views)
        total = max(1, len(observers))
        tag_support: Counter[str] = Counter()
        tag_stances: Dict[str, List[Tuple[str, float]]] = defaultdict(list)
        tag_contexts: Dict[str, set[str]] = defaultdict(set)
        for observer, view in self.mesh.views.items():
            seen = set()
            for atom in view.atoms:
                for tag in atom.tags:
                    seen.add(tag)
                    tag_contexts[tag].add(atom.context)
                for tag, stance in atom.stance.items():
                    tag_stances[tag].append((observer, stance))
            for tag in seen:
                tag_support[tag] += 1

        shared_sections: List[Dict[str, object]] = []
        obstructions: List[Dict[str, object]] = []
        partial_sections: List[Dict[str, object]] = []
        for tag, count in sorted(tag_support.items(), key=lambda kv: (-kv[1], kv[0])):
            support = count / total
            stances = tag_stances.get(tag, [])
            pos = sum(1 for _, value in stances if value > 0.15)
            neg = sum(1 for _, value in stances if value < -0.15)
            contradictory = pos > 0 and neg > 0
            contradiction = min(pos, neg) / max(1, pos + neg)
            record = {
                "semantic_feature": tag,
                "support": round(support, 6),
                "observer_count": count,
                "contexts": sorted(tag_contexts[tag]),
                "positive_stances": pos,
                "negative_stances": neg,
                "contradiction": round(contradiction, 6),
            }
            if support >= support_threshold and contradiction <= contradiction_threshold:
                shared_sections.append(record)
            elif contradictory and contradiction > contradiction_threshold:
                obstructions.append(record)
            else:
                partial_sections.append(record)

        overlaps = self.mesh.alignment_edges(min_similarity=0.10)
        if overlaps:
            incompat_mass = sum((1.0 - e.compatibility) + 0.25 * len(e.conflicts) for e in overlaps)
            obstruction_score = min(1.0, incompat_mass / (1.25 * len(overlaps)))
            compatibility_score = sum(e.compatibility for e in overlaps) / len(overlaps)
        else:
            obstruction_score = 1.0
            compatibility_score = 0.0

        global_section_exists = bool(shared_sections) and obstruction_score < 0.72
        return {
            "global_section_status": "partial-global-section" if global_section_exists else "no-stable-global-section",
            "shared_sections": shared_sections,
            "partial_sections": partial_sections,
            "obstructions": obstructions,
            "obstruction_score": round(obstruction_score, 6),
            "mean_overlap_compatibility": round(compatibility_score, 6),
            "interpretation": (
                "A shared semantic kernel can be glued, but it does not erase local meanings."
                if global_section_exists
                else "Local meanings cannot yet be glued without unacceptable semantic loss; preserve plurality and gather new evidence."
            ),
        }
