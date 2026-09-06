from __future__ import annotations

import importlib.util
import tomllib
from pathlib import Path

_MODULE_PATH = Path(__file__).parents[2] / "scripts/dev/history_publication_audit.py"
_SPEC = importlib.util.spec_from_file_location("history_publication_audit", _MODULE_PATH)
assert _SPEC is not None and _SPEC.loader is not None
_MODULE = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_MODULE)
scan_text = _MODULE.scan_text
_EXPORTER_PATH = Path(__file__).parents[2] / "scripts/dev/public_surface_export.py"
_EXPORTER_SPEC = importlib.util.spec_from_file_location("public_surface_export", _EXPORTER_PATH)
assert _EXPORTER_SPEC is not None and _EXPORTER_SPEC.loader is not None
_EXPORTER = importlib.util.module_from_spec(_EXPORTER_SPEC)
_EXPORTER_SPEC.loader.exec_module(_EXPORTER)


def test_public_owner_git_sources_are_allowed() -> None:
    text = (
        "alpha-research @ git+https://github.com/runchengxie/alpha-research.git@abc123\n"
        "portfolio-backtester @ git+https://github.com/runchengxie/portfolio-backtester.git@def456"
    )

    assert scan_text(text, path="pyproject.toml") == []


def test_unreviewed_git_sources_remain_findings() -> None:
    findings = scan_text(
        "dependency @ " + "git+" + "https://github.com/example/" + "private-research.git@abc123",
        path="pyproject.toml",
    )

    assert findings == [{"category": "git-source-reference", "path": "pyproject.toml"}]


def test_clean_root_metadata_declares_runtime_import_dependencies() -> None:
    project = tomllib.loads((Path(__file__).parents[2] / "pyproject.toml").read_text())
    dependencies = project["project"]["dependencies"]
    names = {
        str(item).split(" @ ", 1)[0].split(">", 1)[0].lower() for item in dependencies
    }

    assert {"numpy", "pandas", "pyarrow", "pyyaml"} <= names
    assert all(
        "@ git+" not in str(item) or "alpha-research" in str(item)
        for item in dependencies
    )
