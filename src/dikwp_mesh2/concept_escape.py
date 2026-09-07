from __future__ import annotations

from collections import Counter, defaultdict
from itertools import combinations
from typing import Dict, Iterable, List, Mapping, Sequence, Tuple

from .mesh import SemanticMesh


DIMENSION_CATALOG = [
    {
        "name": "规则自修改能力",
        "name_en": "rule-self-modification",
        "triggers": {"rule_change", "self_modification", "open_evolution", "meta_dynamics", "novelty"},
        "question": "系统是否能够改变产生自身适应、学习、复制或定义的规则，而不只是沿既定规则优化？",
    },
    {
        "name": "尺度依赖个体化",
        "name_en": "scale-dependent-individuation",
        "triggers": {"scale", "boundary", "multiscale", "collective", "individuality", "observer_boundary"},
        "question": "在细胞、个体、群体、生态或数字组织的不同尺度上，什么因果闭包使其成为可追踪的个体？",
    },
    {
        "name": "观察者参与与反向塑形",
        "name_en": "observer-participation",
        "triggers": {"observer_relative", "mutual_transformation", "subjectivity", "interaction", "push_back"},
        "question": "被评估对象是否会改变观察者的分类、测量和目的，使定义本身成为互动的一部分？",
    },
    {
        "name": "基质—约束可迁移性",
        "name_en": "substrate-constraint-portability",
        "triggers": {"substrate_neutral", "digital_life", "constraint_closure", "embodiment", "migration"},
        "question": "维持身份和功能的约束能否跨碳基、硅基、化学、机器人或虚拟基质迁移？",
    },
    {
        "name": "可生存规范内生性",
        "name_en": "endogenous-viability-normativity",
        "triggers": {"homeostasis", "self_maintenance", "intrinsic_goal", "agency", "viability", "healing"},
        "question": "何种状态对系统而言是由其自身组织产生的可接受或不可接受状态，而非外部评价者强加？",
    },
    {
        "name": "概念投影损失",
        "name_en": "concept-projection-loss",
        "triggers": {"definition_tool", "morphospace", "continuum", "context", "pluralism", "semantic_loss"},
        "question": "把高维语义场压缩成一个词或定义时，哪些关系、尺度、冲突和可能性被系统性丢失？",
    },
]


class ConceptEscapeEngine:
    def __init__(self, mesh: SemanticMesh) -> None:
        self.mesh = mesh

    def propose(self, max_candidates: int = 8) -> List[Dict[str, object]]:
        tag_observers: Dict[str, set[str]] = defaultdict(set)
        tag_types: Dict[str, set[str]] = defaultdict(set)
        tag_stance: Dict[str, List[float]] = defaultdict(list)
        for observer, view in self.mesh.views.items():
            for atom in view.atoms:
                for tag in atom.tags:
                    tag_observers[tag].add(observer)
                    for typ, weight in atom.type_weights.items():
                        if weight >= 0.15:
                            tag_types[tag].add(typ)
                for tag, value in atom.stance.items():
                    tag_stance[tag].append(value)

        candidates: List[Dict[str, object]] = []
        total_obs = max(1, len(self.mesh.views))
        for spec in DIMENSION_CATALOG:
            hits = sorted(spec["triggers"] & set(tag_observers))
            if not hits:
                continue
            support_observers = set()
            type_set = set()
            disagreement = 0.0
            for tag in hits:
                support_observers |= tag_observers[tag]
                type_set |= tag_types[tag]
                vals = tag_stance.get(tag, [])
                if vals:
                    mean = sum(vals) / len(vals)
                    disagreement += sum((x - mean) ** 2 for x in vals) / len(vals)
            support = len(support_observers) / total_obs
            cross_type = len(type_set) / 5.0
            tension = min(1.0, disagreement / max(1, len(hits)))
            escape_need = min(1.0, 0.45 * support + 0.35 * cross_type + 0.20 * tension)
            candidates.append({
                "candidate_dimension": spec["name"],
                "candidate_dimension_en": spec["name_en"],
                "trigger_features": hits,
                "observer_support": sorted(support_observers),
                "support": round(support, 6),
                "cross_DIKWP_span": sorted(type_set),
                "tension": round(tension, 6),
                "escape_need": round(escape_need, 6),
                "operational_question": spec["question"],
                "status": "candidate-axis-not-a-new-definition",
            })
        candidates.sort(key=lambda x: (-x["escape_need"], -x["support"], x["candidate_dimension"]))
        return candidates[:max_candidates]
