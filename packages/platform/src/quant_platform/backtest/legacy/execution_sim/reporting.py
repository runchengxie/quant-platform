"""Module alias preserving implementation identity during compatibility migration."""

import sys
from importlib import import_module
from typing import TYPE_CHECKING

__all__ = [
    "Any",
    "ExecutionAdjustedNavResult",
    "ExecutionSimConfig",
    "ExecutionSimResult",
    "SupportedTradeFeeModel",
    "TradeFeeModel",
    "_daily_period_info",
    "_empty_adjusted_nav_result",
    "_empty_result",
    "_executed_daily_columns",
    "_fill_columns",
    "_format_date",
    "_market_rule_warnings",
    "_nav_fill_columns",
    "_nav_order_columns",
    "_nav_side_fill_ratio",
    "_order_columns",
    "_side_fill_ratio",
    "_summarize_adjusted_nav",
    "_summarize_orders",
    "annotations",
    "cast",
    "describe_execution_sim_config",
    "describe_trade_fee_model",
    "summarize_period_returns",
]

if TYPE_CHECKING:
    from quant_platform._portfolio.execution_sim.reporting import (
        Any,
        ExecutionAdjustedNavResult,
        ExecutionSimConfig,
        ExecutionSimResult,
        SupportedTradeFeeModel,
        TradeFeeModel,
        _daily_period_info,
        _empty_adjusted_nav_result,
        _empty_result,
        _executed_daily_columns,
        _fill_columns,
        _format_date,
        _market_rule_warnings,
        _nav_fill_columns,
        _nav_order_columns,
        _nav_side_fill_ratio,
        _order_columns,
        _side_fill_ratio,
        _summarize_adjusted_nav,
        _summarize_orders,
        annotations,
        cast,
        describe_execution_sim_config,
        describe_trade_fee_model,
        summarize_period_returns,
    )

sys.modules[__name__] = import_module("quant_platform._portfolio.execution_sim.reporting")
