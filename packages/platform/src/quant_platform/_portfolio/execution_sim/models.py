"""Engine alias: quant_backtest_core.daily.execution_sim.models."""

from __future__ import annotations

import sys
from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from quant_backtest_core.daily.execution_sim.models import Any as Any
    from quant_backtest_core.daily.execution_sim.models import CostBreakdown as CostBreakdown
    from quant_backtest_core.daily.execution_sim.models import DatedFeeQuote as DatedFeeQuote
    from quant_backtest_core.daily.execution_sim.models import (
        DatedTradeFeeModel as DatedTradeFeeModel,
    )
    from quant_backtest_core.daily.execution_sim.models import (
        DetailedTradeFeeModel as DetailedTradeFeeModel,
    )
    from quant_backtest_core.daily.execution_sim.models import (
        ExecutionSimConfig as ExecutionSimConfig,
    )
    from quant_backtest_core.daily.execution_sim.models import FeeQuoteContext as FeeQuoteContext
    from quant_backtest_core.daily.execution_sim.models import (
        PreparedExecutionTables as PreparedExecutionTables,
    )
    from quant_backtest_core.daily.execution_sim.models import SlippageModel as SlippageModel
    from quant_backtest_core.daily.execution_sim.models import (
        SupportedTradeFeeModel as SupportedTradeFeeModel,
    )
    from quant_backtest_core.daily.execution_sim.models import TradeFeeModel as TradeFeeModel
    from quant_backtest_core.daily.execution_sim.models import _add_breakdown as _add_breakdown
    from quant_backtest_core.daily.execution_sim.models import (
        _AdjustedNavLedger as _AdjustedNavLedger,
    )
    from quant_backtest_core.daily.execution_sim.models import _AdjustedNavPlan as _AdjustedNavPlan
    from quant_backtest_core.daily.execution_sim.models import (
        _CorporateActionLedger as _CorporateActionLedger,
    )
    from quant_backtest_core.daily.execution_sim.models import _ExecutionTables as _ExecutionTables
    from quant_backtest_core.daily.execution_sim.models import _MarketRules as _MarketRules
    from quant_backtest_core.daily.execution_sim.models import _NavOrder as _NavOrder
    from quant_backtest_core.daily.execution_sim.models import _OrderSink as _OrderSink
    from quant_backtest_core.daily.execution_sim.models import _quote_trade_fee as _quote_trade_fee
    from quant_backtest_core.daily.execution_sim.models import _trade_fee as _trade_fee
    from quant_backtest_core.daily.execution_sim.models import _TradeFeeQuote as _TradeFeeQuote
    from quant_backtest_core.daily.execution_sim.models import (
        _with_dated_fee_context as _with_dated_fee_context,
    )
    from quant_backtest_core.daily.execution_sim.models import dataclass as dataclass
    from quant_backtest_core.daily.execution_sim.models import date as date
    from quant_backtest_core.daily.execution_sim.models import (
        describe_trade_fee_model as describe_trade_fee_model,
    )
    from quant_backtest_core.daily.execution_sim.models import np as np
    from quant_backtest_core.daily.execution_sim.models import pd as pd

sys.modules[__name__] = import_module("quant_backtest_core.daily.execution_sim.models")
