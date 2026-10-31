"""Module alias preserving implementation identity during compatibility migration."""

import sys
from importlib import import_module
from typing import TYPE_CHECKING

__all__ = [
    "_AUDIT_TZ",
    "Any",
    "CostBreakdown",
    "ExecutionSimConfig",
    "_NavOrder",
    "_TradeFeeQuote",
    "_append_nav_order_row",
    "_append_order_rows",
    "_audit_timestamps",
    "_build_order_states",
    "_finalize_open_nav_orders",
    "_format_date",
    "_nav_order_is_complete",
    "_nav_order_should_abort_buy",
    "_record_fill",
    "_record_nav_fill",
    "_record_nav_fill_audit",
    "_update_nav_order",
    "_update_state",
    "annotations",
    "cast",
]

if TYPE_CHECKING:
    from quant_platform._portfolio.execution_sim.orders_nav_states import (
        _AUDIT_TZ,
        Any,
        CostBreakdown,
        ExecutionSimConfig,
        _append_nav_order_row,
        _append_order_rows,
        _audit_timestamps,
        _build_order_states,
        _finalize_open_nav_orders,
        _format_date,
        _nav_order_is_complete,
        _nav_order_should_abort_buy,
        _NavOrder,
        _record_fill,
        _record_nav_fill,
        _record_nav_fill_audit,
        _TradeFeeQuote,
        _update_nav_order,
        _update_state,
        annotations,
        cast,
    )

sys.modules[__name__] = import_module("quant_platform._portfolio.execution_sim.orders_nav_states")
