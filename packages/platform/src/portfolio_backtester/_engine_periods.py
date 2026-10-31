"""Module alias preserving implementation identity during compatibility migration."""

import sys
from importlib import import_module
from typing import TYPE_CHECKING

__all__ = [
    "BacktestPeriodResult",
    "BacktestPositionState",
    "ExecutionSimConfig",
    "_BacktestLegContext",
    "_BacktestPeriodEvaluation",
    "_BacktestResultAccumulator",
    "_BacktestRunContext",
    "_BacktestTopKConfig",
    "_append_backtest_period_result",
    "_apply_liquidity_floor",
    "_build_backtest_return_bundle",
    "_build_ledger_positions",
    "_configured_leg_context",
    "_effective_cost_bps",
    "_evaluate_backtest_rebalance_period",
    "_evaluate_configured_long_only_period",
    "_evaluate_configured_long_short_period",
    "_evaluate_long_only_period",
    "_evaluate_long_short_period",
    "_prepare_backtest_run_context",
    "_resolve_ledger_config",
    "_run_backtest_config",
    "_run_backtest_periods",
    "annotations",
    "cast",
    "period_turnover_fields",
    "resolve_backtest_period_plan",
]

if TYPE_CHECKING:
    from quant_platform._portfolio._engine_periods import (
        BacktestPeriodResult,
        BacktestPositionState,
        ExecutionSimConfig,
        _append_backtest_period_result,
        _apply_liquidity_floor,
        _BacktestLegContext,
        _BacktestPeriodEvaluation,
        _BacktestResultAccumulator,
        _BacktestRunContext,
        _BacktestTopKConfig,
        _build_backtest_return_bundle,
        _build_ledger_positions,
        _configured_leg_context,
        _effective_cost_bps,
        _evaluate_backtest_rebalance_period,
        _evaluate_configured_long_only_period,
        _evaluate_configured_long_short_period,
        _evaluate_long_only_period,
        _evaluate_long_short_period,
        _prepare_backtest_run_context,
        _resolve_ledger_config,
        _run_backtest_config,
        _run_backtest_periods,
        annotations,
        cast,
        period_turnover_fields,
        resolve_backtest_period_plan,
    )

sys.modules[__name__] = import_module("quant_platform._portfolio._engine_periods")
