from __future__ import annotations

from pathlib import Path
import json
import webbrowser

import typer
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table

from .analyzer import analyze_codebase
from .report import generate_markdown
from .visualizer import render_html

app = typer.Typer(add_completion=False, help="FunctionFlow - interactive Python call-graph explorer")
console = Console()


@app.command()
def report(
    path: Path = typer.Argument(..., exists=True, file_okay=True, dir_okay=True, readable=True),
    focus: str | None = typer.Option(None, "--focus", "-f", help="Filter functions before summarizing"),
    output: Path | None = typer.Option(None, "--output", "-o", help="Write Markdown report to this file"),
) -> None:
    """Generate a Markdown architecture digest."""
    graph = analyze_codebase(path, focus=focus)
    markdown = generate_markdown(graph)
    if output:
        output.write_text(markdown, encoding="utf-8")
        console.print(f"[green]Report written to {output}[/green]")
    else:
        console.print(Markdown(markdown))


@app.command()
def map(
    path: Path = typer.Argument(..., exists=True, file_okay=True, dir_okay=True, readable=True),
    focus: str | None = typer.Option(None, "--focus", "-f", help="Only keep nodes whose name/doc/path contains this text"),
    html: Path | None = typer.Option(None, "--html", help="Write an interactive HTML graph"),
    json_output: Path | None = typer.Option(None, "--json", help="Write the raw graph payload to JSON"),
    open_html: bool = typer.Option(False, "--open", help="Open the generated HTML in the browser"),
    no_physics: bool = typer.Option(False, "--no-physics", help="Disable force-directed animation"),
) -> None:
    """Parse a Python project and emit insights + interactive graphs."""
    console.print(f"[bold cyan]Scanning {path}[/bold cyan]")
    graph = analyze_codebase(path, focus=focus)
    summary = graph["summary"]

    table = Table(title="FunctionFlow Summary", show_lines=True)
    table.add_column("Metric", justify="right")
    table.add_column("Value", justify="left")
    for key, value in summary.items():
        table.add_row(key.replace("_", " ").title(), str(value))
    console.print(table)

    insights: dict | None = None
    if html:
        console.print(f"[green]Rendering interactive graph -> {html}[/green]")
        insights = render_html(graph, html, physics=not no_physics)
        if open_html:
            webbrowser.open(Path(insights["output"]).as_uri())

    if json_output:
        json_output.write_text(json.dumps(graph, indent=2), encoding="utf-8")
        console.print(f"[green]Wrote JSON -> {json_output}[/green]")

    if insights:
        hotspots = insights.get("hotspots", [])
        if hotspots:
            panel_lines = [
                f"[bold]{item['name']}[/bold] · betweenness {item['betweenness']} · {item['file']}"
                for item in hotspots
            ]
            console.print(Panel("\n".join(panel_lines), title="Top connectors"))


if __name__ == "__main__":
    app()

