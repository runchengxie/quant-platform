"""Legacy call signature with Engine execution and Platform research reporting."""

from __future__ import annotations

from typing import Any

from quant_backtest_core.daily._position_backtest_engine import *  # noqa: F403
from quant_backtest_core.daily._position_backtest_engine import (
    PositionBacktestConfig as PositionBacktestConfig,
)
from quant_backtest_core.daily._position_backtest_engine import (
    PositionBacktestResult as PositionBacktestResult,
)
from quant_backtest_core.daily._position_backtest_engine import __dict__ as _owned_names
from quant_backtest_core.daily._position_backtest_engine import pd as pd
from quant_backtest_core.daily._position_backtest_engine import run_position_backtest as _owned_run

from quant_platform.backtest.engine_daily import restore_period_research


def __getattr__(name: str) -> Any:
    try:
        return _owned_names[name]
    except KeyError as error:
        raise AttributeError(name) from error


def run_position_backtest(
    *,
    positions: pd.DataFrame,
    pricing: pd.DataFrame,
    periods: pd.DataFrame,
    config: PositionBacktestConfig,
    intraday_bars: pd.DataFrame | None = None,
) -> PositionBacktestResult:
    result = _owned_run(
        positions=positions,
        pricing=pricing,
        periods=periods,
        config=config,
        intraday_bars=intraday_bars,
    )
    return restore_period_research(result, config.trading_days_per_year)
