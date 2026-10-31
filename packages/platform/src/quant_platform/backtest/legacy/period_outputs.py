"""Module alias preserving implementation identity during compatibility migration."""

import sys
from importlib import import_module
from typing import TYPE_CHECKING

__all__ = [
    "Any",
    "Mapping",
    "_build_period_positions",
    "_build_period_positions_impl",
    "_record_exposure_outputs",
    "_record_period_backtest_nav_outputs",
    "_record_period_backtest_outputs",
    "_record_period_execution_sim",
    "_record_period_exposure_outputs",
    "_record_period_ideal_daily_nav",
    "_run_period_backtest",
    "_sample_rebalance_frame",
    "annotations",
    "build_period_positions",
    "build_positions_by_rebalance",
    "rebuild_backtest_from_positions",
    "record_period_backtest_nav_outputs",
    "record_period_exposure_outputs",
]

if TYPE_CHECKING:
    from quant_platform._portfolio.period_outputs import (
        Any,
        Mapping,
        _build_period_positions,
        _build_period_positions_impl,
        _record_exposure_outputs,
        _record_period_backtest_nav_outputs,
        _record_period_backtest_outputs,
        _record_period_execution_sim,
        _record_period_exposure_outputs,
        _record_period_ideal_daily_nav,
        _run_period_backtest,
        _sample_rebalance_frame,
        annotations,
        build_period_positions,
        build_positions_by_rebalance,
        rebuild_backtest_from_positions,
        record_period_backtest_nav_outputs,
        record_period_exposure_outputs,
    )

sys.modules[__name__] = import_module("quant_platform._portfolio.period_outputs")
