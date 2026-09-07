from __future__ import annotations

from dataclasses import asdict
from typing import Dict, Iterable, List, Mapping, Sequence, Tuple

import networkx as nx

from .models import DIKWPType
from .operators import TransformRegistry


class TransformationRouter:
    def __init__(self, registry: TransformRegistry | None = None) -> None:
        self.registry = registry or TransformRegistry()
        self.graph = nx.DiGraph()
        for typ in DIKWPType.ordered():
            self.graph.add_node(typ.value)
        for op in self.registry.all():
            self.graph.add_edge(op.source.value, op.target.value, operator=op)

    def top_paths(
        self,
        source: DIKWPType | str,
        target: DIKWPType | str,
        top_k: int = 5,
        max_hops: int = 4,
        purpose_bias: Mapping[str, float] | None = None,
        avoid: Sequence[str] | None = None,
    ) -> List[Dict[str, object]]:
        src = source.value if isinstance(source, DIKWPType) else str(source).upper()
        dst = target.value if isinstance(target, DIKWPType) else str(target).upper()
        if src not in self.graph or dst not in self.graph:
            raise ValueError("Source and target must be one of D/I/K/W/P")
        avoid = set(avoid or [])
        candidates: List[Dict[str, object]] = []
        for path in nx.all_simple_paths(self.graph, src, dst, cutoff=max_hops):
            if len(path) == 1:
                continue
            operators = []
            cost = 0.0
            loss = 0.0
            reversibility = 1.0
            generativity = 0.0
            blocked = False
            for a, b in zip(path, path[1:]):
                key = f"{a}->{b}"
                if key in avoid:
                    blocked = True
                    break
                op = self.registry.get(a, b)
                operators.append({
                    "type": key,
                    "name": op.name,
                    "description": op.description,
                    "base_loss": op.base_loss,
                    "reversibility": op.reversibility,
                    "generativity": op.generativity,
                })
                cost += op.path_cost(purpose_bias)
                loss = 1.0 - (1.0 - loss) * (1.0 - op.base_loss)
                reversibility *= op.reversibility
                generativity = 1.0 - (1.0 - generativity) * (1.0 - op.generativity)
            if blocked:
                continue
            candidates.append({
                "path": path,
                "operators": operators,
                "hops": len(path) - 1,
                "cost": round(cost, 6),
                "cumulative_loss": round(loss, 6),
                "path_reversibility": round(reversibility, 6),
                "path_generativity": round(generativity, 6),
            })
        candidates.sort(key=lambda x: (x["cost"], x["cumulative_loss"], -x["path_generativity"], x["hops"]))
        return candidates[:top_k]
