"""Module alias preserving implementation identity during compatibility migration."""

import sys
from importlib import import_module
from typing import TYPE_CHECKING

__all__ = [
    "_ROLLING_REPORT_YEARS",
    "_SLUG_PATTERN",
    "Any",
    "Mapping",
    "Sequence",
    "_extract_periods_per_year",
    "_infer_periods_per_year",
    "_layer_comparison_row",
    "_metric_value",
    "_nested_stats",
    "_prepare_series",
    "_rolling_cagr",
    "_rolling_max_drawdown",
    "_rolling_window_obs",
    "_window_max_drawdown",
    "annotations",
    "build_backtest_layer_comparison_frame",
    "build_backtest_report",
    "build_benchmark_compare_entry",
    "build_benchmark_compare_summary_frame",
    "build_benchmark_series",
    "cast",
    "slugify_report_name",
    "summarize_active_returns",
    "summarize_period_returns",
]

if TYPE_CHECKING:
    from quant_platform._portfolio.reporting import (
        _ROLLING_REPORT_YEARS,
        _SLUG_PATTERN,
        Any,
        Mapping,
        Sequence,
        _extract_periods_per_year,
        _infer_periods_per_year,
        _layer_comparison_row,
        _metric_value,
        _nested_stats,
        _prepare_series,
        _rolling_cagr,
        _rolling_max_drawdown,
        _rolling_window_obs,
        _window_max_drawdown,
        annotations,
        build_backtest_layer_comparison_frame,
        build_backtest_report,
        build_benchmark_compare_entry,
        build_benchmark_compare_summary_frame,
        build_benchmark_series,
        cast,
        slugify_report_name,
        summarize_active_returns,
        summarize_period_returns,
    )

sys.modules[__name__] = import_module("quant_platform._portfolio.reporting")
