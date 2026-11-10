"""Engine alias: quant_backtest_core.daily.execution_sim.orders_nav_fees."""

from __future__ import annotations

import sys
from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from quant_backtest_core.daily.execution_sim.orders_nav_fees import (
        DatedTradeFeeModel as DatedTradeFeeModel,
    )
    from quant_backtest_core.daily.execution_sim.orders_nav_fees import (
        ExecutionSimConfig as ExecutionSimConfig,
    )
    from quant_backtest_core.daily.execution_sim.orders_nav_fees import (
        FeeQuoteContext as FeeQuoteContext,
    )
    from quant_backtest_core.daily.execution_sim.orders_nav_fees import (
        SlippageModel as SlippageModel,
    )
    from quant_backtest_core.daily.execution_sim.orders_nav_fees import (
        SupportedTradeFeeModel as SupportedTradeFeeModel,
    )
    from quant_backtest_core.daily.execution_sim.orders_nav_fees import (
        TradeFeeModel as TradeFeeModel,
    )
    from quant_backtest_core.daily.execution_sim.orders_nav_fees import (
        _accrue_nav_fee_quote as _accrue_nav_fee_quote,
    )
    from quant_backtest_core.daily.execution_sim.orders_nav_fees import (
        _ExecutionTables as _ExecutionTables,
    )
    from quant_backtest_core.daily.execution_sim.orders_nav_fees import (
        _nav_fee_group_id as _nav_fee_group_id,
    )
    from quant_backtest_core.daily.execution_sim.orders_nav_fees import (
        _nav_fee_order_id as _nav_fee_order_id,
    )
    from quant_backtest_core.daily.execution_sim.orders_nav_fees import (
        _nav_trade_fee as _nav_trade_fee,
    )
    from quant_backtest_core.daily.execution_sim.orders_nav_fees import _NavOrder as _NavOrder
    from quant_backtest_core.daily.execution_sim.orders_nav_fees import (
        _quote_trade_fee as _quote_trade_fee,
    )
    from quant_backtest_core.daily.execution_sim.orders_nav_fees import (
        _slippage_pricing_row as _slippage_pricing_row,
    )
    from quant_backtest_core.daily.execution_sim.orders_nav_fees import (
        _TradeFeeQuote as _TradeFeeQuote,
    )
    from quant_backtest_core.daily.execution_sim.orders_nav_fees import pd as pd

sys.modules[__name__] = import_module("quant_backtest_core.daily.execution_sim.orders_nav_fees")
