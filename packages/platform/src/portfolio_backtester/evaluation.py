"""Module alias preserving implementation identity during compatibility migration."""

import sys
from importlib import import_module
from typing import TYPE_CHECKING

__all__ = [
    "_build_period_positions",
    "_evaluate_walk_forward_backtest",
    "_execution_trade_fee_model",
    "_filter_positions_to_backtest_periods",
    "_rebalance_key",
    "_record_backtest_outputs",
    "_record_exposure_outputs",
    "_record_period_backtest_outputs",
    "_record_period_execution_sim",
    "_record_period_ideal_daily_nav",
    "_run_period_backtest",
    "_run_walk_forward_backtest_topk",
    "_score_walk_forward_backtest_frame",
    "_summarize_walk_forward_benchmark",
    "annotations",
    "evaluate_walk_forward_backtest",
]

if TYPE_CHECKING:
    from quant_platform._portfolio.evaluation import (
        _build_period_positions,
        _evaluate_walk_forward_backtest,
        _execution_trade_fee_model,
        _filter_positions_to_backtest_periods,
        _rebalance_key,
        _record_backtest_outputs,
        _record_exposure_outputs,
        _record_period_backtest_outputs,
        _record_period_execution_sim,
        _record_period_ideal_daily_nav,
        _run_period_backtest,
        _run_walk_forward_backtest_topk,
        _score_walk_forward_backtest_frame,
        _summarize_walk_forward_benchmark,
        annotations,
        evaluate_walk_forward_backtest,
    )

sys.modules[__name__] = import_module("quant_platform._portfolio.evaluation")
