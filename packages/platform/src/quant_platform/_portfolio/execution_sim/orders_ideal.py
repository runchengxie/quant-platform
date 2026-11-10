"""Engine alias: quant_backtest_core.daily.execution_sim.orders_ideal."""

from __future__ import annotations

import sys
from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from quant_backtest_core.daily.execution_sim.orders_ideal import (
        SELL_UNTIL_NEXT_REBALANCE as SELL_UNTIL_NEXT_REBALANCE,
    )
    from quant_backtest_core.daily.execution_sim.orders_ideal import Any as Any
    from quant_backtest_core.daily.execution_sim.orders_ideal import CostBreakdown as CostBreakdown
    from quant_backtest_core.daily.execution_sim.orders_ideal import (
        DetailedTradeFeeModel as DetailedTradeFeeModel,
    )
    from quant_backtest_core.daily.execution_sim.orders_ideal import (
        ExecutionSimConfig as ExecutionSimConfig,
    )
    from quant_backtest_core.daily.execution_sim.orders_ideal import Mapping as Mapping
    from quant_backtest_core.daily.execution_sim.orders_ideal import TradeFeeModel as TradeFeeModel
    from quant_backtest_core.daily.execution_sim.orders_ideal import (
        _add_breakdown as _add_breakdown,
    )
    from quant_backtest_core.daily.execution_sim.orders_ideal import (
        _append_nav_order_row as _append_nav_order_row,
    )
    from quant_backtest_core.daily.execution_sim.orders_ideal import (
        _apply_ideal_buy_fill as _apply_ideal_buy_fill,
    )
    from quant_backtest_core.daily.execution_sim.orders_ideal import (
        _apply_ideal_sell_fill as _apply_ideal_sell_fill,
    )
    from quant_backtest_core.daily.execution_sim.orders_ideal import (
        _build_ideal_rebalance_orders as _build_ideal_rebalance_orders,
    )
    from quant_backtest_core.daily.execution_sim.orders_ideal import (
        _build_nav_orders_for_target as _build_nav_orders_for_target,
    )
    from quant_backtest_core.daily.execution_sim.orders_ideal import (
        _cost_adjusted_target_notional as _cost_adjusted_target_notional,
    )
    from quant_backtest_core.daily.execution_sim.orders_ideal import (
        _execute_ideal_buy_orders as _execute_ideal_buy_orders,
    )
    from quant_backtest_core.daily.execution_sim.orders_ideal import (
        _execute_ideal_sell_orders as _execute_ideal_sell_orders,
    )
    from quant_backtest_core.daily.execution_sim.orders_ideal import (
        _ExecutionTables as _ExecutionTables,
    )
    from quant_backtest_core.daily.execution_sim.orders_ideal import (
        _ideal_buy_status as _ideal_buy_status,
    )
    from quant_backtest_core.daily.execution_sim.orders_ideal import (
        _ideal_nav_order as _ideal_nav_order,
    )
    from quant_backtest_core.daily.execution_sim.orders_ideal import (
        _ideal_sell_status as _ideal_sell_status,
    )
    from quant_backtest_core.daily.execution_sim.orders_ideal import (
        _nav_sell_max_days as _nav_sell_max_days,
    )
    from quant_backtest_core.daily.execution_sim.orders_ideal import _NavOrder as _NavOrder
    from quant_backtest_core.daily.execution_sim.orders_ideal import (
        _position_values_by_symbol as _position_values_by_symbol,
    )
    from quant_backtest_core.daily.execution_sim.orders_ideal import _price_at as _price_at
    from quant_backtest_core.daily.execution_sim.orders_ideal import (
        _rebalance_ideal_target as _rebalance_ideal_target,
    )
    from quant_backtest_core.daily.execution_sim.orders_ideal import (
        _record_nav_fill_audit as _record_nav_fill_audit,
    )
    from quant_backtest_core.daily.execution_sim.orders_ideal import _trade_fee as _trade_fee
    from quant_backtest_core.daily.execution_sim.orders_ideal import (
        _update_nav_order as _update_nav_order,
    )
    from quant_backtest_core.daily.execution_sim.orders_ideal import np as np
    from quant_backtest_core.daily.execution_sim.orders_ideal import pd as pd

sys.modules[__name__] = import_module("quant_backtest_core.daily.execution_sim.orders_ideal")
