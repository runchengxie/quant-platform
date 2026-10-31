"""Module alias preserving implementation identity during compatibility migration."""

import sys
from importlib import import_module
from typing import TYPE_CHECKING

__all__ = [
    "EPSILON",
    "TERMINAL_POLICY",
    "Any",
    "Cohort",
    "DayFlow",
    "Generation",
    "Ledger",
    "Position",
    "StaggeredCohortExecutionConfig",
    "StaggeredCohortExecutionResult",
    "annotations",
    "cohort_nav",
    "dataclass",
    "field",
    "ledger_nav",
    "position_value",
]

if TYPE_CHECKING:
    from quant_platform._portfolio.staggered_cohort_execution_state import (
        EPSILON,
        TERMINAL_POLICY,
        Any,
        Cohort,
        DayFlow,
        Generation,
        Ledger,
        Position,
        StaggeredCohortExecutionConfig,
        StaggeredCohortExecutionResult,
        annotations,
        cohort_nav,
        dataclass,
        field,
        ledger_nav,
        position_value,
    )

sys.modules[__name__] = import_module("quant_platform._portfolio.staggered_cohort_execution_state")
