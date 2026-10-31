"""Module alias preserving implementation identity during compatibility migration."""

import sys
from importlib import import_module
from typing import TYPE_CHECKING

__all__ = [
    "DEFAULT_EXECUTION_COMPARISON_METRICS",
    "_RESERVED_OUTPUT_COLUMNS",
    "Any",
    "Sequence",
    "_paired_metric_rows",
    "_validate_comparison_options",
    "annotations",
    "cast",
    "compare_paired_execution_metrics",
]

if TYPE_CHECKING:
    from quant_platform._portfolio.execution_comparison import (
        _RESERVED_OUTPUT_COLUMNS,
        DEFAULT_EXECUTION_COMPARISON_METRICS,
        Any,
        Sequence,
        _paired_metric_rows,
        _validate_comparison_options,
        annotations,
        cast,
        compare_paired_execution_metrics,
    )

sys.modules[__name__] = import_module("quant_platform._portfolio.execution_comparison")
