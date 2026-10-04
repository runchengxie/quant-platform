from __future__ import annotations

import ast
import re
import tomllib
from pathlib import Path

FORBIDDEN_IMPORT_ROOTS = {"quant_market_data_platform", "tushare", "rqdatac"}
FORBIDDEN_DISTRIBUTIONS = {"quant-market-data-platform", "tushare", "rqdatac"}


def test_ticknet_does_not_import_market_data_platform_or_provider_sdks() -> None:
    root = Path(__file__).resolve().parents[1]
    source_root = root / "packages/microstructure/src/ticknet"

    violations: list[str] = []
    for path in sorted(source_root.rglob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                names = [alias.name for alias in node.names]
            elif isinstance(node, ast.ImportFrom) and node.module:
                names = [node.module]
            else:
                continue
            for name in names:
                if name.split(".", maxsplit=1)[0] in FORBIDDEN_IMPORT_ROOTS:
                    violations.append(f"{path.relative_to(root)}:{node.lineno}: {name}")

    assert not violations, "Forbidden TickNet imports:\n" + "\n".join(violations)


def test_market_data_platform_and_provider_sdks_are_not_runtime_dependencies() -> None:
    root = Path(__file__).resolve().parents[1]
    project = tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8"))["project"]
    dependencies = project.get("dependencies", [])
    names = {re.split(r"[<=>!~;\[]", item, maxsplit=1)[0].lower() for item in dependencies}

    assert not (names & FORBIDDEN_DISTRIBUTIONS), sorted(names & FORBIDDEN_DISTRIBUTIONS)


def test_data_boundary_docs_match_the_enforced_contract() -> None:
    root = Path(__file__).resolve().parents[1]
    pages = (
        "docs/microstructure/data-boundary.en.md",
        "docs/microstructure/data-boundary.md",
    )
    for relative in pages:
        content = (root / relative).read_text(encoding="utf-8")
        assert "test_microstructure_data_boundary.py" in content
        assert "canonical_adapter" in content
