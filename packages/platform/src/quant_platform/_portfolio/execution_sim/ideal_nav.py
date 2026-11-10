"""Legacy call signature with Engine execution and Platform research reporting."""

from __future__ import annotations

from typing import Any

from quant_backtest_core.daily.execution_sim.ideal_nav import *  # noqa: F403 - compatibility names
from quant_backtest_core.daily.execution_sim.ideal_nav import (
    DetailedTradeFeeModel as DetailedTradeFeeModel,
)
from quant_backtest_core.daily.execution_sim.ideal_nav import (
    ExecutionAdjustedNavResult as ExecutionAdjustedNavResult,
)
from quant_backtest_core.daily.execution_sim.ideal_nav import __dict__ as _owned_names
from quant_backtest_core.daily.execution_sim.ideal_nav import pd as pd
from quant_backtest_core.daily.execution_sim.ideal_nav import simulate_ideal_daily_nav as _owned_run

from quant_platform.backtest.engine_daily import restore_daily_research


def __getattr__(name: str) -> Any:
    try:
        return _owned_names[name]
    except KeyError as error:
        raise AttributeError(name) from error


def simulate_ideal_daily_nav(
    positions: pd.DataFrame | None,
    pricing_data: pd.DataFrame | None,
    *,
    price_col: str,
    limit_up_col: str | None = None,
    limit_down_col: str | None = None,
    listing_status_col: str | None = None,
    transaction_cost_bps: float = 0.0,
    trading_days_per_year: int = 252,
    portfolio_value: float = 1000000.0,
    trade_fee_model: DetailedTradeFeeModel | None = None,
) -> ExecutionAdjustedNavResult:
    result = _owned_run(
        positions,
        pricing_data,
        price_col=price_col,
        limit_up_col=limit_up_col,
        limit_down_col=limit_down_col,
        listing_status_col=listing_status_col,
        transaction_cost_bps=transaction_cost_bps,
        trading_days_per_year=trading_days_per_year,
        portfolio_value=portfolio_value,
        trade_fee_model=trade_fee_model,
    )
    return restore_daily_research(result, trading_days_per_year)
