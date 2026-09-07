from __future__ import annotations

from collections import Counter, defaultdict
from math import log2
from typing import Dict, Iterable, List, Mapping, Sequence, Tuple

from .mesh import SemanticMesh


class InvariantMiner:
    def __init__(self, mesh: SemanticMesh) -> None:
        self.mesh = mesh

    def mine(self, min_support: float = 0.40) -> Dict[str, List[Dict[str, object]]]:
        observers = sorted(self.mesh.views)
        total = max(1, len(observers))
        tag_observers: Dict[str, set[str]] = defaultdict(set)
        tag_types: Dict[str, Counter[str]] = defaultdict(Counter)
        tag_conf: Dict[str, List[float]] = defaultdict(list)
        tag_stances: Dict[str, List[float]] = defaultdict(list)
        tag_labels: Dict[str, List[str]] = defaultdict(list)

        for observer, view in self.mesh.views.items():
            for atom in view.atoms:
                for tag in atom.tags:
                    tag_observers[tag].add(observer)
                    tag_conf[tag].append(atom.confidence)
                    tag_labels[tag].append(atom.label)
                    for typ, weight in atom.type_weights.items():
                        tag_types[tag][typ] += weight
                for tag, value in atom.stance.items():
                    tag_stances[tag].append(value)

        invariants: List[Dict[str, object]] = []
        branches: List[Dict[str, object]] = []
        conflicts: List[Dict[str, object]] = []
        residuals: List[Dict[str, object]] = []

        for tag in sorted(tag_observers):
            support = len(tag_observers[tag]) / total
            stances = tag_stances.get(tag, [])
            positive = sum(1 for x in stances if x > 0.15)
            negative = sum(1 for x in stances if x < -0.15)
            mean_stance = sum(stances) / len(stances) if stances else 0.0
            disagreement = 0.0
            if stances:
                mean = mean_stance
                disagreement = sum((x - mean) ** 2 for x in stances) / len(stances)
            type_mass = tag_types[tag]
            mass_total = sum(type_mass.values()) or 1.0
            type_distribution = {k: round(v / mass_total, 6) for k, v in sorted(type_mass.items())}
            type_entropy = -sum(p * log2(p) for p in type_distribution.values() if p > 0)
            record = {
                "semantic_feature": tag,
                "support": round(support, 6),
                "observers": sorted(tag_observers[tag]),
                "mean_confidence": round(sum(tag_conf[tag]) / len(tag_conf[tag]), 6),
                "mean_stance": round(mean_stance, 6),
                "disagreement": round(disagreement, 6),
                "type_distribution": type_distribution,
                "type_entropy": round(type_entropy, 6),
                "example_labels": tag_labels[tag][:4],
            }
            if support >= min_support and not (positive and negative and disagreement > 0.28):
                invariants.append(record)
            elif positive and negative:
                record["positive_count"] = positive
                record["negative_count"] = negative
                conflicts.append(record)
            elif support >= 0.20:
                branches.append(record)
            else:
                residuals.append(record)

        invariants.sort(key=lambda x: (-x["support"], -x["mean_confidence"], x["semantic_feature"]))
        branches.sort(key=lambda x: (-x["support"], -x["type_entropy"], x["semantic_feature"]))
        conflicts.sort(key=lambda x: (-x["disagreement"], -x["support"], x["semantic_feature"]))
        residuals.sort(key=lambda x: (-x["type_entropy"], -x["support"], x["semantic_feature"]))
        return {
            "invariant_kernel": invariants,
            "perspective_branches": branches,
            "conflicts": conflicts,
            "residuals": residuals,
        }
