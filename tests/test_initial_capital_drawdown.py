"""Synthetic regressions for losses before the first observed wealth peak."""

import numpy as np
import pandas as pd
import pytest
from alpha_research.overfitting_diagnostics import _max_drawdown as scenario_drawdown
from alpha_research.pbo import _max_drawdown as pbo_drawdown
from alpha_research.return_metrics import summarize_period_returns as alpha_summary

from portfolio_backtester._metrics_period import summarize_period_returns
from portfolio_backtester._tearsheet_stats import _summarize_series
from portfolio_backtester._tearsheet_tables import _drawdown_periods


@pytest.mark.parametrize("summary", [summarize_period_returns, alpha_summary])
@pytest.mark.parametrize(
    "values, duration, recovery",
    [
        ([-0.000001], 1, np.nan),
        ([-0.1], 1, np.nan),
        ([-0.1, -0.1, 0.3], 2, 1),
        ([0.1, -0.2, 0.3], 1, 1),
    ],
)
def test_period_drawdown_includes_initial_capital(summary, values, duration, recovery):
    returns = pd.Series(values, index=pd.date_range("2024-01-01", periods=len(values)))
    info = [{"entry_idx": i, "exit_idx": i + 1} for i in range(len(values))]
    result = summary(returns, info, 252)
    expected = -0.2 if values[0] > 0 else (1 + returns).cumprod().min() - 1
    assert result["max_drawdown"] == pytest.approx(expected)
    assert result["calmar"] == pytest.approx(result["ann_return"] / abs(expected))
    assert result["drawdown_duration"] == duration
    if np.isnan(recovery):
        assert np.isnan(result["recovery_time"])
    else:
        assert result["recovery_time"] == recovery
    if values[0] < 0:
        assert np.isnan(result["drawdown_duration_days"])


@pytest.mark.parametrize("drawdown", [pbo_drawdown, scenario_drawdown])
def test_diagnostic_drawdown_includes_initial_capital(drawdown):
    assert drawdown(pd.Series([-0.1])) == pytest.approx(-0.1)


def test_tearsheet_drawdown_includes_initial_capital():
    returns = pd.Series([-0.1, 0.2], index=pd.date_range("2024-01-01", periods=2))
    result = _summarize_series(returns, periods_per_year=252)
    assert result["max_drawdown"] == pytest.approx(-0.1)
    periods = _drawdown_periods(returns, limit=5)
    assert len(periods) == 1
    assert periods[0]["drawdown"] == pytest.approx(-0.1)


@pytest.mark.parametrize("stats_name", ["aexe", "round_lot", "staggered"])
def test_execution_drawdown_includes_initial_capital(stats_name):
    from types import SimpleNamespace

    from portfolio_backtester._aexe_io import compute_stats
    from portfolio_backtester.a_share_round_lot_diagnostics import (
        compute_round_lot_simulation_stats,
    )
    from portfolio_backtester.execution_summary import summarize_staggered_execution

    daily = pd.DataFrame(
        {
            "trade_date": ["2024-01-01"],
            "daily_return": [-0.1],
            "net_return": [-0.1],
            "nav": [0.9],
            "gross_nav_before_cost": [1.0],
            "traded_notional": [0.0],
            "cash_weight": [1.0],
            "holdings": [0],
            "max_weight": [0.0],
            "transaction_cost": [0.0],
            "blocked_buy_weight": [0.0],
            "blocked_sell_weight": [0.0],
        }
    )
    if stats_name == "aexe":
        result = compute_stats(daily)
    elif stats_name == "round_lot":
        result = compute_round_lot_simulation_stats(daily)
    else:
        result = summarize_staggered_execution(
            SimpleNamespace(daily=daily, summary={}),
            variant="synthetic",
            horizon=1,
            single_side_cost_bps=0.0,
        )
    assert result["max_drawdown"] == pytest.approx(-0.1)
