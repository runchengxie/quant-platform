from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_package_boundary_is_retained() -> None:
    assert (ROOT / "packages").is_dir()
    assert (ROOT / "packages/execution/src/quant_execution_engine").is_dir()
    assert (ROOT / "packages/alpha/src/alpha_research").is_dir()


def test_repository_assets_use_target_paths() -> None:
    assert (ROOT / "config/contracts/style-factor-backtest-v1.schema.json").is_file()
    assert (ROOT / "config/migration/provenance.json").is_file()
    assert (ROOT / "docs/examples/synthetic-style-factor.csv").is_file()


def test_old_repository_asset_directories_are_removed() -> None:
    assert not any((ROOT / name).is_dir() for name in ("contracts", "examples", "migration"))


def test_contract_and_migration_payloads_keep_machine_readable_shapes() -> None:
    schema = json.loads(
        (ROOT / "config/contracts/style-factor-backtest-v1.schema.json").read_text(encoding="utf-8")
    )
    provenance = json.loads((ROOT / "config/migration/provenance.json").read_text(encoding="utf-8"))
    assert schema["$schema"]
    assert provenance["source_repository"]
