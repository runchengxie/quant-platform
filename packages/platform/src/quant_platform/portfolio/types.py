"""Module alias preserving implementation identity during compatibility migration."""

import sys
from importlib import import_module
from typing import TYPE_CHECKING

__all__ = [
    "BacktestExecutionContext",
    "BacktestLegResult",
    "BacktestPeriodPlan",
    "BacktestPeriodResult",
    "BacktestPositionState",
    "BacktestPricingContext",
    "CostBreakdown",
    "CostModel",
    "EntryPolicy",
    "ExitPolicy",
    "SelectionConstraints",
    "SlippageModel",
    "TurnoverBreakdown",
    "annotations",
    "dataclass",
    "field",
]

if TYPE_CHECKING:
    from quant_platform._portfolio.types import (
        BacktestExecutionContext,
        BacktestLegResult,
        BacktestPeriodPlan,
        BacktestPeriodResult,
        BacktestPositionState,
        BacktestPricingContext,
        CostBreakdown,
        CostModel,
        EntryPolicy,
        ExitPolicy,
        SelectionConstraints,
        SlippageModel,
        TurnoverBreakdown,
        annotations,
        dataclass,
        field,
    )

sys.modules[__name__] = import_module("quant_platform._portfolio.types")
