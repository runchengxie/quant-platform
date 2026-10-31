"""Reject direct old namespace imports in first-party production source."""

from __future__ import annotations

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def _dynamic_name(node: ast.AST) -> str:
    if not isinstance(node, ast.Call) or not node.args:
        return ""
    function = node.func
    name = (
        function.id
        if isinstance(function, ast.Name)
        else function.attr
        if isinstance(function, ast.Attribute)
        else ""
    )
    if name not in {"import_module", "__import__"}:
        return ""
    value = node.args[0]
    if isinstance(value, ast.JoinedStr) and value.values:
        value = value.values[0]
    return value.value if isinstance(value, ast.Constant) and isinstance(value.value, str) else ""


def violations(root: Path = ROOT) -> list[str]:
    problems = []
    for path in (root / "packages").rglob("*.py"):
        if "portfolio_backtester" in path.parts:
            continue  # Explicit compatibility aliases are the only permitted surface.
        for node in ast.walk(ast.parse(path.read_text())):
            names = (
                [node.module or ""]
                if isinstance(node, ast.ImportFrom)
                else [alias.name for alias in node.names]
                if isinstance(node, ast.Import)
                else []
            )
            names.append(_dynamic_name(node))
            if any(
                name == "portfolio_backtester" or name.startswith("portfolio_backtester.")
                for name in names
            ):
                problems.append(f"{path.relative_to(root)}:{getattr(node, 'lineno', 0)}")
    return problems


if __name__ == "__main__":
    found = violations()
    if found:
        raise SystemExit(
            "Use public quant_platform owners instead of legacy imports:\n" + "\n".join(found)
        )
    print("No first-party production imports of the old namespace")
