"""Portfolio turnover accounting with price-induced weight drift."""

from __future__ import annotations

from typing import cast as cast

from quant_backtest_core.daily.trade_accounting import (
    compute_trade_summary as compute_trade_summary,
)
from quant_backtest_core.daily.trade_accounting import (
    drift_previous_weights as drift_previous_weights,
)

from .portfolio_weights import normalize_position_weights as normalize_position_weights

# Compatibility aliases for callers migrating private orchestration helpers.
_compute_trade_summary = compute_trade_summary
_drift_previous_weights = drift_previous_weights


__all__ = [
    "_compute_trade_summary",
    "_drift_previous_weights",
    "compute_trade_summary",
    "drift_previous_weights",
]
