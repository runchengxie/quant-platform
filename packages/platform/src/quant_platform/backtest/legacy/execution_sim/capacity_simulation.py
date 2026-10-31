"""Module alias preserving implementation identity during compatibility migration."""

import sys
from importlib import import_module
from typing import TYPE_CHECKING

__all__ = [
    "Any",
    "ExecutionSimConfig",
    "ExecutionSimResult",
    "SupportedTradeFeeModel",
    "TradeFeeModel",
    "_ExecutionTables",
    "_OrderSink",
    "_build_targets_by_rebalance",
    "_empty_result",
    "_execute_buy_orders",
    "_execute_capacity_rebalance",
    "_execute_sell_orders",
    "_fill_columns",
    "_order_columns",
    "_prepare_execution_tables",
    "_prepare_long_only_execution_positions",
    "_run_capacity_rebalances",
    "_summarize_orders",
    "annotations",
    "simulate_capacity_execution",
]

if TYPE_CHECKING:
    from quant_platform._portfolio.execution_sim.capacity_simulation import (
        Any,
        ExecutionSimConfig,
        ExecutionSimResult,
        SupportedTradeFeeModel,
        TradeFeeModel,
        _build_targets_by_rebalance,
        _empty_result,
        _execute_buy_orders,
        _execute_capacity_rebalance,
        _execute_sell_orders,
        _ExecutionTables,
        _fill_columns,
        _order_columns,
        _OrderSink,
        _prepare_execution_tables,
        _prepare_long_only_execution_positions,
        _run_capacity_rebalances,
        _summarize_orders,
        annotations,
        simulate_capacity_execution,
    )

sys.modules[__name__] = import_module("quant_platform._portfolio.execution_sim.capacity_simulation")
