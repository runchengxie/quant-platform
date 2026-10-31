"""Module alias preserving implementation identity during compatibility migration."""

import sys
from importlib import import_module
from typing import TYPE_CHECKING

__all__ = [
    "_STYLE_FACTOR_ORDER",
    "Any",
    "Mapping",
    "Sequence",
    "_add_industry_summary",
    "_add_style_summary",
    "_apply_industry_labels_asof",
    "_build_active_exposure_summary_table",
    "_build_benchmark_daily_returns",
    "_build_beta_table",
    "_build_exposure_rows",
    "_build_exposure_summary_row",
    "_empty_exposure_result",
    "_exposure_period_key",
    "_exposure_summary_periods",
    "_finalize_industry_exposure",
    "_finalize_style_exposure",
    "_industry_exposure_rows",
    "_normalize_exposure_industry_source",
    "_normalize_exposure_positions",
    "_normalize_exposure_scored_data",
    "_normalize_exposure_summary_dates",
    "_price_history_tables",
    "_resolve_exposure_industry_context",
    "_style_rows_for_rebalance",
    "annotations",
    "cast",
    "compute_backtest_exposure_analysis",
]

if TYPE_CHECKING:
    from quant_platform._portfolio._exposure_assemble import (
        _STYLE_FACTOR_ORDER,
        Any,
        Mapping,
        Sequence,
        _add_industry_summary,
        _add_style_summary,
        _apply_industry_labels_asof,
        _build_active_exposure_summary_table,
        _build_benchmark_daily_returns,
        _build_beta_table,
        _build_exposure_rows,
        _build_exposure_summary_row,
        _empty_exposure_result,
        _exposure_period_key,
        _exposure_summary_periods,
        _finalize_industry_exposure,
        _finalize_style_exposure,
        _industry_exposure_rows,
        _normalize_exposure_industry_source,
        _normalize_exposure_positions,
        _normalize_exposure_scored_data,
        _normalize_exposure_summary_dates,
        _price_history_tables,
        _resolve_exposure_industry_context,
        _style_rows_for_rebalance,
        annotations,
        cast,
        compute_backtest_exposure_analysis,
    )

sys.modules[__name__] = import_module("quant_platform._portfolio._exposure_assemble")
