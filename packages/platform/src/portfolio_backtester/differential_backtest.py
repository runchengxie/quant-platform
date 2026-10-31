"""Module alias preserving implementation identity during compatibility migration."""

import sys
from importlib import import_module
from typing import TYPE_CHECKING

__all__ = [
    "DIFFERENTIAL_BACKTEST_SCHEMA",
    "Any",
    "CanonicalBacktestResult",
    "DifferentialBacktestReport",
    "_assert_unique_comparison_keys",
    "_capability_differences",
    "_difference_summary",
    "_metric_columns",
    "_numeric_differences",
    "annotations",
    "compare_backtest_results",
    "dataclass",
]

if TYPE_CHECKING:
    from quant_platform._portfolio.differential_backtest import (
        DIFFERENTIAL_BACKTEST_SCHEMA,
        Any,
        CanonicalBacktestResult,
        DifferentialBacktestReport,
        _assert_unique_comparison_keys,
        _capability_differences,
        _difference_summary,
        _metric_columns,
        _numeric_differences,
        annotations,
        compare_backtest_results,
        dataclass,
    )

sys.modules[__name__] = import_module("quant_platform._portfolio.differential_backtest")
