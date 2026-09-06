#!/usr/bin/env python3
"""Export the reviewed, dependency-free public control-plane surface."""

from __future__ import annotations

import argparse
import json
import re
import shutil
from pathlib import Path

MANIFEST_RELATIVE = Path("docs/public-surface-manifest.json")
PUBLIC_CLASSES = {"public-control-plane", "public-contract"}
GENERATED_PATHS = {
    "README.md",
    "pyproject.toml",
    "scripts/dev/public_dependency_registry.json",
    "scripts/dev/public_readiness_debt.json",
    "scripts/dev/public_surface_export.py",
    "scripts/dev/history_publication_audit.py",
}
PRIVATE_STRATEGY_PATTERN = re.compile(
    r"\b(?:daily[_-]?watch20|deepseek|hotsector|style[_-]?replica|d11[_-]?h5)\b",
    re.IGNORECASE,
)
SECRET_PATTERNS = (
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b"),
    re.compile(r"\bgithub_pat_[A-Za-z0-9_]{20,}\b"),
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
)

PUBLIC_README = """# Strategy Pipeline

面向 artifact 编排、发布、回执和下游交接的无依赖控制面基础能力。

本仓库负责 run 周边的物流控制。具体策略、研究流程、特征模型、组合规则、数据
provider 和执行场所由使用方仓库负责，并通过独立的薄 adapter 接入。

## 安装

```bash
pip install strategy-pipeline
```

运行时依赖公开的 owner 包和常用数据处理库。请先阅读[文档首页](docs/README.md)、[控制面 API](docs/control-plane.md)
和 [owner 接入指南](docs/integrating-an-owner.md)。

## 提供的能力

- 类型明确的 request、artifact reference 和 run receipt
- 从 owner 到 publication 的确定性编排
- 与 provider 无关的 artifact publication 和 handoff 边界
- 不依赖私有模块的通用 CLI

公共包不包含策略代码、provider SDK、凭证、私有研究流程或专有数据。
"""

PUBLIC_PYPROJECT = """[build-system]
requires = [\"setuptools>=68\", \"wheel\"]
build-backend = \"setuptools.build_meta\"

[project]
name = \"strategy-pipeline\"
version = \"0.1.0\"
description = \"Public pipeline orchestration for evaluation, artifacts, and handoff\"
readme = \"README.md\"
requires-python = \">=3.12\"
dependencies = [
  \"numpy>=1.23\",
  \"pandas>=2.0,<3\",
  \"pyarrow>=23.0.1\",
  \"pyyaml>=6.0\",
]

[tool.setuptools]
package-dir = {\"\" = \"src\"}

[tool.setuptools.packages.find]
where = [\"src\"]
include = [\"strategy_pipeline\", \"strategy_pipeline.*\"]
"""

PUBLIC_DEPENDENCY_REGISTRY = """{
  \"schema_version\": 1,
  \"repositories\": {
    \"https://github.com/runchengxie/alpha-research.git\": \"public\",
    \"https://github.com/runchengxie/market-data-platform.git\": \"public\",
    \"https://github.com/runchengxie/portfolio-backtester.git\": \"public\"
  }
}
"""


def _manifest_path(source_root: Path) -> Path:
    path = source_root / MANIFEST_RELATIVE
    if not path.is_file():
        raise ValueError(f"missing public surface manifest: {path}")
    return path


def _load_manifest(source_root: Path) -> list[dict[str, str]]:
    payload = json.loads(_manifest_path(source_root).read_text(encoding="utf-8"))
    if payload.get("schema_version") != 1 or payload.get("publication_mode") != "clean-root":
        raise ValueError("public surface manifest must use schema_version 1 and clean-root mode")
    entries = payload.get("entries")
    if not isinstance(entries, list) or not entries:
        raise ValueError("public surface manifest entries must be non-empty")
    return [entry for entry in entries if entry.get("classification") in PUBLIC_CLASSES]


