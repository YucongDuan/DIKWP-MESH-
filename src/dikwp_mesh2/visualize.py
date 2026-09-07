from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Iterable, List, Mapping, Sequence

import matplotlib.pyplot as plt
from matplotlib import rcParams

rcParams["font.sans-serif"] = ["Noto Sans CJK JP", "DejaVu Sans"]
rcParams["axes.unicode_minus"] = False
import networkx as nx
import numpy as np
import pandas as pd

from .mesh import SemanticMesh
from .models import DIKWPType, SemanticBundleResult
from .operators import TransformRegistry


def plot_dikwp_network(output: Path) -> None:
    registry = TransformRegistry()
    g = nx.MultiDiGraph()
    for t in DIKWPType.ordered():
        g.add_node(t.value)
    for op in registry.all():
        g.add_edge(op.source.value, op.target.value)
    pos = nx.circular_layout(g)
    fig = plt.figure(figsize=(8, 8))
    ax = fig.add_subplot(111)
    nx.draw_networkx_nodes(g, pos, node_size=2600, ax=ax)
    nx.draw_networkx_labels(g, pos, font_size=18, font_weight="bold", ax=ax)
    curved_edges = []
    self_edges = []
    for u, v in g.edges():
        if u == v:
            self_edges.append((u, v))
        else:
            curved_edges.append((u, v))
    nx.draw_networkx_edges(g, pos, edgelist=curved_edges, arrows=True, arrowstyle="-|>", arrowsize=14, connectionstyle="arc3,rad=0.12", width=1.0, alpha=0.55, ax=ax)
    nx.draw_networkx_edges(g, pos, edgelist=self_edges, arrows=True, arrowstyle="-|>", arrowsize=14, connectionstyle="arc3,rad=0.45", width=1.0, alpha=0.55, ax=ax)
    ax.set_title("DIKWP as an all-to-all directed semantic network (25 primitive operators)")
    ax.axis("off")
    fig.tight_layout()
    fig.savefig(output, dpi=180, bbox_inches="tight")
    plt.close(fig)


def plot_observer_similarity(mesh: SemanticMesh, output: Path) -> None:
    sim = mesh.observer_similarity()
    observers = sorted(sim)
    arr = np.array([[sim[a][b] for b in observers] for a in observers])
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111)
    im = ax.imshow(arr, vmin=0, vmax=1)
    ax.set_xticks(range(len(observers)), observers, rotation=60, ha="right", fontsize=8)
    ax.set_yticks(range(len(observers)), observers, fontsize=8)
    for i in range(len(observers)):
        for j in range(len(observers)):
            ax.text(j, i, f"{arr[i,j]:.2f}", ha="center", va="center", fontsize=6)
    ax.set_title("Cross-observer semantic similarity")
    fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    fig.tight_layout()
    fig.savefig(output, dpi=180, bbox_inches="tight")
    plt.close(fig)


def plot_transformation_usage(result: SemanticBundleResult, output: Path) -> None:
    types = [t.value for t in DIKWPType.ordered()]
    arr = np.array([[result.transformation_usage[f"{a}->{b}"] for b in types] for a in types])
    fig = plt.figure(figsize=(7, 6))
    ax = fig.add_subplot(111)
    im = ax.imshow(arr)
    ax.set_xticks(range(5), types)
    ax.set_yticks(range(5), types)
    ax.set_xlabel("Target semantic resource type")
    ax.set_ylabel("Source semantic resource type")
    for i in range(5):
        for j in range(5):
            ax.text(j, i, str(int(arr[i, j])), ha="center", va="center", fontsize=10)
    ax.set_title("Observed DIKWP×DIKWP transformation usage")
    fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    fig.tight_layout()
    fig.savefig(output, dpi=180, bbox_inches="tight")
    plt.close(fig)


def plot_semantic_mesh(mesh: SemanticMesh, output: Path, max_nodes: int = 55) -> None:
    atoms = mesh.atoms()[:max_nodes]
    atom_ids = {a.id for a in atoms}
    g = nx.DiGraph()
    for atom in atoms:
        g.add_node(atom.id, label=atom.label[:18], typ=atom.dominant_type.value, observer=atom.observer)
    for u, v, data in mesh.graph.edges(data=True):
        if u in atom_ids and v in atom_ids and data.get("kind") == "transformation":
            g.add_edge(u, v)
    if g.number_of_edges() == 0:
        # Add alignment edges for visualization only.
        for edge in mesh.alignment_edges(min_similarity=0.25)[:80]:
            if edge.atom_a in atom_ids and edge.atom_b in atom_ids:
                g.add_edge(edge.atom_a, edge.atom_b)
    pos = nx.spring_layout(g, seed=42, k=0.62)
    fig = plt.figure(figsize=(13, 10))
    ax = fig.add_subplot(111)
    node_sizes = [620 + 700 * max(mesh.atom(n).type_weights.values()) for n in g.nodes]
    nx.draw_networkx_nodes(g, pos, node_size=node_sizes, alpha=0.85, ax=ax)
    nx.draw_networkx_edges(g, pos, arrows=True, arrowsize=10, alpha=0.25, width=0.8, ax=ax)
    labels = {n: f"{mesh.atom(n).dominant_type.value}:{mesh.atom(n).label[:15]}" for n in g.nodes}
    nx.draw_networkx_labels(g, pos, labels=labels, font_size=6, ax=ax)
    ax.set_title(f"Multi-observer semantic mesh for concept: {mesh.concept}")
    ax.axis("off")
    fig.tight_layout()
    fig.savefig(output, dpi=180, bbox_inches="tight")
    plt.close(fig)
