from __future__ import annotations

import tomllib
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def _assert_allowed_package_sources(lock: dict[str, object]) -> None:
    packages = lock["package"]
    assert isinstance(packages, list)
    for package in packages:
        assert isinstance(package, dict)
        source = package["source"]
        if package["name"] == "quant-platform":
            assert source == {"editable": "."}
        elif package["name"] == "research-contracts":
            assert source == {"directory": "packages/research-contracts"}
        elif package["name"] == "research-code-quality":
            assert source["git"].startswith("https://github.com/runchengxie/quant-code-quality.git")
        else:
            assert source == {"registry": "https://pypi.org/simple"}


def test_distribution_declares_only_public_registry_dependencies() -> None:
    project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    dependencies = project["project"]["dependencies"]
    dev_dependencies = project["dependency-groups"]["dev"]

    assert dependencies == [
        "duckdb>=1.2",
        "numpy>=1.23",
        "pandas>=2.0",
        "pandas-ta>=0.3.14b0",
        "pyarrow>=25.0.1",
        "PyYAML>=6.0",
        "scipy>=1.14",
        "scikit-learn>=1.9.0",
        "xgboost>=1.7",
        "research-contracts>=0.1.0",
    ]
    assert dev_dependencies == [
        "polars>=1.0",
        "torch>=2.0",
        "jsonschema>=4.25",
        "pytest>=9.0.3",
        "research-code-quality",
        "ruff>=0.8",
        "ty==0.0.77",
    ]
    assert project["tool"]["uv"]["sources"]["research-contracts"] == {
        "path": "packages/research-contracts"
    }


def test_lock_allows_only_pypi_and_the_project_editable_source() -> None:
    lock = tomllib.loads((ROOT / "uv.lock").read_text(encoding="utf-8"))

    _assert_allowed_package_sources(lock)


@pytest.mark.parametrize(
    "source",
    [
        {"git": "https://github.com/example/package.git"},
        {"directory": "../workspace-package"},
        {"registry": "https://packages.example.internal/simple"},
        {"editable": "../unexpected-local-package"},
    ],
)
def test_lock_source_policy_rejects_nonpublic_or_unexpected_sources(
    source: dict[str, str],
) -> None:
    lock = {"package": [{"name": "unexpected-package", "source": source}]}

    with pytest.raises(AssertionError):
        _assert_allowed_package_sources(lock)
