"""Module alias preserving implementation identity during compatibility migration."""

import sys
from importlib import import_module
from typing import TYPE_CHECKING

__all__ = [
    "EXECUTION_SUMMARY_SCHEMA",
    "Any",
    "StaggeredCohortExecutionResult",
    "_numeric",
    "annotations",
    "cast",
    "execution_summary_frame",
    "summarize_staggered_execution",
]

if TYPE_CHECKING:
    from quant_platform._portfolio.execution_summary import (
        EXECUTION_SUMMARY_SCHEMA,
        Any,
        StaggeredCohortExecutionResult,
        _numeric,
        annotations,
        cast,
        execution_summary_frame,
        summarize_staggered_execution,
    )

sys.modules[__name__] = import_module("quant_platform._portfolio.execution_summary")
