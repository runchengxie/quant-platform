"""Module alias preserving implementation identity during compatibility migration."""

import sys
from importlib import import_module
from typing import TYPE_CHECKING

__all__ = [
    "Any",
    "DetailedTradeFeeModel",
    "Mapping",
    "_execution_market_rule_columns",
    "_execution_trade_fee_model",
    "_filter_positions_to_backtest_periods",
    "_optional_market_rule_col",
    "_rebalance_key",
    "_record_period_execution_sim",
    "_record_period_ideal_daily_nav",
    "_run_period_execution_simulations",
    "annotations",
    "cast",
    "logger",
    "simulate_capacity_execution",
    "simulate_execution_adjusted_nav",
    "simulate_ideal_daily_nav",
]

if TYPE_CHECKING:
    from quant_platform._portfolio._evaluation_positions import (
        Any,
        DetailedTradeFeeModel,
        Mapping,
        _execution_market_rule_columns,
        _execution_trade_fee_model,
        _filter_positions_to_backtest_periods,
        _optional_market_rule_col,
        _rebalance_key,
        _record_period_execution_sim,
        _record_period_ideal_daily_nav,
        _run_period_execution_simulations,
        annotations,
        cast,
        logger,
        simulate_capacity_execution,
        simulate_execution_adjusted_nav,
        simulate_ideal_daily_nav,
    )

sys.modules[__name__] = import_module("quant_platform._portfolio._evaluation_positions")
