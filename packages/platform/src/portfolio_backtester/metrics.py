"""Module alias preserving implementation identity during compatibility migration."""

import sys
from importlib import import_module
from typing import TYPE_CHECKING

__all__ = [
    "_metrics_ic",
    "annotations",
    "daily_ic_series",
    "estimate_turnover",
    "leg_attribution_frame",
    "pearson_corr",
    "quantile_returns",
    "scipy_stats",
    "spearman_corr",
    "summarize_active_returns",
    "summarize_ic",
    "summarize_leg_attribution",
    "summarize_period_returns",
]

if TYPE_CHECKING:
    from quant_platform._portfolio.metrics import (
        _metrics_ic,
        annotations,
        daily_ic_series,
        estimate_turnover,
        leg_attribution_frame,
        pearson_corr,
        quantile_returns,
        scipy_stats,
        spearman_corr,
        summarize_active_returns,
        summarize_ic,
        summarize_leg_attribution,
        summarize_period_returns,
    )

sys.modules[__name__] = import_module("quant_platform._portfolio.metrics")
