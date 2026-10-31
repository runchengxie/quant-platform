"""Module alias preserving implementation identity during compatibility migration."""

import sys
from importlib import import_module
from typing import TYPE_CHECKING

__all__ = [
    "_append_nav_order_row",
    "_append_order_rows",
    "_apply_ideal_buy_fill",
    "_apply_ideal_sell_fill",
    "_build_ideal_rebalance_orders",
    "_build_nav_orders_for_target",
    "_build_order_states",
    "_build_targets_by_rebalance",
    "_cash_weight_breakdown",
    "_cost_adjusted_target_notional",
    "_execute_buy_orders",
    "_execute_ideal_buy_orders",
    "_execute_ideal_sell_orders",
    "_execute_nav_buy_orders_for_day",
    "_execute_nav_orders_for_day",
    "_execute_nav_sell_orders_for_day",
    "_execute_sell_orders",
    "_finalize_open_nav_orders",
    "_ideal_buy_status",
    "_ideal_nav_order",
    "_ideal_sell_status",
    "_nav_order_is_complete",
    "_nav_order_should_abort_buy",
    "_nav_sell_max_days",
    "_rebalance_ideal_target",
    "_record_fill",
    "_record_nav_fill",
    "_target_cash_notional",
    "_update_nav_order",
    "_update_state",
]

if TYPE_CHECKING:
    from quant_platform._portfolio.execution_sim.orders import (
        _append_nav_order_row,
        _append_order_rows,
        _apply_ideal_buy_fill,
        _apply_ideal_sell_fill,
        _build_ideal_rebalance_orders,
        _build_nav_orders_for_target,
        _build_order_states,
        _build_targets_by_rebalance,
        _cash_weight_breakdown,
        _cost_adjusted_target_notional,
        _execute_buy_orders,
        _execute_ideal_buy_orders,
        _execute_ideal_sell_orders,
        _execute_nav_buy_orders_for_day,
        _execute_nav_orders_for_day,
        _execute_nav_sell_orders_for_day,
        _execute_sell_orders,
        _finalize_open_nav_orders,
        _ideal_buy_status,
        _ideal_nav_order,
        _ideal_sell_status,
        _nav_order_is_complete,
        _nav_order_should_abort_buy,
        _nav_sell_max_days,
        _rebalance_ideal_target,
        _record_fill,
        _record_nav_fill,
        _target_cash_notional,
        _update_nav_order,
        _update_state,
    )

sys.modules[__name__] = import_module("quant_platform._portfolio.execution_sim.orders")
