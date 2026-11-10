"""Engine alias: quant_backtest_core.daily.execution_sim.orders."""

from __future__ import annotations

import sys
from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from quant_backtest_core.daily.execution_sim.orders import (
        _append_nav_order_row as _append_nav_order_row,
    )
    from quant_backtest_core.daily.execution_sim.orders import (
        _append_order_rows as _append_order_rows,
    )
    from quant_backtest_core.daily.execution_sim.orders import (
        _apply_ideal_buy_fill as _apply_ideal_buy_fill,
    )
    from quant_backtest_core.daily.execution_sim.orders import (
        _apply_ideal_sell_fill as _apply_ideal_sell_fill,
    )
    from quant_backtest_core.daily.execution_sim.orders import (
        _build_ideal_rebalance_orders as _build_ideal_rebalance_orders,
    )
    from quant_backtest_core.daily.execution_sim.orders import (
        _build_nav_orders_for_target as _build_nav_orders_for_target,
    )
    from quant_backtest_core.daily.execution_sim.orders import (
        _build_order_states as _build_order_states,
    )
    from quant_backtest_core.daily.execution_sim.orders import (
        _build_targets_by_rebalance as _build_targets_by_rebalance,
    )
    from quant_backtest_core.daily.execution_sim.orders import (
        _cash_weight_breakdown as _cash_weight_breakdown,
    )
    from quant_backtest_core.daily.execution_sim.orders import (
        _cost_adjusted_target_notional as _cost_adjusted_target_notional,
    )
    from quant_backtest_core.daily.execution_sim.orders import (
        _execute_buy_orders as _execute_buy_orders,
    )
    from quant_backtest_core.daily.execution_sim.orders import (
        _execute_ideal_buy_orders as _execute_ideal_buy_orders,
    )
    from quant_backtest_core.daily.execution_sim.orders import (
        _execute_ideal_sell_orders as _execute_ideal_sell_orders,
    )
    from quant_backtest_core.daily.execution_sim.orders import (
        _execute_nav_buy_orders_for_day as _execute_nav_buy_orders_for_day,
    )
    from quant_backtest_core.daily.execution_sim.orders import (
        _execute_nav_orders_for_day as _execute_nav_orders_for_day,
    )
    from quant_backtest_core.daily.execution_sim.orders import (
        _execute_nav_sell_orders_for_day as _execute_nav_sell_orders_for_day,
    )
    from quant_backtest_core.daily.execution_sim.orders import (
        _execute_sell_orders as _execute_sell_orders,
    )
    from quant_backtest_core.daily.execution_sim.orders import (
        _finalize_open_nav_orders as _finalize_open_nav_orders,
    )
    from quant_backtest_core.daily.execution_sim.orders import (
        _ideal_buy_status as _ideal_buy_status,
    )
    from quant_backtest_core.daily.execution_sim.orders import _ideal_nav_order as _ideal_nav_order
    from quant_backtest_core.daily.execution_sim.orders import (
        _ideal_sell_status as _ideal_sell_status,
    )
    from quant_backtest_core.daily.execution_sim.orders import (
        _nav_order_is_complete as _nav_order_is_complete,
    )
    from quant_backtest_core.daily.execution_sim.orders import (
        _nav_order_should_abort_buy as _nav_order_should_abort_buy,
    )
    from quant_backtest_core.daily.execution_sim.orders import (
        _nav_sell_max_days as _nav_sell_max_days,
    )
    from quant_backtest_core.daily.execution_sim.orders import (
        _rebalance_ideal_target as _rebalance_ideal_target,
    )
    from quant_backtest_core.daily.execution_sim.orders import _record_fill as _record_fill
    from quant_backtest_core.daily.execution_sim.orders import _record_nav_fill as _record_nav_fill
    from quant_backtest_core.daily.execution_sim.orders import (
        _target_cash_notional as _target_cash_notional,
    )
    from quant_backtest_core.daily.execution_sim.orders import (
        _update_nav_order as _update_nav_order,
    )
    from quant_backtest_core.daily.execution_sim.orders import _update_state as _update_state

sys.modules[__name__] = import_module("quant_backtest_core.daily.execution_sim.orders")
