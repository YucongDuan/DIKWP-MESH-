from __future__ import annotations

if __package__:
    from ._ui_presentation import localize_html as _ui_localize_html
else:
    from _ui_presentation import localize_html as _ui_localize_html


import html
import json
from pathlib import Path
from typing import Dict, Iterable, List, Mapping, Sequence

from jinja2 import Template

from .mesh import SemanticMesh
from .models import SemanticBundleResult


TEMPLATE = Template(r'''<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>DIKWP-MESH² Dashboard</title>
<style>
:root { --bg:#f5f7fb; --card:#fff; --ink:#1a2333; --muted:#5f6b7a; --line:#dbe2ec; --accent:#263c68; --warn:#8b4d00; --bad:#8a1c1c; }
*{box-sizing:border-box} body{margin:0;background:var(--bg);color:var(--ink);font-family:Arial,"Microsoft YaHei",sans-serif;line-height:1.55}
header{background:linear-gradient(120deg,#172642,#314f85);color:white;padding:34px 6vw 26px} h1{margin:0 0 8px;font-size:32px} header p{max-width:980px;margin:0;color:#dce7fb}
main{max-width:1250px;margin:22px auto;padding:0 20px 50px}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:14px}.card{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:16px;box-shadow:0 2px 10px rgba(20,35,60,.05)}.metric{font-size:28px;font-weight:700;color:var(--accent)}.label{font-size:13px;color:var(--muted)}h2{margin-top:32px;border-bottom:2px solid var(--line);padding-bottom:7px}h3{margin-bottom:7px}.imgcard img{width:100%;height:auto;border:1px solid var(--line);border-radius:9px}.cols{display:grid;grid-template-columns:1fr 1fr;gap:16px}@media(max-width:850px){.cols{grid-template-columns:1fr}}
table{border-collapse:collapse;width:100%;font-size:13px}th,td{padding:8px 9px;border-bottom:1px solid var(--line);vertical-align:top}th{text-align:left;background:#eef2f8}.pill{display:inline-block;padding:2px 7px;margin:2px;border-radius:12px;background:#e8eef8;font-size:12px}.warn{color:var(--warn)}.bad{color:var(--bad)}details{background:white;border:1px solid var(--line);border-radius:9px;margin:8px 0;padding:10px 12px}summary{cursor:pointer;font-weight:700}.note{color:var(--muted);font-size:13px}.footer{margin-top:35px;color:var(--muted);font-size:12px}
</style>
</head>
<body>
<header><h1>DIKWP-MESH²</h1><p>网状语义生成、DIKWP×DIKWP多维转化、跨主体概念解缚与共知演化系统。D/I/K/W/P为同等语义资源类型；概念只是特定观察者、语境和目的下对高维语义场的投影。</p></header>
<main>
<section class="grid">
<div class="card"><div class="metric">{{ result.observer_count }}</div><div class="label">观察者 / 局部语义截面</div></div>
<div class="card"><div class="metric">{{ result.atom_count }}</div><div class="label">语义原子</div></div>
<div class="card"><div class="metric">{{ '%.3f'|format(result.metrics.subjectivity_escape_score) }}</div><div class="label">跨主体语义超越分数（非客观真理分数）</div></div>
<div class="card"><div class="metric">{{ '%.3f'|format(result.metrics.concept_escape_readiness) }}</div><div class="label">概念空间逃逸准备度</div></div>
<div class="card"><div class="metric">{{ result.metrics.directed_cycle_count|int }}</div><div class="label">语义转化有向环</div></div>
<div class="card"><div class="metric">{{ '%.0f%%'|format(result.metrics.transformation_type_coverage*100) }}</div><div class="label">25类变换覆盖率</div></div>
</section>

<h2>1. 网状结构与当前语义场</h2>
<div class="cols"><div class="card imgcard"><img src="dikwp_network.png" alt="DIKWP all-to-all directed network" /></div><div class="card imgcard"><img src="semantic_mesh.png" alt="multi-observer semantic mesh" /></div></div>

<h2>2. 跨观察者对齐与变换使用</h2>
<div class="cols"><div class="card imgcard"><img src="observer_similarity.png" alt="observer similarity matrix" /></div><div class="card imgcard"><img src="transformation_usage.png" alt="DIKWP transformation usage heatmap" /></div></div>

<h2>3. 可拼接的跨主体不变量核</h2>
<div class="card"><table><thead><tr><th>语义特征</th><th>支持度</th><th>DIKWP分布</th><th>观察者</th></tr></thead><tbody>
{% for item in result.invariant_kernel[:15] %}<tr><td><b>{{ item.semantic_feature }}</b></td><td>{{ '%.2f'|format(item.support) }}</td><td>{% for k,v in item.type_distribution.items() %}<span class="pill">{{k}} {{'%.2f'|format(v)}}</span>{% endfor %}</td><td>{{ item.observers|join('、') }}</td></tr>{% endfor %}
</tbody></table></div>

<h2>4. 不可被平均掉的冲突与阻碍</h2>
<div class="card"><p><b>局部到全局状态：</b>{{ result.gluing.global_section_status }}；<b>阻碍分数：</b>{{ '%.3f'|format(result.gluing.obstruction_score) }}</p><p class="note">{{ result.gluing.interpretation }}</p>
{% for item in result.conflicts[:12] %}<details><summary>{{ item.semantic_feature }} — 分歧 {{ '%.3f'|format(item.disagreement) }}</summary><p>支持度：{{ '%.2f'|format(item.support) }}；正向：{{ item.positive_count }}；负向：{{ item.negative_count }}</p><p>{{ item.example_labels|join('；') }}</p></details>{% endfor %}
</div>

<h2>5. 概念解缚：建议新增的语义坐标</h2>
<div class="grid">{% for item in result.escape_candidates %}<div class="card"><h3>{{ item.candidate_dimension }}</h3><div class="label">{{ item.candidate_dimension_en }}</div><p>{{ item.operational_question }}</p><p><b>逃逸必要度：</b>{{ '%.3f'|format(item.escape_need) }}</p><p>{% for t in item.cross_DIKWP_span %}<span class="pill">{{ t }}</span>{% endfor %}</p><p class="note">触发：{{ item.trigger_features|join('、') }}</p></div>{% endfor %}</div>

<h2>6. 层级泄漏审计</h2>
<div class="card"><p><b>判定：</b><span class="{{ 'bad' if result.hierarchy_audit.verdict == 'REJECT_AS_HIERARCHICAL' else 'warn' }}">{{ result.hierarchy_audit.verdict }}</span>；层级泄漏分数 {{ '%.3f'|format(result.hierarchy_audit.hierarchy_leakage_score) }}</p>
{% for f in result.hierarchy_audit.findings %}<details><summary>[{{ f.severity }}] {{ f.code }}</summary><p>{{ f.message }}</p></details>{% endfor %}
</div>

<h2>7. 高阶算子演化提案</h2><div class="grid">{% for item in result.meta_operator_proposals %}<div class="card"><h3>{{ item.name }}</h3><p><b>路径：</b>{{ item.path|join(' → ') }}</p><p>{{ item.purpose }}</p><p class="note">验证：{{ item.validation }}</p><p class="note">回滚：{{ item.rollback }}</p></div>{% endfor %}</div>

<h2>8. 任务索引语义合同</h2><div class="grid">{% for item in result.semantic_contracts %}<div class="card"><h3>{{ item.contract }}</h3><p>{{ item.use }}</p><p><b>允许输出：</b>{{ item.decision_output|join('、') }}</p><p class="note"><b>禁止：</b>{{ item.prohibited_output }}</p></div>{% endfor %}</div>

<h2>9. 解释边界</h2><div class="card"><p>该仪表盘不生成“生命的唯一最终定义”。它输出跨观察者不变量、局部语义分支、不可拼接冲突、未翻译残差、任务索引语义合同以及值得新增的语义坐标。所谓“跨主体超越”是对单一观察者垄断的降低，不等于获得无条件、无语境的绝对客观真理。</p></div>
<div class="footer">Generated by DIKWP-MESH² MVP. Offline artifact; no external scripts or network calls.</div>
</main></body></html>''')


def render_dashboard(result: SemanticBundleResult, mesh: SemanticMesh, output: Path) -> None:
    output.write_text(_ui_localize_html(TEMPLATE.render(result=result.to_dict())), encoding="utf-8")
