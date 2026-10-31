"""Module alias preserving implementation identity during compatibility migration."""

import sys
from importlib import import_module
from typing import TYPE_CHECKING

__all__ = [
    "Any",
    "Mapping",
    "Sequence",
    "_apply_industry_labels_asof",
    "_as_numeric",
    "_build_industry_history",
    "_clean_categorical_labels",
    "_empty_industry_summary",
    "_finalize_industry_exposure",
    "_industry_exposure_rows",
    "_normalize_exposure_industry_source",
    "_normalize_exposure_positions",
    "_normalize_exposure_scored_data",
    "_resolve_exposure_industry_context",
    "_resolve_industry_column",
    "_to_datetime_series",
    "annotations",
    "canonicalize_symbol_columns",
]

if TYPE_CHECKING:
    from quant_platform._portfolio._exposure_industry import (
        Any,
        Mapping,
        Sequence,
        _apply_industry_labels_asof,
        _as_numeric,
        _build_industry_history,
        _clean_categorical_labels,
        _empty_industry_summary,
        _finalize_industry_exposure,
        _industry_exposure_rows,
        _normalize_exposure_industry_source,
        _normalize_exposure_positions,
        _normalize_exposure_scored_data,
        _resolve_exposure_industry_context,
        _resolve_industry_column,
        _to_datetime_series,
        annotations,
        canonicalize_symbol_columns,
    )

sys.modules[__name__] = import_module("quant_platform._portfolio._exposure_industry")
