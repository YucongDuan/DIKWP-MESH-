from __future__ import annotations

from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Set, Tuple


class DIKWPType(str, Enum):
    D = "D"
    I = "I"
    K = "K"
    W = "W"
    P = "P"

    @classmethod
    def ordered(cls) -> Tuple["DIKWPType", ...]:
        return (cls.D, cls.I, cls.K, cls.W, cls.P)


def normalize_weights(weights: Mapping[str | DIKWPType, float]) -> Dict[str, float]:
    out = {t.value: 0.0 for t in DIKWPType.ordered()}
    for key, value in weights.items():
        k = key.value if isinstance(key, DIKWPType) else str(key).upper()
        if k not in out:
            raise ValueError(f"Unknown DIKWP type: {key}")
        out[k] = max(0.0, float(value))
    total = sum(out.values())
    if total <= 0:
        raise ValueError("At least one DIKWP weight must be positive")
    return {k: v / total for k, v in out.items()}


@dataclass(slots=True)
class SemanticAtom:
    id: str
    label: str
    observer: str
    context: str
    type_weights: Dict[str, float]
    tags: Set[str] = field(default_factory=set)
    stance: Dict[str, float] = field(default_factory=dict)
    evidence: List[str] = field(default_factory=list)
    confidence: float = 0.5
    modality: str = "text"
    scale: str = "unspecified"
    time: str = "present"
    source: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.type_weights = normalize_weights(self.type_weights)
        self.tags = {str(t).strip() for t in self.tags if str(t).strip()}
        self.confidence = min(1.0, max(0.0, float(self.confidence)))
        self.stance = {str(k): max(-1.0, min(1.0, float(v))) for k, v in self.stance.items()}

    @property
    def dominant_type(self) -> DIKWPType:
        key = max(self.type_weights, key=self.type_weights.get)
        return DIKWPType(key)

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["tags"] = sorted(self.tags)
        return data


@dataclass(slots=True)
class TransformationEvent:
    id: str
    source_atoms: List[str]
    target_atoms: List[str]
    source_type: DIKWPType
    target_type: DIKWPType
    operator: str
    observer: str
    context: str
    semantic_gain: float = 0.0
    semantic_loss: float = 0.0
    evidence_delta: float = 0.0
    reversibility: float = 0.5
    purpose_shift: float = 0.0
    notes: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for name in ("semantic_gain", "semantic_loss", "reversibility"):
            value = float(getattr(self, name))
            setattr(self, name, min(1.0, max(0.0, value)))
        self.evidence_delta = max(-1.0, min(1.0, float(self.evidence_delta)))
        self.purpose_shift = max(-1.0, min(1.0, float(self.purpose_shift)))

    @property
    def transformation_type(self) -> str:
        return f"{self.source_type.value}->{self.target_type.value}"

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["source_type"] = self.source_type.value
        data["target_type"] = self.target_type.value
        data["transformation_type"] = self.transformation_type
        return data


@dataclass(slots=True)
class ObserverView:
    observer: str
    role: str
    context: str
    purpose_profile: Dict[str, float]
    atoms: List[SemanticAtom]
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.purpose_profile = {str(k): max(0.0, float(v)) for k, v in self.purpose_profile.items()}
        total = sum(self.purpose_profile.values())
        if total:
            self.purpose_profile = {k: v / total for k, v in self.purpose_profile.items()}

    def tag_set(self) -> Set[str]:
        out: Set[str] = set()
        for atom in self.atoms:
            out |= atom.tags
        return out

    def to_dict(self) -> Dict[str, Any]:
        return {
            "observer": self.observer,
            "role": self.role,
            "context": self.context,
            "purpose_profile": self.purpose_profile,
            "atoms": [a.to_dict() for a in self.atoms],
            "metadata": self.metadata,
        }


@dataclass(slots=True)
class AlignmentEdge:
    atom_a: str
    atom_b: str
    observer_a: str
    observer_b: str
    similarity: float
    compatibility: float
    shared_tags: List[str]
    conflicts: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class SemanticBundleResult:
    concept: str
    observer_count: int
    atom_count: int
    invariant_kernel: List[Dict[str, Any]]
    perspective_branches: List[Dict[str, Any]]
    conflicts: List[Dict[str, Any]]
    residuals: List[Dict[str, Any]]
    escape_candidates: List[Dict[str, Any]]
    gluing: Dict[str, Any]
    metrics: Dict[str, float]
    transformation_usage: Dict[str, int]
    hierarchy_audit: Dict[str, Any]
    transformation_tensor: Dict[str, Any] = field(default_factory=dict)
    meta_operator_proposals: List[Dict[str, Any]] = field(default_factory=list)
    semantic_contracts: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
