"""Compatibility alias for the Engine-owned quant_backtest_core.daily._execution_build."""

from __future__ import annotations

import sys
from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from quant_backtest_core.daily._execution_build import (
        _L2_HALF_SPREAD_TABLE as _L2_HALF_SPREAD_TABLE,
    )
    from quant_backtest_core.daily._execution_build import MARKET_CALENDAR as MARKET_CALENDAR
    from quant_backtest_core.daily._execution_build import Any as Any
    from quant_backtest_core.daily._execution_build import BpsCostModel as BpsCostModel
    from quant_backtest_core.daily._execution_build import BpsSlippageModel as BpsSlippageModel
    from quant_backtest_core.daily._execution_build import CostModel as CostModel
    from quant_backtest_core.daily._execution_build import (
        DetailedTradeFeeModel as DetailedTradeFeeModel,
    )
    from quant_backtest_core.daily._execution_build import EntryPolicy as EntryPolicy
    from quant_backtest_core.daily._execution_build import ExecutionModel as ExecutionModel
    from quant_backtest_core.daily._execution_build import ExitFallbackPolicy as ExitFallbackPolicy
    from quant_backtest_core.daily._execution_build import ExitPolicy as ExitPolicy
    from quant_backtest_core.daily._execution_build import ExitPricePolicy as ExitPricePolicy
    from quant_backtest_core.daily._execution_build import Mapping as Mapping
    from quant_backtest_core.daily._execution_build import NoCostModel as NoCostModel
    from quant_backtest_core.daily._execution_build import NoSlippageModel as NoSlippageModel
    from quant_backtest_core.daily._execution_build import (
        ParticipationSlippageModel as ParticipationSlippageModel,
    )
    from quant_backtest_core.daily._execution_build import (
        SelectionConstraints as SelectionConstraints,
    )
    from quant_backtest_core.daily._execution_build import SideBpsCostModel as SideBpsCostModel
    from quant_backtest_core.daily._execution_build import SlippageModel as SlippageModel
    from quant_backtest_core.daily._execution_build import (
        _build_detailed_trade_fee_model as _build_detailed_trade_fee_model,
    )
    from quant_backtest_core.daily._execution_build import (
        _coerce_non_negative_float as _coerce_non_negative_float,
    )
    from quant_backtest_core.daily._execution_build import (
        _coerce_positive_float as _coerce_positive_float,
    )
    from quant_backtest_core.daily._execution_build import _get_cost_alias as _get_cost_alias
    from quant_backtest_core.daily._execution_build import build_cost_model as build_cost_model
    from quant_backtest_core.daily._execution_build import build_entry_policy as build_entry_policy
    from quant_backtest_core.daily._execution_build import (
        build_execution_model as build_execution_model,
    )
    from quant_backtest_core.daily._execution_build import build_exit_policy as build_exit_policy
    from quant_backtest_core.daily._execution_build import (
        build_selection_constraints as build_selection_constraints,
    )
    from quant_backtest_core.daily._execution_build import (
        build_slippage_model as build_slippage_model,
    )
    from quant_backtest_core.daily._execution_build import cast as cast
    from quant_backtest_core.daily._execution_build import coerce_date_set as coerce_date_set
    from quant_backtest_core.daily._execution_build import (
        describe_cost_model as describe_cost_model,
    )
    from quant_backtest_core.daily._execution_build import (
        describe_execution_model as describe_execution_model,
    )
    from quant_backtest_core.daily._execution_build import (
        describe_selection_constraints as describe_selection_constraints,
    )
    from quant_backtest_core.daily._execution_build import (
        describe_slippage_model as describe_slippage_model,
    )
    from quant_backtest_core.daily._execution_build import (
        l2_price_tiered_slippage as l2_price_tiered_slippage,
    )
    from quant_backtest_core.daily._execution_build import (
        normalize_execution_calendar as normalize_execution_calendar,
    )
    from quant_backtest_core.daily._execution_build import np as np
    from quant_backtest_core.daily._execution_build import pd as pd
    from quant_backtest_core.daily._execution_build import (
        required_pricing_columns as required_pricing_columns,
    )

sys.modules[__name__] = import_module("quant_backtest_core.daily._execution_build")
