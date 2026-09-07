"""DIKWP-MESH² package."""

from .models import DIKWPType, SemanticAtom, TransformationEvent, ObserverView
from .mesh import SemanticMesh
from .operators import TransformRegistry
from .higher_order import compose_types, MetaOperatorEvolutionEngine
from .tensor import TransformationTensor

__all__ = [
    "DIKWPType",
    "SemanticAtom",
    "TransformationEvent",
    "ObserverView",
    "SemanticMesh",
    "TransformRegistry",
    "compose_types",
    "MetaOperatorEvolutionEngine",
    "TransformationTensor",
]

__version__ = "1.0.0"
