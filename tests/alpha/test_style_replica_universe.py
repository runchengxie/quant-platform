from __future__ import annotations

import pandas as pd
import pytest
from alpha_research.style_replica.universe import filter_style_replica_universe


def test_historical_st_status_filters_only_its_own_date() -> None:
    dates = pd.to_datetime(["2025-01-02", "2025-01-03"])
    prices = pd.DataFrame({"A": [10.0, 11.0], "B": [20.0, 21.0]}, index=dates)
    instruments = pd.DataFrame(
        {
            "symbol": ["A", "B", "A", "B"],
            "trade_date": [20250102, 20250102, 20250103, 20250103],
            "is_st": [False, False, True, False],
            "is_suspended": [False] * 4,
            "list_date": ["20200101"] * 4,
            "name": ["ST 当前名称"] * 4,
        }
    )
    jan2 = filter_style_replica_universe(
        prices, instruments, dates[0], min_history=1, min_listed_days=0
    )
    jan3 = filter_style_replica_universe(
        prices, instruments, dates[1], min_history=1, min_listed_days=0
    )
    assert jan2.columns.tolist() == ["A", "B"]
    assert jan3.columns.tolist() == ["B"]


def test_current_name_cannot_supply_historical_st_status() -> None:
    prices = pd.DataFrame({"A": [10.0]}, index=pd.to_datetime(["2025-01-02"]))
    instruments = pd.DataFrame({"symbol": ["A"], "name": ["ST 当前名称"]})
    with pytest.raises(ValueError, match=r"trade_date.*is_st"):
        filter_style_replica_universe(prices, instruments, "2025-01-02", min_history=1)


def test_missing_dated_instrument_row_never_falls_back_to_price_history() -> None:
    prices = pd.DataFrame({"A": [10.0]}, index=pd.to_datetime(["2025-01-02"]))
    instruments = pd.DataFrame(
        {
            "symbol": ["A"],
            "trade_date": ["20250103"],
            "is_st": [False],
            "is_suspended": [False],
            "list_date": ["20200101"],
        }
    )
    assert filter_style_replica_universe(prices, instruments, "2025-01-02", min_history=1).empty


def test_unknown_st_and_suspended_status_cannot_form_positions() -> None:
    prices = pd.DataFrame({"A": [10.0], "B": [20.0]}, index=pd.to_datetime(["2025-01-02"]))
    instruments = pd.DataFrame(
        {
            "symbol": ["A", "B"],
            "trade_date": [20250102, 20250102],
            "is_st": [pd.NA, False],
            "is_suspended": [False, True],
            "list_date": [20200101, 20200101],
        }
    )
    assert filter_style_replica_universe(prices, instruments, "2025-01-02", min_history=1).empty
