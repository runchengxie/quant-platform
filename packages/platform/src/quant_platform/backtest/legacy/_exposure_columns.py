"""Module alias preserving implementation identity during compatibility migration."""

import sys
from importlib import import_module
from typing import TYPE_CHECKING

__all__ = [
    "_BETA_COLUMNS",
    "_DEFAULT_INDUSTRY_COLUMNS",
    "_LOW_VOL_COLUMNS",
    "_MISSING_LABEL_TOKENS",
    "_MOMENTUM_COLUMNS",
    "_QUALITY_COLUMNS",
    "_STYLE_FACTOR_ORDER",
    "Any",
    "Mapping",
    "Sequence",
    "_as_numeric",
    "_build_benchmark_daily_returns",
    "_build_beta_table",
    "_clean_categorical_labels",
    "_empty_exposure_result",
    "_empty_industry_summary",
    "_empty_style_summary",
    "_exposure_period_key",
    "_price_history_tables",
    "_resolve_industry_column",
    "_safe_log",
    "_to_datetime_series",
    "_update_factor_meta",
    "_weighted_average",
    "_zscore",
    "annotations",
    "canonicalize_symbol_columns",
    "cast",
]

if TYPE_CHECKING:
    from quant_platform._portfolio._exposure_columns import (
        _BETA_COLUMNS,
        _DEFAULT_INDUSTRY_COLUMNS,
        _LOW_VOL_COLUMNS,
        _MISSING_LABEL_TOKENS,
        _MOMENTUM_COLUMNS,
        _QUALITY_COLUMNS,
        _STYLE_FACTOR_ORDER,
        Any,
        Mapping,
        Sequence,
        _as_numeric,
        _build_benchmark_daily_returns,
        _build_beta_table,
        _clean_categorical_labels,
        _empty_exposure_result,
        _empty_industry_summary,
        _empty_style_summary,
        _exposure_period_key,
        _price_history_tables,
        _resolve_industry_column,
        _safe_log,
        _to_datetime_series,
        _update_factor_meta,
        _weighted_average,
        _zscore,
        annotations,
        canonicalize_symbol_columns,
        cast,
    )

sys.modules[__name__] = import_module("quant_platform._portfolio._exposure_columns")
