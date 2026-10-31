"""Module alias preserving implementation identity during compatibility migration."""

import sys
from importlib import import_module
from typing import TYPE_CHECKING

__all__ = [
    "DEFAULT_INDUSTRY_COLUMNS",
    "DEFAULT_STYLE_COLUMNS",
    "Any",
    "Sequence",
    "TurnoverAttributionResult",
    "_avg_abs_rank_change",
    "_empty_result",
    "_feature_attribution",
    "_first_existing",
    "_format_entry_date",
    "_industry_attribution",
    "_mean_or_zero",
    "_merge_asof_scored_columns",
    "_merge_scored_columns",
    "_normalize_positions",
    "_normalize_scored",
    "_parse_yyyymmdd",
    "_regime_attribution",
    "_resolve_feature_columns",
    "_side_weighted_mean",
    "_summary",
    "_trade_frame",
    "_window_turnover_rows",
    "annotations",
    "canonicalize_symbol_columns",
    "cast",
    "compute_turnover_attribution",
    "dataclass",
]

if TYPE_CHECKING:
    from quant_platform._portfolio.turnover_attribution import (
        DEFAULT_INDUSTRY_COLUMNS,
        DEFAULT_STYLE_COLUMNS,
        Any,
        Sequence,
        TurnoverAttributionResult,
        _avg_abs_rank_change,
        _empty_result,
        _feature_attribution,
        _first_existing,
        _format_entry_date,
        _industry_attribution,
        _mean_or_zero,
        _merge_asof_scored_columns,
        _merge_scored_columns,
        _normalize_positions,
        _normalize_scored,
        _parse_yyyymmdd,
        _regime_attribution,
        _resolve_feature_columns,
        _side_weighted_mean,
        _summary,
        _trade_frame,
        _window_turnover_rows,
        annotations,
        canonicalize_symbol_columns,
        cast,
        compute_turnover_attribution,
        dataclass,
    )

sys.modules[__name__] = import_module("quant_platform._portfolio.turnover_attribution")
