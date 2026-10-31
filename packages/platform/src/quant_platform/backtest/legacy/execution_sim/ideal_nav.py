"""Module alias preserving implementation identity during compatibility migration."""

import sys
from importlib import import_module
from typing import TYPE_CHECKING

__all__ = [
    "Any",
    "CostBreakdown",
    "DatedTradeFeeModel",
    "DetailedTradeFeeModel",
    "ExecutionAdjustedNavResult",
    "ExecutionSimConfig",
    "SupportedTradeFeeModel",
    "TradeFeeModel",
    "_ExecutionTables",
    "_build_execution_tables",
    "_build_targets_by_rebalance",
    "_empty_adjusted_nav_result",
    "_executed_daily_columns",
    "_format_date",
    "_ideal_daily_nav_row",
    "_nav_fill_columns",
    "_nav_order_columns",
    "_positions_value",
    "_prepare_ideal_nav_targets",
    "_prepare_long_only_execution_positions",
    "_rebalance_ideal_target",
    "_refresh_last_prices",
    "_run_ideal_daily_nav_ledger",
    "_summarize_adjusted_nav",
    "annotations",
    "simulate_ideal_daily_nav",
]

if TYPE_CHECKING:
    from quant_platform._portfolio.execution_sim.ideal_nav import (
        Any,
        CostBreakdown,
        DatedTradeFeeModel,
        DetailedTradeFeeModel,
        ExecutionAdjustedNavResult,
        ExecutionSimConfig,
        SupportedTradeFeeModel,
        TradeFeeModel,
        _build_execution_tables,
        _build_targets_by_rebalance,
        _empty_adjusted_nav_result,
        _executed_daily_columns,
        _ExecutionTables,
        _format_date,
        _ideal_daily_nav_row,
        _nav_fill_columns,
        _nav_order_columns,
        _positions_value,
        _prepare_ideal_nav_targets,
        _prepare_long_only_execution_positions,
        _rebalance_ideal_target,
        _refresh_last_prices,
        _run_ideal_daily_nav_ledger,
        _summarize_adjusted_nav,
        annotations,
        simulate_ideal_daily_nav,
    )

sys.modules[__name__] = import_module("quant_platform._portfolio.execution_sim.ideal_nav")
