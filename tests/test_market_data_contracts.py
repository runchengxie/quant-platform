from __future__ import annotations

from pathlib import Path

import pytest

from market_data_platform.data_provider_contracts import (
    fundamentals_provider_supported,
    require_supported_market,
)
from market_data_platform.dataset_contracts import (
    DatasetContract,
    validate_dataset_contract,
)


def test_dataset_contract_round_trips_public_semantics() -> None:
    payload = DatasetContract(
        dataset_id="synthetic.daily",
        provider="synthetic",
        market="a_share",
        asset_schema_version="v1",
        primary_key=("trade_date", "symbol"),
        ordering={"exchange_sequence_available": False},
        quality_rules={"duplicate_key": "quarantine"},
    ).to_payload()

    assert validate_dataset_contract(payload) == payload


def test_public_market_boundary_is_explicit() -> None:
    assert require_supported_market("A_SHARE") == "a_share"
    assert fundamentals_provider_supported("synthetic", "a_share") is False
    with pytest.raises(ValueError, match="Supported markets"):
        require_supported_market("unknown")


def test_public_data_package_contains_no_provider_implementation() -> None:
    package_root = Path(__file__).parents[1] / "packages" / "portfolio-backtester" / "src"
    names = {path.name for path in (package_root / "market_data_platform").rglob("*")}
    assert "providers" not in names
    assert "credentials" not in {name.casefold() for name in names}
