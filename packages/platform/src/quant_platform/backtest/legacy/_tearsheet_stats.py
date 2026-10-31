"""Module alias preserving implementation identity during compatibility migration."""

import sys
from importlib import import_module
from typing import TYPE_CHECKING

__all__ = [
    "Any",
    "Mapping",
    "_cumulative_frame",
    "_cvar_95",
    "_daily_nav_series",
    "_is_finite",
    "_layer_nav_frame",
    "_merge_stats",
    "_metric",
    "_prepare_returns",
    "_resolve_periods_per_year",
    "_rolling_sharpe",
    "_rolling_sharpe_frame",
    "_summarize_series",
    "annotations",
]

if TYPE_CHECKING:
    from quant_platform._portfolio._tearsheet_stats import (
        Any,
        Mapping,
        _cumulative_frame,
        _cvar_95,
        _daily_nav_series,
        _is_finite,
        _layer_nav_frame,
        _merge_stats,
        _metric,
        _prepare_returns,
        _resolve_periods_per_year,
        _rolling_sharpe,
        _rolling_sharpe_frame,
        _summarize_series,
        annotations,
    )

sys.modules[__name__] = import_module("quant_platform._portfolio._tearsheet_stats")
