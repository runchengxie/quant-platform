"""Module alias preserving implementation identity during compatibility migration."""

import sys
from importlib import import_module
from typing import TYPE_CHECKING

__all__ = [
    "BacktestPeriodPlan",
    "Literal",
    "_label_horizon_exit_index",
    "_resolve_planned_exit_index",
    "annotations",
    "resolve_backtest_period_plan",
    "resolve_execution_date",
]

if TYPE_CHECKING:
    from quant_platform._portfolio.periods import (
        BacktestPeriodPlan,
        Literal,
        _label_horizon_exit_index,
        _resolve_planned_exit_index,
        annotations,
        resolve_backtest_period_plan,
        resolve_execution_date,
    )

sys.modules[__name__] = import_module("quant_platform._portfolio.periods")
