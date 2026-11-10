"""Engine alias: quant_backtest_core.daily.execution_sim.reporting."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from quant_backtest_core.daily.execution_sim import reporting as _owned

from ..metrics import summarize_period_returns as summarize_period_returns

if TYPE_CHECKING:
    from quant_backtest_core.daily.execution_sim.reporting import Any as Any
    from quant_backtest_core.daily.execution_sim.reporting import (
        ExecutionAdjustedNavResult as ExecutionAdjustedNavResult,
    )
    from quant_backtest_core.daily.execution_sim.reporting import (
        ExecutionSimConfig as ExecutionSimConfig,
    )
    from quant_backtest_core.daily.execution_sim.reporting import (
        ExecutionSimResult as ExecutionSimResult,
    )
    from quant_backtest_core.daily.execution_sim.reporting import (
        SupportedTradeFeeModel as SupportedTradeFeeModel,
    )
    from quant_backtest_core.daily.execution_sim.reporting import TradeFeeModel as TradeFeeModel
    from quant_backtest_core.daily.execution_sim.reporting import (
        _daily_period_info as _daily_period_info,
    )
    from quant_backtest_core.daily.execution_sim.reporting import (
        _empty_adjusted_nav_result as _empty_adjusted_nav_result,
    )
    from quant_backtest_core.daily.execution_sim.reporting import _empty_result as _empty_result
    from quant_backtest_core.daily.execution_sim.reporting import (
        _executed_daily_columns as _executed_daily_columns,
    )
    from quant_backtest_core.daily.execution_sim.reporting import _fill_columns as _fill_columns
    from quant_backtest_core.daily.execution_sim.reporting import _format_date as _format_date
    from quant_backtest_core.daily.execution_sim.reporting import (
        _market_rule_warnings as _market_rule_warnings,
    )
    from quant_backtest_core.daily.execution_sim.reporting import (
        _nav_fill_columns as _nav_fill_columns,
    )
    from quant_backtest_core.daily.execution_sim.reporting import (
        _nav_order_columns as _nav_order_columns,
    )
    from quant_backtest_core.daily.execution_sim.reporting import (
        _nav_side_fill_ratio as _nav_side_fill_ratio,
    )
    from quant_backtest_core.daily.execution_sim.reporting import _order_columns as _order_columns
    from quant_backtest_core.daily.execution_sim.reporting import (
        _side_fill_ratio as _side_fill_ratio,
    )
    from quant_backtest_core.daily.execution_sim.reporting import (
        _summarize_adjusted_nav as _summarize_adjusted_nav,
    )
    from quant_backtest_core.daily.execution_sim.reporting import (
        _summarize_orders as _summarize_orders,
    )
    from quant_backtest_core.daily.execution_sim.reporting import asdict as asdict
    from quant_backtest_core.daily.execution_sim.reporting import cast as cast
    from quant_backtest_core.daily.execution_sim.reporting import (
        describe_execution_sim_config as describe_execution_sim_config,
    )
    from quant_backtest_core.daily.execution_sim.reporting import (
        describe_trade_fee_model as describe_trade_fee_model,
    )
    from quant_backtest_core.daily.execution_sim.reporting import np as np
    from quant_backtest_core.daily.execution_sim.reporting import pd as pd
    from quant_backtest_core.daily.execution_sim.reporting import (
        summarize_execution as summarize_execution,
    )


def __getattr__(name: str) -> Any:
    return getattr(_owned, name)
