# FunctionFlow

Interactive Python call-graph explorer that turns any codebase into an explorable network. Built for developers who want instant architectural intuition without spinning up heavyweight IDE tooling.

> **TL;DR** `pip install -e . && functionflow map src --html graph.html --open`

## Why it deserves a ⭐

- **Practical:** understand onboarding-sized codebases in minutes, not days.
- **Frontier:** combines static analysis, lightweight complexity hints, graph centrality, and WebGL rendering for a fresh view of legacy Python.
- **Correct:** pure-AST parsing means zero runtime side effects or imports.
- **Interesting:** every run surfaces "hotspot" functions that glue your system together. Perfect fuel for refactors, docs, and architecture decks.

## Features

- 📦 Works on single files or entire repos (including nested packages).
- 🔍 `--focus foo` filters by name/doc/path, letting you zoom into specific subsystems.
- 🌐 Generates a PyVis-powered HTML map with physics, hover tooltips, and weighted edges.
- 🧾 `functionflow report` emits a ready-to-commit Markdown architecture digest.
- 🔥 Betweenness-centrality highlights the functions that control knowledge flow.
- 📊 Rich console summary plus optional JSON export for automation.
- ⚙️ Complexity hints tell you which functions are doing too much.

## Quickstart

```bash
git clone https://github.com/OliverZ-dot/FunctionFlow
cd functionflow
python -m venv .venv && source .venv/bin/activate  # PowerShell: .\.venv\Scripts\Activate.ps1
pip install -e .
functionflow map path/to/project --html callgraph.html --open
```

### CLI Examples

```bash
# Analyze only functions containing "payment" in their name/doc/path
functionflow map ./services --focus payment --html payments.html

# Export raw graph data for downstream tooling
functionflow map . --json graph.json

# Ship a Markdown report instead of HTML
functionflow report ./services --focus api --output api-hotspots.md
```

### Smoke-test on the bundled sample

```bash
functionflow map samples/spaceship --html spaceship.html --open
functionflow report samples/spaceship
```

## Internals

1. `functionflow.analyzer` walks every AST node without executing user code.
2. We annotate each function with type (method, async, etc.), docstring snippet, and a rough complexity score (count of meaningful statements).
3. Calls are tracked with file + line origins, then piped into NetworkX.
4. Betweenness centrality + indegree become the "heat" that sizes nodes/edges.
5. PyVis renders a gorgeous, interactive map ready for browsers and presentations.

## Roadmap

- [ ] Export to Mermaid and Graphviz for CI-friendly artifacts.
- [ ] Cache graphs for instant re-runs during development.
- [ ] VS Code extension that embeds the FunctionFlow HTML viewer.
- [ ] Live-reload server that watches your repo for changes.

## Contributing

Issues and PRs welcome! Start with `python -m pytest` (tests coming soon) and keep docs up to date.

## License

MIT © FunctionFlow Contributors
