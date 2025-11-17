from __future__ import annotations

from pathlib import Path
from typing import Dict, Iterable, List, Tuple

import json
import math

import networkx as nx
from pyvis.network import Network


COLOR_BY_TYPE = {
    "function": "#38bdf8",
    "async": "#f97316",
    "method": "#34d399",
    "async-method": "#facc15",
    "class": "#c084fc",
}


def _heat(values: Dict[str, float]) -> Dict[str, float]:
    if not values:
        return {}
    min_v = min(values.values())
    max_v = max(values.values())
    if math.isclose(min_v, max_v):
        return {k: 0.5 for k in values}
    return {k: (v - min_v) / (max_v - min_v) for k, v in values.items()}


def _build_graph(graph_data: Dict[str, List[Dict[str, object]]]) -> nx.DiGraph:
    g = nx.DiGraph()
    for node in graph_data["nodes"]:
        g.add_node(node["id"], **node)
    for edge in graph_data["edges"]:
        g.add_edge(edge["source"], edge["target"], **edge)
    return g


def render_html(
    graph_data: Dict[str, List[Dict[str, object]]],
    output_path: Path,
    *,
    physics: bool = True,
) -> Dict[str, object]:
    output_path = output_path.with_suffix(".html")
    g = _build_graph(graph_data)
    centrality = _heat(nx.betweenness_centrality(g)) if g else {}
    indegree = _heat(dict(g.in_degree())) if g else {}

    net = Network(
        height="720px",
        width="100%",
        bgcolor="#020617",
        font_color="#e2e8f0",
        directed=True,
        notebook=False,
    )
    net.toggle_physics(physics)
    net.barnes_hut(gravity=-20000, central_gravity=0.1, spring_length=180, spring_strength=0.02)

    for node_id, data in g.nodes(data=True):
        fn_type = data.get("type", "function")
        color = COLOR_BY_TYPE.get(fn_type, "#f472b6")
        label = node_id.split(".")[-1]
        doc = data.get("doc", "") or "No docstring"
        complexity = data.get("complexity_hint", 0)
        tooltip = (
            f"<b>{node_id}</b><br>"
            f"{data.get('path')}:{data.get('lineno')}<br>"
            f"{doc}<br>"
            f"Complexity hint: {complexity}"
        )
        size = 12 + 30 * centrality.get(node_id, 0.3)
        net.add_node(
            node_id,
            label=label,
            title=tooltip,
            color=color,
            value=size,
            shadow=True,
        )

    for src, dst, data in g.edges(data=True):
        tooltip = f"{data.get('path')}:{data.get('lineno')}"
        width = 1.2 + 4 * indegree.get(dst, 0.2)
        net.add_edge(src, dst, title=tooltip, width=width, color="#475569")

    net.show(str(output_path))

    # textual insights
    top_connectors = sorted(centrality.items(), key=lambda kv: kv[1], reverse=True)[:5]
    hotspots = [
        {"name": name, "betweenness": round(score, 4), "file": g.nodes[name].get("path")}
        for name, score in top_connectors
    ]

    return {
        "output": str(output_path),
        "hotspots": hotspots,
        "stats": {
            "nodes": g.number_of_nodes(),
            "edges": g.number_of_edges(),
        },
    }

