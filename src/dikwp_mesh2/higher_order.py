from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Dict, Iterable, List, Mapping, Sequence

from .models import DIKWPType
from .operators import TransformRegistry


@dataclass(frozen=True, slots=True)
class CompositeTransform:
    path: List[str]
    primitive_operators: List[str]
    cumulative_loss: float
    reversibility: float
    generativity: float
    evidence_need: float

    def to_dict(self) -> Dict[str, object]:
        return asdict(self)


def compose_types(path: Sequence[str | DIKWPType], registry: TransformRegistry | None = None) -> CompositeTransform:
    registry = registry or TransformRegistry()
    nodes = [x.value if isinstance(x, DIKWPType) else str(x).upper() for x in path]
    if len(nodes) < 2:
        raise ValueError("A composite transformation needs at least two DIKWP types")
    for node in nodes:
        if node not in {x.value for x in DIKWPType.ordered()}:
            raise ValueError(f"Unknown DIKWP type: {node}")
    loss = 0.0
    reversibility = 1.0
    generativity = 0.0
    evidence_need = 0.0
    names: List[str] = []
    for a, b in zip(nodes, nodes[1:]):
        op = registry.get(a, b)
        names.append(op.name)
        loss = 1.0 - (1.0 - loss) * (1.0 - op.base_loss)
        reversibility *= op.reversibility
        generativity = 1.0 - (1.0 - generativity) * (1.0 - op.generativity)
        evidence_need = 1.0 - (1.0 - evidence_need) * (1.0 - op.evidence_need)
    return CompositeTransform(
        path=nodes,
        primitive_operators=names,
        cumulative_loss=round(loss, 6),
        reversibility=round(reversibility, 6),
        generativity=round(generativity, 6),
        evidence_need=round(evidence_need, 6),
    )


class MetaOperatorEvolutionEngine:
    """Proposes higher-order operators when fixed concepts or primitive paths fail.

    A proposal is not silently installed. It carries triggering obstructions, a
    test plan and a rollback condition. This prevents 'concept escape' from
    becoming unconstrained invention.
    """

    def propose(
        self,
        conflicts: Sequence[Mapping[str, object]],
        residuals: Sequence[Mapping[str, object]],
        escape_candidates: Sequence[Mapping[str, object]],
        gluing: Mapping[str, object],
    ) -> List[Dict[str, object]]:
        proposals: List[Dict[str, object]] = []
        obstruction = float(gluing.get("obstruction_score", 0.0))
        conflict_names = [str(x.get("semantic_feature")) for x in conflicts[:5]]
        residual_names = [str(x.get("semantic_feature")) for x in residuals[:5]]

        if obstruction >= 0.35:
            proposals.append({
                "name": "obstruction-preserving-glue",
                "path": ["I->K", "K->W", "W->I"],
                "purpose": "Construct a shared model, audit its value/power effects, then return contested distinctions to the information graph instead of forcing consensus.",
                "triggers": conflict_names,
                "installation_status": "proposal-only",
                "validation": "The operator is accepted only if it improves predictive coordination without reducing recorded dissent or provenance.",
                "rollback": "Rollback when minority residual coverage falls or contradiction detection weakens.",
            })
        if residual_names:
            proposals.append({
                "name": "residual-to-new-axis",
                "path": ["K->I", "I->P", "P->D", "D->K"],
                "purpose": "Convert recurring untranslatable residuals into a candidate semantic dimension, design observations for it, and test whether it explains previously disconnected cases.",
                "triggers": residual_names,
                "installation_status": "proposal-only",
                "validation": "Pre-register cases that the new axis must separate and cases on which it must remain neutral.",
                "rollback": "Delete or quarantine the axis if it merely renames an existing feature or amplifies one observer's language.",
            })
        for candidate in escape_candidates[:3]:
            proposals.append({
                "name": f"axis-seeding::{candidate.get('candidate_dimension_en')}",
                "path": ["P->I", "I->D", "D->K", "K->P"],
                "purpose": f"Operationalize the candidate dimension '{candidate.get('candidate_dimension')}' through measurements, models, and purpose revision.",
                "triggers": list(candidate.get("trigger_features", [])),
                "installation_status": "proposal-only",
                "validation": str(candidate.get("operational_question", "")),
                "rollback": "Suspend if the dimension has low cross-observer transfer or cannot generate discriminating tests.",
            })
        return proposals
