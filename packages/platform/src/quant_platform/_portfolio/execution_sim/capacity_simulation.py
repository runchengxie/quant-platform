"""Engine alias: quant_backtest_core.daily.execution_sim.capacity_simulation."""

from __future__ import annotations

import sys
from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from quant_backtest_core.daily.execution_sim.capacity_simulation import Any as Any
    from quant_backtest_core.daily.execution_sim.capacity_simulation import (
        ExecutionSimConfig as ExecutionSimConfig,
    )
    from quant_backtest_core.daily.execution_sim.capacity_simulation import (
        ExecutionSimResult as ExecutionSimResult,
    )
    from quant_backtest_core.daily.execution_sim.capacity_simulation import (
        SupportedTradeFeeModel as SupportedTradeFeeModel,
    )
    from quant_backtest_core.daily.execution_sim.capacity_simulation import (
        TradeFeeModel as TradeFeeModel,
    )
    from quant_backtest_core.daily.execution_sim.capacity_simulation import (
        _build_targets_by_rebalance as _build_targets_by_rebalance,
    )
    from quant_backtest_core.daily.execution_sim.capacity_simulation import (
        _empty_result as _empty_result,
    )
    from quant_backtest_core.daily.execution_sim.capacity_simulation import (
        _execute_buy_orders as _execute_buy_orders,
    )
    from quant_backtest_core.daily.execution_sim.capacity_simulation import (
        _execute_capacity_rebalance as _execute_capacity_rebalance,
    )
    from quant_backtest_core.daily.execution_sim.capacity_simulation import (
        _execute_sell_orders as _execute_sell_orders,
    )
    from quant_backtest_core.daily.execution_sim.capacity_simulation import (
        _ExecutionTables as _ExecutionTables,
    )
    from quant_backtest_core.daily.execution_sim.capacity_simulation import (
        _fill_columns as _fill_columns,
    )
    from quant_backtest_core.daily.execution_sim.capacity_simulation import (
        _order_columns as _order_columns,
    )
    from quant_backtest_core.daily.execution_sim.capacity_simulation import _OrderSink as _OrderSink
    from quant_backtest_core.daily.execution_sim.capacity_simulation import (
        _prepare_execution_tables as _prepare_execution_tables,
    )
    from quant_backtest_core.daily.execution_sim.capacity_simulation import (
        _prepare_long_only_execution_positions as _prepare_long_only_execution_positions,
    )
    from quant_backtest_core.daily.execution_sim.capacity_simulation import (
        _run_capacity_rebalances as _run_capacity_rebalances,
    )
    from quant_backtest_core.daily.execution_sim.capacity_simulation import (
        _summarize_orders as _summarize_orders,
    )
    from quant_backtest_core.daily.execution_sim.capacity_simulation import pd as pd
    from quant_backtest_core.daily.execution_sim.capacity_simulation import (
        simulate_capacity_execution as simulate_capacity_execution,
    )

sys.modules[__name__] = import_module("quant_backtest_core.daily.execution_sim.capacity_simulation")