def _copy_entry(source_root: Path, output_root: Path, relative: str) -> None:
    source = source_root / relative
    target = output_root / relative
    if not source.exists():
        raise ValueError(f"public manifest path does not exist: {relative}")
    if source.is_dir():
        shutil.copytree(
            source,
            target,
            dirs_exist_ok=True,
            ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "*.pyo"),
        )
    else:
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)


def _assert_public_content(source_root: Path, relative: str) -> None:
    if relative in GENERATED_PATHS:
        return
    source = source_root / relative
    candidates = [source] if source.is_file() else source.rglob("*")
    for path in candidates:
        if not path.is_file() or "__pycache__" in path.parts:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        if PRIVATE_STRATEGY_PATTERN.search(text):
            raise ValueError(f"private strategy marker in public path: {relative}")
        if any(pattern.search(text) for pattern in SECRET_PATTERNS):
            raise ValueError(f"secret pattern in public path: {relative}")


def _write_public_metadata(
    source_root: Path,
    output_root: Path,
    copied_paths: list[str],
) -> None:
    (output_root / "README.md").write_text(PUBLIC_README, encoding="utf-8")
    (output_root / "pyproject.toml").write_text(PUBLIC_PYPROJECT, encoding="utf-8")
    package = output_root / "src" / "strategy_pipeline"
    package.mkdir(parents=True, exist_ok=True)
    source_init = source_root / "src" / "strategy_pipeline" / "__init__.py"
    if not source_init.is_file():
        raise ValueError(f"missing public package initializer: {source_init}")
    shutil.copy2(source_init, package / "__init__.py")
    dev = output_root / "scripts" / "dev"
    dev.mkdir(parents=True, exist_ok=True)
    (dev / "public_dependency_registry.json").write_text(
        PUBLIC_DEPENDENCY_REGISTRY,
        encoding="utf-8",
    )
    (dev / "public_readiness_debt.json").write_text(
        '{\n  "schema_version": 1,\n  "entries": {}\n}\n',
        encoding="utf-8",
    )
    docs = output_root / "docs"
    docs.mkdir(parents=True, exist_ok=True)
    public_manifest_entries = [
        {
            "path": path,
            "classification": "public-control-plane",
            "owner": "strategy-pipeline maintainers",
            "sensitivity": "releasable",
            "reason": "Included in the reviewed clean-root public surface.",
        }
        for path in copied_paths
    ]
    if "scripts/dev/public_surface_export.py" not in copied_paths:
        public_manifest_entries.append(
            {
                "path": "scripts/dev/public_surface_export.py",
                "classification": "public-control-plane",
                "owner": "strategy-pipeline maintainers",
                "sensitivity": "releasable",
                "reason": "Reproducible exporter for the reviewed public surface.",
            }
        )
    (docs / "public-surface-manifest.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "publication_mode": "clean-root",
                "entries": public_manifest_entries,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def export_public_surface(source_root: Path, output_root: Path) -> dict[str, object]:
    source_root = source_root.resolve()
    output_root = output_root.resolve()
    if output_root.exists() and any(output_root.iterdir()):
        raise ValueError(f"output directory must be empty: {output_root}")
    output_root.mkdir(parents=True, exist_ok=True)

    entries = _load_manifest(source_root)
    for entry in entries:
        _assert_public_content(source_root, entry["path"])
        _copy_entry(source_root, output_root, entry["path"])
    copied_paths = sorted(entry["path"] for entry in entries)
    if (source_root / "scripts/dev/public_surface_export.py").exists():
        _copy_entry(source_root, output_root, "scripts/dev/public_surface_export.py")
    _write_public_metadata(source_root, output_root, copied_paths)
    return {
        "ready": True,
        "source_root": str(source_root),
        "output_root": str(output_root),
        "copied_paths": copied_paths,
        "excluded_by_default": True,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=Path.cwd())
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    report = export_public_surface(args.source, args.output)
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
