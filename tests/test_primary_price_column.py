"""Compatibility for explicit, empty-string primary pricing column names."""

import pandas as pd
import pytest

from quant_platform.backtest.legacy.position_backtest import (
    PositionBacktestConfig,
    normalize_position_backtest_pricing,
    run_position_backtest,
)


@pytest.mark.parametrize("terminal", [None, "close"])
def test_empty_primary_column_is_preserved_in_normalizer_and_public_replay(
    terminal: str | None,
) -> None:
    prices = pd.DataFrame(
        {
            "trade_date": ["20240102", "20240103"],
            "symbol": ["A", "A"],
            "": ["10", "12"],
            "close": [11.0, 15.0],
        }
    )
    normalized = normalize_position_backtest_pricing(
        prices, price_col="", terminal_exit_price_col=terminal
    )
    assert normalized[""].tolist() == [10, 12]
    result = run_position_backtest(
        positions=pd.DataFrame(
            [{"rebalance_date": "20240101", "entry_date": "20240102", "symbol": "A", "weight": 1.0}]
        ),
        pricing=prices,
        periods=pd.DataFrame(
            [{"rebalance_date": "20240101", "entry_date": "20240102", "exit_date": "20240103"}]
        ),
        config=PositionBacktestConfig(price_col="", terminal_exit_price_col=terminal),
    )
    expected = 0.2 if terminal is None else 0.5
    assert result.gross_returns["gross_return"].tolist() == pytest.approx([expected])


def test_missing_empty_primary_column_raises_the_required_column_error() -> None:
    prices = pd.DataFrame({"trade_date": ["20240102"], "symbol": ["A"], "close": [10.0]})
    with pytest.raises(ValueError, match="missing required column"):
        normalize_position_backtest_pricing(prices, price_col="", terminal_exit_price_col="close")
