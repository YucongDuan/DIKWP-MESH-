from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Mapping, Sequence

from .models import ObserverView, SemanticAtom, TransformationEvent, DIKWPType
from .mesh import SemanticMesh


def load_bundle(path: str | Path) -> SemanticMesh:
    path = Path(path)
    data = json.loads(path.read_text(encoding="utf-8"))
    mesh = SemanticMesh(data["concept"])
    for view_data in data["observers"]:
        atoms: List[SemanticAtom] = []
        for atom_data in view_data["atoms"]:
            atoms.append(
                SemanticAtom(
                    id=atom_data["id"],
                    label=atom_data["label"],
                    observer=view_data["observer"],
                    context=atom_data.get("context", view_data.get("context", "general")),
                    type_weights=atom_data["type_weights"],
                    tags=set(atom_data.get("tags", [])),
                    stance=atom_data.get("stance", {}),
                    evidence=atom_data.get("evidence", []),
                    confidence=atom_data.get("confidence", 0.5),
                    modality=atom_data.get("modality", "text"),
                    scale=atom_data.get("scale", "unspecified"),
                    time=atom_data.get("time", "present"),
                    source=atom_data.get("source", ""),
                    metadata=atom_data.get("metadata", {}),
                )
            )
        view = ObserverView(
            observer=view_data["observer"],
            role=view_data.get("role", "observer"),
            context=view_data.get("context", "general"),
            purpose_profile=view_data.get("purpose_profile", {}),
            atoms=atoms,
            metadata=view_data.get("metadata", {}),
        )
        mesh.add_view(view)

    for tr in data.get("transformations", []):
        mesh.add_transformation(
            TransformationEvent(
                id=tr["id"],
                source_atoms=tr["source_atoms"],
                target_atoms=tr["target_atoms"],
                source_type=DIKWPType(tr["source_type"]),
                target_type=DIKWPType(tr["target_type"]),
                operator=tr["operator"],
                observer=tr.get("observer", "system"),
                context=tr.get("context", "general"),
                semantic_gain=tr.get("semantic_gain", 0.0),
                semantic_loss=tr.get("semantic_loss", 0.0),
                evidence_delta=tr.get("evidence_delta", 0.0),
                reversibility=tr.get("reversibility", 0.5),
                purpose_shift=tr.get("purpose_shift", 0.0),
                notes=tr.get("notes", ""),
                metadata=tr.get("metadata", {}),
            )
        )
    for h in data.get("hyperrelations", []):
        mesh.add_hyperrelation(h["id"], h["label"], h["atom_ids"], h.get("relation_type", "relation"))
    return mesh


def write_json(path: str | Path, data: Any) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
