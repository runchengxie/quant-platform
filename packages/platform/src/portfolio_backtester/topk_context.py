"""Module alias preserving implementation identity during compatibility migration."""

import sys
from importlib import import_module
from typing import TYPE_CHECKING

__all__ = [
    "BacktestExecutionContext",
    "BacktestPeriodResult",
    "BacktestPositionState",
    "BacktestPricingContext",
    "BacktestSpec",
    "ExecutionModel",
    "Literal",
    "MaxNewNamesShortfallPolicy",
    "SelectionPricePolicy",
    "TargetWeightPolicy",
    "_BacktestPeriodEvaluation",
    "_BacktestResultAccumulator",
    "_BacktestRunContext",
    "_BacktestTopKConfig",
    "_build_backtest_return_bundle",
    "_build_backtest_spec_config",
    "_mean_period_field",
    "_merge_backtest_supplemental_columns",
    "_prepare_backtest_run_context",
    "annotations",
    "cast",
    "dataclass",
    "field",
    "normalize_backtest_frame",
    "normalize_weighting_mode",
    "prepare_backtest_pricing_context",
    "resolve_backtest_execution_context",
    "summarize_period_returns",
]

if TYPE_CHECKING:
    from quant_platform._portfolio.topk_context import (
        BacktestExecutionContext,
        BacktestPeriodResult,
        BacktestPositionState,
        BacktestPricingContext,
        BacktestSpec,
        ExecutionModel,
        Literal,
        MaxNewNamesShortfallPolicy,
        SelectionPricePolicy,
        TargetWeightPolicy,
        _BacktestPeriodEvaluation,
        _BacktestResultAccumulator,
        _BacktestRunContext,
        _BacktestTopKConfig,
        _build_backtest_return_bundle,
        _build_backtest_spec_config,
        _mean_period_field,
        _merge_backtest_supplemental_columns,
        _prepare_backtest_run_context,
        annotations,
        cast,
        dataclass,
        field,
        normalize_backtest_frame,
        normalize_weighting_mode,
        prepare_backtest_pricing_context,
        resolve_backtest_execution_context,
        summarize_period_returns,
    )

sys.modules[__name__] = import_module("quant_platform._portfolio.topk_context")
