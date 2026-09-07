from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass
from math import sqrt
from typing import Dict, Iterable, List, Mapping, Optional, Sequence, Set, Tuple

import networkx as nx

from .models import AlignmentEdge, DIKWPType, ObserverView, SemanticAtom, TransformationEvent


def cosine_weights(a: Mapping[str, float], b: Mapping[str, float]) -> float:
    keys = set(a) | set(b)
    num = sum(float(a.get(k, 0.0)) * float(b.get(k, 0.0)) for k in keys)
    da = sqrt(sum(float(a.get(k, 0.0)) ** 2 for k in keys))
    db = sqrt(sum(float(b.get(k, 0.0)) ** 2 for k in keys))
    if da == 0 or db == 0:
        return 0.0
    return num / (da * db)


def jaccard(a: Set[str], b: Set[str]) -> float:
    if not a and not b:
        return 1.0
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


class SemanticMesh:
    """A multi-observer, typed semantic multigraph.

    D/I/K/W/P are co-equal node-type weights. Transformation edges may form cycles,
    branches, merges, and higher-order paths. Hyper-relations are represented by
    relation nodes connected to all participating atoms.
    """

    def __init__(self, concept: str) -> None:
        self.concept = concept
        self.graph = nx.MultiDiGraph(concept=concept)
        self.views: Dict[str, ObserverView] = {}
        self.transformations: Dict[str, TransformationEvent] = {}
        self.hyperedge_nodes: Set[str] = set()

    def add_view(self, view: ObserverView) -> None:
        if view.observer in self.views:
            raise ValueError(f"Duplicate observer: {view.observer}")
        self.views[view.observer] = view
        for atom in view.atoms:
            self.add_atom(atom)

    def add_atom(self, atom: SemanticAtom) -> None:
        if atom.id in self.graph:
            raise ValueError(f"Duplicate atom id: {atom.id}")
        self.graph.add_node(atom.id, kind="atom", atom=atom, observer=atom.observer)

    def add_transformation(self, event: TransformationEvent) -> None:
        if event.id in self.transformations:
            raise ValueError(f"Duplicate transformation id: {event.id}")
        self.transformations[event.id] = event
        for src in event.source_atoms:
            for dst in event.target_atoms:
                if src not in self.graph or dst not in self.graph:
                    raise KeyError(f"Unknown transformation endpoint: {src} -> {dst}")
                self.graph.add_edge(
                    src,
                    dst,
                    key=event.id,
                    kind="transformation",
                    event=event,
                    transform_type=event.transformation_type,
                    weight=max(0.01, 1.0 - event.semantic_loss),
                )

    def add_hyperrelation(self, relation_id: str, label: str, atom_ids: Sequence[str], relation_type: str) -> None:
        if relation_id in self.graph:
            raise ValueError(f"Duplicate relation id: {relation_id}")
        self.graph.add_node(relation_id, kind="hyperrelation", label=label, relation_type=relation_type)
        self.hyperedge_nodes.add(relation_id)
        for atom_id in atom_ids:
            if atom_id not in self.graph:
                raise KeyError(atom_id)
            self.graph.add_edge(atom_id, relation_id, kind="membership", weight=1.0)
            self.graph.add_edge(relation_id, atom_id, kind="membership", weight=1.0)

    def atoms(self) -> List[SemanticAtom]:
        return [data["atom"] for _, data in self.graph.nodes(data=True) if data.get("kind") == "atom"]

    def atom(self, atom_id: str) -> SemanticAtom:
        return self.graph.nodes[atom_id]["atom"]

    def alignment_edges(self, min_similarity: float = 0.24) -> List[AlignmentEdge]:
        atoms = self.atoms()
        out: List[AlignmentEdge] = []
        for i, a in enumerate(atoms):
            for b in atoms[i + 1 :]:
                if a.observer == b.observer:
                    continue
                shared = sorted(a.tags & b.tags)
                tag_sim = jaccard(a.tags, b.tags)
                type_sim = cosine_weights(a.type_weights, b.type_weights)
                context_sim = 1.0 if a.context == b.context else 0.55
                conflicts: List[str] = []
                stance_overlap = set(a.stance) & set(b.stance)
                stance_agreement: List[float] = []
                for key in stance_overlap:
                    delta = abs(a.stance[key] - b.stance[key])
                    stance_agreement.append(1.0 - delta / 2.0)
                    if a.stance[key] * b.stance[key] < -0.12:
                        conflicts.append(key)
                stance_score = sum(stance_agreement) / len(stance_agreement) if stance_agreement else 0.65
                similarity = 0.48 * tag_sim + 0.25 * type_sim + 0.12 * context_sim + 0.15 * stance_score
                compatibility = similarity * (1.0 - 0.20 * min(1.0, len(conflicts) / 2.0))
                if similarity >= min_similarity or shared:
                    out.append(
                        AlignmentEdge(
                            atom_a=a.id,
                            atom_b=b.id,
                            observer_a=a.observer,
                            observer_b=b.observer,
                            similarity=round(similarity, 6),
                            compatibility=round(compatibility, 6),
                            shared_tags=shared,
                            conflicts=sorted(conflicts),
                        )
                    )
        return sorted(out, key=lambda e: (-e.similarity, e.atom_a, e.atom_b))

    def observer_similarity(self) -> Dict[str, Dict[str, float]]:
        observers = sorted(self.views)
        result: Dict[str, Dict[str, float]] = {o: {} for o in observers}
        for a in observers:
            for b in observers:
                if a == b:
                    result[a][b] = 1.0
                    continue
                tags_a, tags_b = self.views[a].tag_set(), self.views[b].tag_set()
                tag_sim = jaccard(tags_a, tags_b)
                purpose_sim = cosine_weights(self.views[a].purpose_profile, self.views[b].purpose_profile)
                result[a][b] = round(0.72 * tag_sim + 0.28 * purpose_sim, 6)
        return result

    def transformation_usage(self) -> Dict[str, int]:
        counts = Counter(event.transformation_type for event in self.transformations.values())
        return {f"{s.value}->{t.value}": int(counts.get(f"{s.value}->{t.value}", 0)) for s in DIKWPType.ordered() for t in DIKWPType.ordered()}

    def cycles(self) -> List[List[str]]:
        simple = nx.DiGraph()
        for u, v, data in self.graph.edges(data=True):
            if data.get("kind") == "transformation":
                simple.add_edge(u, v)
        return list(nx.simple_cycles(simple))

    def centrality_by_type(self) -> Dict[str, float]:
        simple = nx.DiGraph()
        for node_id, data in self.graph.nodes(data=True):
            if data.get("kind") == "atom":
                simple.add_node(node_id)
        for u, v, data in self.graph.edges(data=True):
            if data.get("kind") == "transformation" and u in simple and v in simple:
                simple.add_edge(u, v)
        if not simple:
            return {t.value: 0.0 for t in DIKWPType.ordered()}
        c = nx.pagerank(simple, alpha=0.85) if simple.number_of_edges() else {n: 1 / len(simple) for n in simple}
        sums = {t.value: 0.0 for t in DIKWPType.ordered()}
        for node_id, value in c.items():
            atom = self.atom(node_id)
            for typ, weight in atom.type_weights.items():
                sums[typ] += value * weight
        total = sum(sums.values()) or 1.0
        return {k: round(v / total, 6) for k, v in sums.items()}
