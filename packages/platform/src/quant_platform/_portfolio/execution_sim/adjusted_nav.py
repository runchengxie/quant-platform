"""Legacy call signature with Engine execution and Platform research reporting."""

from __future__ import annotations

from typing import Any

from quant_backtest_core.daily.execution_sim.adjusted_nav import *  # noqa: F403
from quant_backtest_core.daily.execution_sim.adjusted_nav import CorporateAction as CorporateAction
from quant_backtest_core.daily.execution_sim.adjusted_nav import (
    ExecutionAdjustedNavResult as ExecutionAdjustedNavResult,
)
from quant_backtest_core.daily.execution_sim.adjusted_nav import (
    ExecutionSimConfig as ExecutionSimConfig,
)
from quant_backtest_core.daily.execution_sim.adjusted_nav import Iterable as Iterable
from quant_backtest_core.daily.execution_sim.adjusted_nav import SlippageModel as SlippageModel
from quant_backtest_core.daily.execution_sim.adjusted_nav import TradeFeeModel as TradeFeeModel
from quant_backtest_core.daily.execution_sim.adjusted_nav import __dict__ as _owned_names
from quant_backtest_core.daily.execution_sim.adjusted_nav import (
    _ExecutionTables as _ExecutionTables,
)
from quant_backtest_core.daily.execution_sim.adjusted_nav import pd as pd
from quant_backtest_core.daily.execution_sim.adjusted_nav import (
    simulate_execution_adjusted_nav as _owned_run,
)

from quant_platform.backtest.engine_daily import restore_daily_research


def __getattr__(name: str) -> Any:
    try:
        return _owned_names[name]
    except KeyError as error:
        raise AttributeError(name) from error


def simulate_execution_adjusted_nav(
    positions: pd.DataFrame | None,
    pricing_data: pd.DataFrame | None,
    config: ExecutionSimConfig,
    *,
    price_col: str,
    tradable_col: str | None = None,
    buy_tradable_col: str | None = None,
    sell_tradable_col: str | None = None,
    limit_up_col: str | None = None,
    limit_down_col: str | None = None,
    listing_status_col: str | None = None,
    transaction_cost_bps: float = 0.0,
    trading_days_per_year: int = 252,
    trade_fee_model: TradeFeeModel | None = None,
    slippage_model: SlippageModel | None = None,
    prepared_tables: _ExecutionTables | None = None,
    corporate_actions: Iterable[CorporateAction] | None = None,
    price_basis: str | None = None,
) -> ExecutionAdjustedNavResult:
    result = _owned_run(
        positions,
        pricing_data,
        config,
        price_col=price_col,
        tradable_col=tradable_col,
        buy_tradable_col=buy_tradable_col,
        sell_tradable_col=sell_tradable_col,
        limit_up_col=limit_up_col,
        limit_down_col=limit_down_col,
        listing_status_col=listing_status_col,
        transaction_cost_bps=transaction_cost_bps,
        trading_days_per_year=trading_days_per_year,
        trade_fee_model=trade_fee_model,
        slippage_model=slippage_model,
        prepared_tables=prepared_tables,
        corporate_actions=corporate_actions,
        price_basis=price_basis,
    )
    return restore_daily_research(result, trading_days_per_year)
