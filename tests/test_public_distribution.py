from __future__ import annotations

import tomllib
from pathlib import Path

import pytest
from packaging.markers import Marker
from packaging.version import Version

ROOT = Path(__file__).resolve().parents[1]
SDK_REVISION = "51ab1e8cb2267d938a0681b81f2419d504ed91cc"
SDK_REPOSITORY = "https://github.com/runchengxie/quant-backtest-engine.git"
SDK_DEPENDENCY = (
    f"quant-backtest-engine-client @ git+{SDK_REPOSITORY}@{SDK_REVISION}#subdirectory=python"
)

CORE_DEPENDENCY = (
    f"quant-backtest-core[minute,cost,scenario,planning] @ git+{SDK_REPOSITORY}@{SDK_REVISION}"
    "#subdirectory=core"
)


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
            assert source["git"].startswith(
                "https://github.com/runchengxie/research-code-quality.git"
            )
        elif package["name"] in {"quant-backtest-engine-client", "quant-backtest-core"}:
            subdir = "core" if package["name"] == "quant-backtest-core" else "python"
            assert source == {
                "git": f"{SDK_REPOSITORY}?subdirectory={subdir}&rev={SDK_REVISION}#{SDK_REVISION}"
            }
        else:
            assert source == {"registry": "https://pypi.org/simple"}


def test_distribution_declares_public_registry_and_immutable_provider_dependencies() -> None:
    project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    dependencies = project["project"]["dependencies"]
    dev_dependencies = project["dependency-groups"]["dev"]

    assert project["project"]["version"] == "0.2.0"
    assert project["project"]["requires-python"] == ">=3.12,<3.14"
    assert dependencies == [
        CORE_DEPENDENCY,
        SDK_DEPENDENCY,
        "duckdb>=1.2",
        "numpy>=1.23",
        "pandas>=2.0",
        "pyarrow>=25.0.1",
        "PyYAML>=6.0",
        "scipy>=1.14",
        "research-contracts>=0.1.0",
    ]
    assert project["project"]["optional-dependencies"]["ml"] == [
        "pandas-ta>=0.3.14b0",
        "scikit-learn>=1.9.0",
        "ta>=0.11,<0.12",
        "xgboost>=1.7",
    ]
    assert project["project"]["optional-dependencies"]["engine"] == [SDK_DEPENDENCY]
    assert dev_dependencies == [
        SDK_DEPENDENCY,
        "maturin>=1,<2",
        "pandas-ta>=0.3.14b0",
        "scikit-learn>=1.9.0",
        "xgboost>=1.7",
        "polars>=1.0",
        "torch>=2.0",
        "jsonschema>=4.25",
        "pytest>=9.0.3",
        "pytest-cov>=6.0",
        "research-code-quality",
        "ruff>=0.8",
        "ty==0.0.86",
        "ta>=0.11,<0.12",
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


@pytest.mark.parametrize("python_version", ["3.12", "3.13"])
def test_lock_preserves_current_pandas_in_supported_python_modes(python_version: str) -> None:
    lock = tomllib.loads((ROOT / "uv.lock").read_text(encoding="utf-8"))
    environment = {"python_version": python_version, "python_full_version": f"{python_version}.0"}
    selected = [
        package["version"]
        for package in lock["package"]
        if package["name"] == "pandas"
        and (
            not package.get("resolution-markers")
            or any(Marker(marker).evaluate(environment) for marker in package["resolution-markers"])
        )
    ]
    assert len(selected) == 1
    assert Version(selected[0]) >= Version("3.0.5")
