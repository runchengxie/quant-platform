"""Module alias preserving implementation identity during compatibility migration."""

import sys
from importlib import import_module
from typing import TYPE_CHECKING

__all__ = [
    "Any",
    "Mapping",
    "Path",
    "SupportsInt",
    "_normalize_backtest_postprocess_config",
    "_normalize_backtest_tearsheet_enabled",
    "_normalize_benchmark_compare",
    "_normalize_benchmark_compare_item",
    "_normalize_optional_text",
    "_normalize_positive_int_or_none",
    "_optional_text",
    "_resolve_backtest_benchmark_settings",
    "_resolve_backtest_exit_settings",
    "_resolve_backtest_group_col",
    "_resolve_backtest_postprocess_settings",
    "_resolve_backtest_signal_direction",
    "_resolve_backtest_weighting",
    "_resolve_selection_score_settings",
    "annotations",
    "cast",
    "resolve_backtest_base_settings",
]

if TYPE_CHECKING:
    from quant_platform._portfolio.backtest_config import (
        Any,
        Mapping,
        Path,
        SupportsInt,
        _normalize_backtest_postprocess_config,
        _normalize_backtest_tearsheet_enabled,
        _normalize_benchmark_compare,
        _normalize_benchmark_compare_item,
        _normalize_optional_text,
        _normalize_positive_int_or_none,
        _optional_text,
        _resolve_backtest_benchmark_settings,
        _resolve_backtest_exit_settings,
        _resolve_backtest_group_col,
        _resolve_backtest_postprocess_settings,
        _resolve_backtest_signal_direction,
        _resolve_backtest_weighting,
        _resolve_selection_score_settings,
        annotations,
        cast,
        resolve_backtest_base_settings,
    )

sys.modules[__name__] = import_module("quant_platform._portfolio.backtest_config")
