"""Module alias preserving implementation identity during compatibility migration."""

import sys
from importlib import import_module
from typing import TYPE_CHECKING

__all__ = [
    "Any",
    "_empty_ic_summary",
    "annotations",
    "cast",
    "daily_ic_series",
    "leg_attribution_frame",
    "pearson_corr",
    "quantile_returns",
    "spearman_corr",
    "summarize_ic",
    "summarize_leg_attribution",
]

if TYPE_CHECKING:
    from quant_platform._portfolio._metrics_ic import (
        Any,
        _empty_ic_summary,
        annotations,
        cast,
        daily_ic_series,
        leg_attribution_frame,
        pearson_corr,
        quantile_returns,
        spearman_corr,
        summarize_ic,
        summarize_leg_attribution,
    )

sys.modules[__name__] = import_module("quant_platform._portfolio._metrics_ic")
