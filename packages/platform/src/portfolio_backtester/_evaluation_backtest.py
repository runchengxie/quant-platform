"""Module alias preserving implementation identity during compatibility migration."""

import sys
from importlib import import_module
from typing import TYPE_CHECKING

__all__ = [
    "Any",
    "Callable",
    "Mapping",
    "_apply_freshness_overlay_if_configured",
    "_build_period_positions",
    "_evaluate_walk_forward_backtest",
    "_record_backtest_outputs",
    "_record_exposure_outputs",
    "_record_period_backtest_outputs",
    "_run_period_backtest",
    "_run_walk_forward_backtest_topk",
    "_score_walk_forward_backtest_frame",
    "_summarize_walk_forward_benchmark",
    "_warn_if_delay_exit_lag",
    "annotations",
    "apply_position_postprocess",
    "apply_score_postprocess_inplace",
    "backtest_topk",
    "build_benchmark_series",
    "build_positions_by_rebalance",
    "compute_backtest_exposure_analysis",
    "get_rebalance_dates",
    "logger",
    "summarize_active_returns",
    "summarize_period_returns",
]

if TYPE_CHECKING:
    from quant_platform._portfolio._evaluation_backtest import (
        Any,
        Callable,
        Mapping,
        _apply_freshness_overlay_if_configured,
        _build_period_positions,
        _evaluate_walk_forward_backtest,
        _record_backtest_outputs,
        _record_exposure_outputs,
        _record_period_backtest_outputs,
        _run_period_backtest,
        _run_walk_forward_backtest_topk,
        _score_walk_forward_backtest_frame,
        _summarize_walk_forward_benchmark,
        _warn_if_delay_exit_lag,
        annotations,
        apply_position_postprocess,
        apply_score_postprocess_inplace,
        backtest_topk,
        build_benchmark_series,
        build_positions_by_rebalance,
        compute_backtest_exposure_analysis,
        get_rebalance_dates,
        logger,
        summarize_active_returns,
        summarize_period_returns,
    )

sys.modules[__name__] = import_module("quant_platform._portfolio._evaluation_backtest")
