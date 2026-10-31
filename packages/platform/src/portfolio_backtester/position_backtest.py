"""Module alias preserving implementation identity during compatibility migration."""

import sys
from importlib import import_module
from typing import TYPE_CHECKING

__all__ = [
    "PositionBacktestConfig",
    "PositionBacktestResult",
    "PositionExitPolicy",
    "add_position_backtest_args",
    "annotations",
    "normalize_position_backtest_periods",
    "normalize_position_backtest_positions",
    "normalize_position_backtest_pricing",
    "run",
    "run_position_backtest",
]

if TYPE_CHECKING:
    from quant_platform._portfolio.position_backtest import (
        PositionBacktestConfig,
        PositionBacktestResult,
        PositionExitPolicy,
        add_position_backtest_args,
        annotations,
        normalize_position_backtest_periods,
        normalize_position_backtest_positions,
        normalize_position_backtest_pricing,
        run,
        run_position_backtest,
    )

sys.modules[__name__] = import_module("quant_platform._portfolio.position_backtest")
