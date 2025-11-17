from pathlib import Path

from functionflow.analyzer import analyze_codebase


FIXTURE = Path(__file__).parent.parent / "samples" / "spaceship"


def test_analyze_codebase_counts_functions_and_calls():
    graph = analyze_codebase(FIXTURE)
    summary = graph["summary"]
    assert summary["files_scanned"] == 2
    assert summary["functions"] >= 8
    assert summary["calls"] >= 6


def test_focus_filter_limits_results():
    graph = analyze_codebase(FIXTURE, focus="ignite")
    assert graph["summary"]["functions"] == 1
    assert all("ignite" in node["id"] for node in graph["nodes"])

