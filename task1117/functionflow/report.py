from __future__ import annotations

from collections import Counter, defaultdict
from textwrap import dedent
from typing import Dict, List

import networkx as nx

from .visualizer import _build_graph, _heat


def _module_bucket(node_id: str) -> str:
    parts = node_id.split(".")
    if len(parts) <= 2:
        return parts[0]
    return ".".join(parts[:2])


def _format_table(rows: List[tuple[str, str]], headers: tuple[str, str]) -> str:
    lines = [f"| {headers[0]} | {headers[1]} |", f"| --- | --- |"]
    for left, right in rows:
        lines.append(f"| {left} | {right} |")
    return "\n".join(lines)


def _docstring_coverage(nodes: List[Dict[str, object]]) -> tuple[int, int]:
    documented = sum(1 for node in nodes if node.get("doc"))
    return documented, len(nodes)


def generate_markdown(graph_data: Dict[str, List[Dict[str, object]]]) -> str:
    """Produce a rich Markdown report from raw analyzer output."""
    g = _build_graph(graph_data)
    betweenness = _heat(nx.betweenness_centrality(g)) if g else {}
    out_degree = dict(g.out_degree()) if g else {}
    in_degree = dict(g.in_degree()) if g else {}

    nodes = list(graph_data["nodes"])
    edges = list(graph_data["edges"])

    documented, total = _docstring_coverage(nodes)
    module_counter = Counter(_module_bucket(node["id"]) for node in nodes)

    top_hotspots = sorted(
        ((node, betweenness.get(node["id"], 0.0)) for node in nodes),
        key=lambda pair: pair[1],
        reverse=True,
    )[:5]
    hotspot_rows = [
        (
            node["id"],
            f"{score:.3f} · {node['path']}:{node['lineno']}",
        )
        for node, score in top_hotspots
    ]

    fan_in = sorted(in_degree.items(), key=lambda kv: kv[1], reverse=True)[:5]
    fan_out = sorted(out_degree.items(), key=lambda kv: kv[1], reverse=True)[:5]
    fan_in_rows = [(node, str(value)) for node, value in fan_in]
    fan_out_rows = [(node, str(value)) for node, value in fan_out]

    module_rows = [(module, str(count)) for module, count in module_counter.most_common(5)]

    report = dedent(
        f"""
        # FunctionFlow Report

        - Files scanned: {graph_data['summary']['files_scanned']}
        - Functions detected: {graph_data['summary']['functions']}
        - Calls tracked: {graph_data['summary']['calls']}
        - Docstring coverage: {documented}/{total} ({(documented/total*100 if total else 0):.1f}%)

        ## Knowledge Hotspots
        {_format_table(hotspot_rows, ("Function", "Betweenness · Location"))}

        ## Fan-in Champs (most callers)
        {_format_table(fan_in_rows, ("Function", "Incoming edges"))}

        ## Fan-out Champs (most callees)
        {_format_table(fan_out_rows, ("Function", "Outgoing edges"))}

        ## Busiest Modules
        {_format_table(module_rows, ("Module", "Functions"))}
        """
    ).strip()

    return report

