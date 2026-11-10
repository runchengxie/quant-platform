"""Compatibility alias for the Engine-owned quant_backtest_core.daily.execution."""

from __future__ import annotations

import sys
from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from quant_backtest_core.daily.execution import BpsCostModel as BpsCostModel
    from quant_backtest_core.daily.execution import BpsSlippageModel as BpsSlippageModel
    from quant_backtest_core.daily.execution import CostModel as CostModel
    from quant_backtest_core.daily.execution import DatedFeeQuote as DatedFeeQuote
    from quant_backtest_core.daily.execution import DatedFeeSchedule as DatedFeeSchedule
    from quant_backtest_core.daily.execution import DatedTradeFeeModel as DatedTradeFeeModel
    from quant_backtest_core.daily.execution import DetailedTradeFeeModel as DetailedTradeFeeModel
    from quant_backtest_core.daily.execution import EntryPolicy as EntryPolicy
    from quant_backtest_core.daily.execution import ExecutionModel as ExecutionModel
    from quant_backtest_core.daily.execution import ExitFallbackPolicy as ExitFallbackPolicy
    from quant_backtest_core.daily.execution import ExitPolicy as ExitPolicy
    from quant_backtest_core.daily.execution import ExitPricePolicy as ExitPricePolicy
    from quant_backtest_core.daily.execution import FeeQuoteContext as FeeQuoteContext
    from quant_backtest_core.daily.execution import FeeSchedulePeriod as FeeSchedulePeriod
    from quant_backtest_core.daily.execution import NoCostModel as NoCostModel
    from quant_backtest_core.daily.execution import NoSlippageModel as NoSlippageModel
    from quant_backtest_core.daily.execution import (
        ParticipationSlippageModel as ParticipationSlippageModel,
    )
    from quant_backtest_core.daily.execution import SelectionConstraints as SelectionConstraints
    from quant_backtest_core.daily.execution import SideBpsCostModel as SideBpsCostModel
    from quant_backtest_core.daily.execution import SlippageModel as SlippageModel
    from quant_backtest_core.daily.execution import build_cost_model as build_cost_model
    from quant_backtest_core.daily.execution import build_entry_policy as build_entry_policy
    from quant_backtest_core.daily.execution import build_execution_model as build_execution_model
    from quant_backtest_core.daily.execution import build_exit_policy as build_exit_policy
    from quant_backtest_core.daily.execution import (
        build_selection_constraints as build_selection_constraints,
    )
    from quant_backtest_core.daily.execution import build_slippage_model as build_slippage_model
    from quant_backtest_core.daily.execution import describe_cost_model as describe_cost_model
    from quant_backtest_core.daily.execution import (
        describe_execution_model as describe_execution_model,
    )
    from quant_backtest_core.daily.execution import (
        describe_selection_constraints as describe_selection_constraints,
    )
    from quant_backtest_core.daily.execution import (
        describe_slippage_model as describe_slippage_model,
    )
    from quant_backtest_core.daily.execution import (
        l2_price_tiered_slippage as l2_price_tiered_slippage,
    )
    from quant_backtest_core.daily.execution import (
        required_pricing_columns as required_pricing_columns,
    )

sys.modules[__name__] = import_module("quant_backtest_core.daily.execution")
