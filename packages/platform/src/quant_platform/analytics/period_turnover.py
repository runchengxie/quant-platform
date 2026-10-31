"""Module alias preserving implementation identity during compatibility migration."""

import sys
from importlib import import_module
from typing import TYPE_CHECKING

__all__ = [
    "BacktestLegResult",
    "BacktestPeriodResult",
    "_merged_names",
    "_optional_sum",
    "annotations",
    "period_result_from_leg",
    "period_result_from_legs",
    "period_turnover_fields",
]

if TYPE_CHECKING:
    from quant_platform._portfolio.period_turnover import (
        BacktestLegResult,
        BacktestPeriodResult,
        _merged_names,
        _optional_sum,
        annotations,
        period_result_from_leg,
        period_result_from_legs,
        period_turnover_fields,
    )

sys.modules[__name__] = import_module("quant_platform._portfolio.period_turnover")
