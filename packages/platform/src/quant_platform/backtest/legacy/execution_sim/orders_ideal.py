"""Module alias preserving implementation identity during compatibility migration."""

import sys
from importlib import import_module
from typing import TYPE_CHECKING

__all__ = [
    "SELL_UNTIL_NEXT_REBALANCE",
    "Any",
    "CostBreakdown",
    "DetailedTradeFeeModel",
    "ExecutionSimConfig",
    "Mapping",
    "TradeFeeModel",
    "_ExecutionTables",
    "_NavOrder",
    "_add_breakdown",
    "_append_nav_order_row",
    "_apply_ideal_buy_fill",
    "_apply_ideal_sell_fill",
    "_build_ideal_rebalance_orders",
    "_build_nav_orders_for_target",
    "_cost_adjusted_target_notional",
    "_execute_ideal_buy_orders",
    "_execute_ideal_sell_orders",
    "_ideal_buy_status",
    "_ideal_nav_order",
    "_ideal_sell_status",
    "_nav_sell_max_days",
    "_position_values_by_symbol",
    "_price_at",
    "_rebalance_ideal_target",
    "_record_nav_fill_audit",
    "_trade_fee",
    "_update_nav_order",
    "annotations",
]

if TYPE_CHECKING:
    from quant_platform._portfolio.execution_sim.orders_ideal import (
        SELL_UNTIL_NEXT_REBALANCE,
        Any,
        CostBreakdown,
        DetailedTradeFeeModel,
        ExecutionSimConfig,
        Mapping,
        TradeFeeModel,
        _add_breakdown,
        _append_nav_order_row,
        _apply_ideal_buy_fill,
        _apply_ideal_sell_fill,
        _build_ideal_rebalance_orders,
        _build_nav_orders_for_target,
        _cost_adjusted_target_notional,
        _execute_ideal_buy_orders,
        _execute_ideal_sell_orders,
        _ExecutionTables,
        _ideal_buy_status,
        _ideal_nav_order,
        _ideal_sell_status,
        _nav_sell_max_days,
        _NavOrder,
        _position_values_by_symbol,
        _price_at,
        _rebalance_ideal_target,
        _record_nav_fill_audit,
        _trade_fee,
        _update_nav_order,
        annotations,
    )

sys.modules[__name__] = import_module("quant_platform._portfolio.execution_sim.orders_ideal")
