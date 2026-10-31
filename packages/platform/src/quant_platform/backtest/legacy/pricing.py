"""Module alias preserving implementation identity during compatibility migration."""

import sys
from importlib import import_module
from typing import TYPE_CHECKING

__all__ = [
    "BacktestExecutionContext",
    "BacktestPricingContext",
    "BpsCostModel",
    "EntryPolicy",
    "ExecutionModel",
    "ExitPolicy",
    "Literal",
    "NoSlippageModel",
    "ParticipationSlippageModel",
    "SelectionConstraints",
    "SlippageModel",
    "annotations",
    "assert_backtest_pricing_frame",
    "canonicalize_symbol_columns",
    "cast",
    "normalize_backtest_frame",
    "prepare_backtest_pricing_context",
    "resolve_backtest_execution_context",
    "slippage_pricing_row",
]

if TYPE_CHECKING:
    from quant_platform._portfolio.pricing import (
        BacktestExecutionContext,
        BacktestPricingContext,
        BpsCostModel,
        EntryPolicy,
        ExecutionModel,
        ExitPolicy,
        Literal,
        NoSlippageModel,
        ParticipationSlippageModel,
        SelectionConstraints,
        SlippageModel,
        annotations,
        assert_backtest_pricing_frame,
        canonicalize_symbol_columns,
        cast,
        normalize_backtest_frame,
        prepare_backtest_pricing_context,
        resolve_backtest_execution_context,
        slippage_pricing_row,
    )

sys.modules[__name__] = import_module("quant_platform._portfolio.pricing")
