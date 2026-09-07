from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Mapping, Sequence, Tuple

from .models import DIKWPType


@dataclass(frozen=True, slots=True)
class TransformOperator:
    source: DIKWPType
    target: DIKWPType
    name: str
    description: str
    base_loss: float
    evidence_need: float
    reversibility: float
    generativity: float

    @property
    def key(self) -> str:
        return f"{self.source.value}->{self.target.value}"

    def path_cost(self, purpose_bias: Mapping[str, float] | None = None) -> float:
        purpose_bias = purpose_bias or {}
        preference = float(purpose_bias.get(self.key, 0.0))
        cost = 0.52 * self.base_loss + 0.28 * self.evidence_need + 0.20 * (1.0 - self.reversibility)
        return max(0.01, cost - 0.25 * preference)


_OPERATOR_SPECS: Dict[Tuple[str, str], Tuple[str, str, float, float, float, float]] = {
    ("D", "D"): ("re-observe", "Re-sample, calibrate, denoise, aggregate, or change measurement granularity.", 0.08, 0.25, 0.90, 0.20),
    ("D", "I"): ("differentiate", "Extract distinctions, regularities, contrasts, and context-dependent relations from observations.", 0.16, 0.30, 0.78, 0.45),
    ("D", "K"): ("abduce-model", "Generate causal or generative hypotheses directly from observations while exposing assumptions.", 0.34, 0.62, 0.42, 0.65),
    ("D", "W"): ("salience-evaluate", "Assess immediate welfare, risk, or value relevance of observations without assuming a final theory.", 0.42, 0.58, 0.35, 0.55),
    ("D", "P"): ("purpose-infer", "Infer candidate purposes or demands from observed behavior, with a high risk of projection.", 0.55, 0.72, 0.25, 0.60),
    ("I", "D"): ("operationalize", "Turn a relation or distinction into measurable variables, probes, and observations.", 0.20, 0.42, 0.70, 0.45),
    ("I", "I"): ("re-segment", "Reframe, regroup, compress, or expand relational structure under another context.", 0.12, 0.28, 0.82, 0.55),
    ("I", "K"): ("generalize", "Build explanatory, predictive, or causal models from relational patterns.", 0.28, 0.52, 0.48, 0.66),
    ("I", "W"): ("consequence-map", "Translate patterns into value, risk, fairness, resilience, or long-term consequence structures.", 0.35, 0.48, 0.42, 0.58),
    ("I", "P"): ("question-form", "Transform detected differences into questions, goals, or intervention candidates.", 0.32, 0.40, 0.55, 0.72),
    ("K", "D"): ("predict-test", "Derive observable predictions and discriminating experiments from a model.", 0.18, 0.30, 0.76, 0.44),
    ("K", "I"): ("derive-signature", "Extract relational signatures, implications, and compressed explanations from knowledge.", 0.15, 0.25, 0.80, 0.42),
    ("K", "K"): ("model-revise", "Integrate, split, negate, analogize, or revise models while retaining provenance.", 0.14, 0.38, 0.65, 0.74),
    ("K", "W"): ("implication-audit", "Evaluate model consequences, trade-offs, distributional effects, and unknown risks.", 0.24, 0.45, 0.54, 0.60),
    ("K", "P"): ("goal-design", "Formulate controllable objectives, experiments, or commitments from a knowledge model.", 0.28, 0.42, 0.52, 0.65),
    ("W", "D"): ("value-directed-observe", "Select observations required by safety, justice, welfare, or reversibility concerns.", 0.22, 0.35, 0.68, 0.50),
    ("W", "I"): ("value-reweight", "Change which distinctions matter under different affected parties and horizons.", 0.20, 0.32, 0.66, 0.58),
    ("W", "K"): ("normative-model-select", "Select, constrain, or challenge explanatory models using explicit values and harms.", 0.31, 0.55, 0.45, 0.62),
    ("W", "W"): ("value-negotiate", "Expose conflicts among values, stakeholders, time horizons, and scales without forced consensus.", 0.18, 0.44, 0.56, 0.72),
    ("W", "P"): ("commit", "Convert evaluated trade-offs into bounded purposes, duties, prohibitions, or exit conditions.", 0.21, 0.36, 0.60, 0.54),
    ("P", "D"): ("purpose-select-observation", "Choose what to measure, sample, or preserve in order to pursue or audit a purpose.", 0.24, 0.38, 0.65, 0.48),
    ("P", "I"): ("purpose-frame", "Choose distinctions and relations relevant to a purpose while logging excluded alternatives.", 0.28, 0.42, 0.57, 0.58),
    ("P", "K"): ("purpose-construct-knowledge", "Select or construct models needed for a purpose, with explicit risk of motivated reasoning.", 0.40, 0.60, 0.38, 0.70),
    ("P", "W"): ("means-ends-audit", "Audit whether a purpose and its means remain acceptable under consequences and other purposes.", 0.22, 0.40, 0.64, 0.60),
    ("P", "P"): ("purpose-transform", "Split, merge, negotiate, suspend, reverse, or replace purposes and representation rights.", 0.26, 0.48, 0.50, 0.82),
}


class TransformRegistry:
    def __init__(self) -> None:
        self._operators: Dict[str, TransformOperator] = {}
        for src in DIKWPType.ordered():
            for dst in DIKWPType.ordered():
                name, description, loss, need, rev, gen = _OPERATOR_SPECS[(src.value, dst.value)]
                operator = TransformOperator(src, dst, name, description, loss, need, rev, gen)
                self._operators[operator.key] = operator

    def get(self, source: DIKWPType | str, target: DIKWPType | str) -> TransformOperator:
        s = source.value if isinstance(source, DIKWPType) else str(source).upper()
        t = target.value if isinstance(target, DIKWPType) else str(target).upper()
        return self._operators[f"{s}->{t}"]

    def all(self) -> List[TransformOperator]:
        return [self._operators[k] for k in sorted(self._operators)]

    def as_matrix(self) -> Dict[str, Dict[str, Dict[str, float | str]]]:
        result: Dict[str, Dict[str, Dict[str, float | str]]] = {}
        for src in DIKWPType.ordered():
            result[src.value] = {}
            for dst in DIKWPType.ordered():
                op = self.get(src, dst)
                result[src.value][dst.value] = {
                    "name": op.name,
                    "description": op.description,
                    "base_loss": op.base_loss,
                    "evidence_need": op.evidence_need,
                    "reversibility": op.reversibility,
                    "generativity": op.generativity,
                }
        return result
