"""Module alias preserving implementation identity during compatibility migration."""

import sys
from importlib import import_module
from typing import TYPE_CHECKING

__all__ = [
    "Any",
    "PositionBacktestConfig",
    "PositionBacktestEvaluation",
    "PositionBacktestResult",
    "_period_records",
    "_prepare_benchmark_frame",
    "_return_frame",
    "_strategy_return_series",
    "annotations",
    "build_benchmark_series",
    "dataclass",
    "evaluate_position_backtest",
    "run_position_backtest",
    "summarize_active_returns",
    "summarize_period_returns",
]

if TYPE_CHECKING:
    from quant_platform._portfolio.position_evaluation import (
        Any,
        PositionBacktestConfig,
        PositionBacktestEvaluation,
        PositionBacktestResult,
        _period_records,
        _prepare_benchmark_frame,
        _return_frame,
        _strategy_return_series,
        annotations,
        build_benchmark_series,
        dataclass,
        evaluate_position_backtest,
        run_position_backtest,
        summarize_active_returns,
        summarize_period_returns,
    )

sys.modules[__name__] = import_module("quant_platform._portfolio.position_evaluation")
