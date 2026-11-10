"""Engine alias: quant_backtest_core.daily.execution_sim.orders_nav."""

from __future__ import annotations

import sys
from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from quant_backtest_core.daily.execution_sim.orders_nav import Any as Any
    from quant_backtest_core.daily.execution_sim.orders_nav import CostBreakdown as CostBreakdown
    from quant_backtest_core.daily.execution_sim.orders_nav import (
        DatedTradeFeeModel as DatedTradeFeeModel,
    )
    from quant_backtest_core.daily.execution_sim.orders_nav import (
        ExecutionSimConfig as ExecutionSimConfig,
    )
    from quant_backtest_core.daily.execution_sim.orders_nav import SlippageModel as SlippageModel
    from quant_backtest_core.daily.execution_sim.orders_nav import (
        SupportedTradeFeeModel as SupportedTradeFeeModel,
    )
    from quant_backtest_core.daily.execution_sim.orders_nav import TradeFeeModel as TradeFeeModel
    from quant_backtest_core.daily.execution_sim.orders_nav import (
        _accrue_nav_fee_quote as _accrue_nav_fee_quote,
    )
    from quant_backtest_core.daily.execution_sim.orders_nav import _add_breakdown as _add_breakdown
    from quant_backtest_core.daily.execution_sim.orders_nav import (
        _affordable_nav_buy_fill as _affordable_nav_buy_fill,
    )
    from quant_backtest_core.daily.execution_sim.orders_nav import (
        _append_nav_order_row as _append_nav_order_row,
    )
    from quant_backtest_core.daily.execution_sim.orders_nav import (
        _append_order_rows as _append_order_rows,
    )
    from quant_backtest_core.daily.execution_sim.orders_nav import (
        _apply_buy_day_fills as _apply_buy_day_fills,
    )
    from quant_backtest_core.daily.execution_sim.orders_nav import (
        _apply_nav_buy_fill as _apply_nav_buy_fill,
    )
    from quant_backtest_core.daily.execution_sim.orders_nav import (
        _apply_nav_buy_fills as _apply_nav_buy_fills,
    )
    from quant_backtest_core.daily.execution_sim.orders_nav import (
        _apply_nav_sell_fill as _apply_nav_sell_fill,
    )
    from quant_backtest_core.daily.execution_sim.orders_nav import (
        _build_order_states as _build_order_states,
    )
    from quant_backtest_core.daily.execution_sim.orders_nav import (
        _capacity_notional as _capacity_notional,
    )
    from quant_backtest_core.daily.execution_sim.orders_nav import (
        _capacity_weight as _capacity_weight,
    )
    from quant_backtest_core.daily.execution_sim.orders_nav import (
        _execute_buy_orders as _execute_buy_orders,
    )
    from quant_backtest_core.daily.execution_sim.orders_nav import (
        _execute_nav_buy_orders_for_day as _execute_nav_buy_orders_for_day,
    )
    from quant_backtest_core.daily.execution_sim.orders_nav import (
        _execute_nav_orders_for_day as _execute_nav_orders_for_day,
    )
    from quant_backtest_core.daily.execution_sim.orders_nav import (
        _execute_nav_sell_orders_for_day as _execute_nav_sell_orders_for_day,
    )
    from quant_backtest_core.daily.execution_sim.orders_nav import (
        _execute_sell_orders as _execute_sell_orders,
    )
    from quant_backtest_core.daily.execution_sim.orders_nav import (
        _execution_window_dates as _execution_window_dates,
    )
    from quant_backtest_core.daily.execution_sim.orders_nav import (
        _ExecutionTables as _ExecutionTables,
    )
    from quant_backtest_core.daily.execution_sim.orders_nav import (
        _finalize_open_nav_orders as _finalize_open_nav_orders,
    )
    from quant_backtest_core.daily.execution_sim.orders_nav import _limit_down_at as _limit_down_at
    from quant_backtest_core.daily.execution_sim.orders_nav import _limit_up_at as _limit_up_at
    from quant_backtest_core.daily.execution_sim.orders_nav import (
        _listing_status_at as _listing_status_at,
    )
    from quant_backtest_core.daily.execution_sim.orders_nav import _MarketRules as _MarketRules
    from quant_backtest_core.daily.execution_sim.orders_nav import (
        _nav_buy_cash_required as _nav_buy_cash_required,
    )
    from quant_backtest_core.daily.execution_sim.orders_nav import (
        _nav_fee_group_id as _nav_fee_group_id,
    )
    from quant_backtest_core.daily.execution_sim.orders_nav import (
        _nav_fee_order_id as _nav_fee_order_id,
    )
    from quant_backtest_core.daily.execution_sim.orders_nav import (
        _nav_order_is_complete as _nav_order_is_complete,
    )
    from quant_backtest_core.daily.execution_sim.orders_nav import (
        _nav_order_should_abort_buy as _nav_order_should_abort_buy,
    )
    from quant_backtest_core.daily.execution_sim.orders_nav import _nav_trade_fee as _nav_trade_fee
    from quant_backtest_core.daily.execution_sim.orders_nav import _NavOrder as _NavOrder
    from quant_backtest_core.daily.execution_sim.orders_nav import _OrderSink as _OrderSink
    from quant_backtest_core.daily.execution_sim.orders_nav import _price_at as _price_at
    from quant_backtest_core.daily.execution_sim.orders_nav import (
        _quantize_nav_sell_quantity as _quantize_nav_sell_quantity,
    )
    from quant_backtest_core.daily.execution_sim.orders_nav import _record_fill as _record_fill
    from quant_backtest_core.daily.execution_sim.orders_nav import (
        _record_nav_fill_audit as _record_nav_fill_audit,
    )
    from quant_backtest_core.daily.execution_sim.orders_nav import (
        _slippage_pricing_row as _slippage_pricing_row,
    )
    from quant_backtest_core.daily.execution_sim.orders_nav import (
        _update_nav_order as _update_nav_order,
    )
    from quant_backtest_core.daily.execution_sim.orders_nav import _update_state as _update_state
    from quant_backtest_core.daily.execution_sim.orders_nav import np as np
    from quant_backtest_core.daily.execution_sim.orders_nav import pd as pd

sys.modules[__name__] = import_module("quant_backtest_core.daily.execution_sim.orders_nav")
