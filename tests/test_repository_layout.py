from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_package_boundary_is_retained() -> None:
    assert (ROOT / "packages").is_dir()
    assert (ROOT / "packages/execution/src/quant_execution_engine").is_dir()
    assert (ROOT / "packages/alpha/src/alpha_research").is_dir()


def test_migration_config_is_removed_after_transfer() -> None:
    assert not (ROOT / "config").exists()


def test_old_repository_asset_directories_are_removed() -> None:
    assert not any((ROOT / name).is_dir() for name in ("contracts", "examples", "migration"))
