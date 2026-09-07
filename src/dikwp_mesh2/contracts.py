from __future__ import annotations

from typing import Dict, List, Mapping, Sequence


class SemanticContractCompiler:
    """Compiles task-specific contracts instead of a single concept definition."""

    def compile(
        self,
        concept: str,
        invariants: Sequence[Mapping[str, object]],
        conflicts: Sequence[Mapping[str, object]],
        residuals: Sequence[Mapping[str, object]],
        escape_candidates: Sequence[Mapping[str, object]],
    ) -> List[Dict[str, object]]:
        invariant_names = [str(x.get("semantic_feature")) for x in invariants[:8]]
        conflict_names = [str(x.get("semantic_feature")) for x in conflicts[:6]]
        residual_names = [str(x.get("semantic_feature")) for x in residuals[:6]]
        axes = [str(x.get("candidate_dimension")) for x in escape_candidates[:5]]
        return [
            {
                "contract": "recognition-and-classification",
                "concept": concept,
                "use": "Compare candidates without asserting an observer-free essence.",
                "minimum_shared_features": invariant_names,
                "must_report_conflicts": conflict_names,
                "must_preserve_residuals": residual_names,
                "candidate_new_axes": axes,
                "decision_output": ["inside-operational-boundary", "outside-operational-boundary", "liminal", "insufficient-evidence"],
                "prohibited_output": "single metaphysical truth label",
            },
            {
                "contract": "research-and-concept-escape",
                "concept": concept,
                "use": "Discover missing dimensions and redesign experiments when existing concepts compress away relevant structure.",
                "minimum_shared_features": invariant_names[:5],
                "must_report_conflicts": conflict_names,
                "must_preserve_residuals": residual_names,
                "candidate_new_axes": axes,
                "decision_output": ["retain-axis", "split-axis", "merge-axis", "seed-new-axis", "defer"],
                "prohibited_output": "installing a new axis without preregistered discriminating tests",
            },
            {
                "contract": "governance-and-rights",
                "concept": concept,
                "use": "Make decisions while acknowledging that different operational purposes require different boundaries.",
                "minimum_shared_features": invariant_names[:5],
                "must_report_conflicts": conflict_names,
                "must_preserve_residuals": residual_names,
                "candidate_new_axes": axes,
                "decision_output": ["precautionary-protection", "ordinary-treatment", "independent-review", "no-action"],
                "prohibited_output": "using semantic consensus as a substitute for legal authority, welfare evidence, or due process",
            },
        ]
