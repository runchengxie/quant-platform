"""Module alias preserving implementation identity during compatibility migration."""

import sys
from importlib import import_module
from typing import TYPE_CHECKING

__all__ = [
    "EPSILON",
    "Any",
    "DayFlow",
    "Ledger",
    "StaggeredCohortExecutionConfig",
    "StaggeredCohortExecutionResult",
    "_append_cohort_snapshots",
    "_append_position_snapshots",
    "_generation_row",
    "_result_summary",
    "annotations",
    "append_day_outputs",
    "build_result",
    "check_conservation",
    "check_cost_identity",
    "cohort_nav",
    "finalize_generations",
    "generation_rows",
    "position_value",
]

if TYPE_CHECKING:
    from quant_platform._portfolio.staggered_cohort_execution_reporting import (
        EPSILON,
        Any,
        DayFlow,
        Ledger,
        StaggeredCohortExecutionConfig,
        StaggeredCohortExecutionResult,
        _append_cohort_snapshots,
        _append_position_snapshots,
        _generation_row,
        _result_summary,
        annotations,
        append_day_outputs,
        build_result,
        check_conservation,
        check_cost_identity,
        cohort_nav,
        finalize_generations,
        generation_rows,
        position_value,
    )

sys.modules[__name__] = import_module(
    "quant_platform._portfolio.staggered_cohort_execution_reporting"
)
