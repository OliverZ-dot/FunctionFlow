"""
FunctionFlow: interactive Python call-graph explorer.

This package exposes a small public surface:
- `analyze_codebase` returns the raw graph + metadata.
- `render_html` materializes the interactive graph experience.
- `app` (Typer) powers the CLI entrypoint.
"""

from .analyzer import analyze_codebase
from .visualizer import render_html
from .cli import app

__all__ = ["analyze_codebase", "render_html", "app"]

