from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Set, Tuple
import ast
import textwrap


SKIP_DIRS = {"__pycache__", ".git", ".venv", "venv", "env", ".mypy_cache"}


@dataclass(slots=True)
class FunctionNode:
    qualname: str
    filepath: Path
    lineno: int
    fn_type: str
    docstring: str
    complexity_hint: int


@dataclass(slots=True)
class CallEdge:
    caller: str
    callee: str
    filepath: Path
    lineno: int


class FunctionCallGraphBuilder(ast.NodeVisitor):
    def __init__(self, module_name: str, file_path: Path) -> None:
        self.module_name = module_name
        self.file_path = file_path
        self.current_stack: List[Tuple[str, str]] = []  # (qualname, fn_type)
        self.functions: Dict[str, FunctionNode] = {}
        self.edges: List[CallEdge] = []

    # ---- helpers -----------------------------------------------------------------
    def _qualname_for(self, name: str, fn_type: str) -> str:
        scope = [self.module_name] + [q.split(".")[-1] for q, _ in self.current_stack]
        scope.append(name)
        qualname = ".".join(filter(None, scope))
        return qualname

    def _docstring(self, node: ast.AST) -> str:
        doc = ast.get_docstring(node) or ""
        if doc:
            doc = textwrap.dedent(doc).strip().splitlines()[0][:200]
        return doc

    def _complexity_hint(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> int:
        """Rough heuristic: number of statements at top level inside the body."""
        return sum(1 for stmt in node.body if not isinstance(stmt, (ast.Expr, ast.Pass)))

    def _record_function(self, node: ast.FunctionDef | ast.AsyncFunctionDef, kind: str) -> None:
        qualname = self._qualname_for(node.name, kind)
        self.current_stack.append((qualname, kind))
        self.functions[qualname] = FunctionNode(
            qualname=qualname,
            filepath=self.file_path,
            lineno=node.lineno,
            fn_type=kind,
            docstring=self._docstring(node),
            complexity_hint=self._complexity_hint(node),
        )
        self.generic_visit(node)
        self.current_stack.pop()

    def _record_call(self, node: ast.Call) -> None:
        if not self.current_stack:
            return
        caller = self.current_stack[-1][0]
        target = self._resolve_callable_name(node.func)
        if not target:
            return
        self.edges.append(
            CallEdge(
                caller=caller,
                callee=target,
                filepath=self.file_path,
                lineno=node.lineno,
            )
        )

    def _resolve_callable_name(self, node: ast.AST) -> Optional[str]:
        if isinstance(node, ast.Name):
            return node.id
        if isinstance(node, ast.Attribute):
            parts: List[str] = []
            current: Optional[ast.AST] = node
            while isinstance(current, ast.Attribute):
                parts.append(current.attr)
                current = current.value
            if isinstance(current, ast.Name):
                parts.append(current.id)
            parts.reverse()
            return ".".join(parts)
        if isinstance(node, ast.Call):
            # Handles decorator factories like decorator()(...)
            return self._resolve_callable_name(node.func)
        return None

    # ---- visitor overrides --------------------------------------------------------
    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:  # type: ignore[override]
        kind = "method" if self.current_stack and self.current_stack[-1][1] == "class" else "function"
        self._record_function(node, kind)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:  # type: ignore[override]
        kind = "async"
        if self.current_stack and self.current_stack[-1][1] == "class":
            kind = "async-method"
        self._record_function(node, kind)

    def visit_ClassDef(self, node: ast.ClassDef) -> None:  # type: ignore[override]
        qualname = self._qualname_for(node.name, "class")
        self.current_stack.append((qualname, "class"))
        self.generic_visit(node)
        self.current_stack.pop()

    def visit_Call(self, node: ast.Call) -> None:  # type: ignore[override]
        self._record_call(node)
        self.generic_visit(node)


def _python_files(root: Path) -> Iterable[Path]:
    if root.is_file():
        yield root
        return
    for path in root.rglob("*.py"):
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        yield path


def _module_name(project_root: Path, file_path: Path) -> str:
    rel = file_path.relative_to(project_root)
    parts = list(rel.with_suffix("").parts)
    return ".".join(parts)


def analyze_codebase(
    root: Path,
    *,
    focus: Optional[str] = None,
) -> Dict[str, object]:
    root = root.resolve()
    all_functions: Dict[str, FunctionNode] = {}
    edges: List[CallEdge] = []
    python_files = list(_python_files(root))
    for file_path in python_files:
        try:
            source = file_path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        module_name = _module_name(root, file_path)
        builder = FunctionCallGraphBuilder(module_name, file_path)
        try:
            tree = ast.parse(source)
        except SyntaxError:
            continue
        builder.visit(tree)
        all_functions.update(builder.functions)
        edges.extend(builder.edges)

    if focus:
        focus_lower = focus.lower()
        filtered_nodes = {
            name: node
            for name, node in all_functions.items()
            if focus_lower in name.lower()
            or focus_lower in node.docstring.lower()
            or focus_lower in str(node.filepath).lower()
        }
        allowed = set(filtered_nodes)
        filtered_edges = [edge for edge in edges if edge.caller in allowed]
    else:
        filtered_nodes = all_functions
        filtered_edges = edges

    summary = {
        "files_scanned": len(python_files),
        "functions": len(filtered_nodes),
        "calls": len(filtered_edges),
    }

    nodes_payload = [
        {
            "id": node.qualname,
            "path": str(node.filepath),
            "lineno": node.lineno,
            "type": node.fn_type,
            "doc": node.docstring,
            "complexity_hint": node.complexity_hint,
        }
        for node in filtered_nodes.values()
    ]
    edges_payload = [
        {
            "source": edge.caller,
            "target": edge.callee,
            "path": str(edge.filepath),
            "lineno": edge.lineno,
        }
        for edge in filtered_edges
    ]

    return {
        "nodes": nodes_payload,
        "edges": edges_payload,
        "summary": summary,
    }

