"""Module alias preserving implementation identity during compatibility migration."""

import sys
from importlib import import_module
from typing import TYPE_CHECKING

__all__ = [
    "Any",
    "_annualized_return",
    "_calendar_half_year_split",
    "_calendar_year_split",
    "_distribution_stats",
    "_drawdown_timing",
    "_empty_drawdown_timing",
    "_empty_period_return_summary",
    "_exit_lag_stats",
    "_holding_period_stats",
    "_index_day_distance",
    "_period_exit_lag",
    "_recovery_timing",
    "_risk_adjusted_stats",
    "annotations",
    "cast",
    "summarize_period_returns",
    "yearly_compounded_returns",
]

if TYPE_CHECKING:
    from quant_platform._portfolio._metrics_period import (
        Any,
        _annualized_return,
        _calendar_half_year_split,
        _calendar_year_split,
        _distribution_stats,
        _drawdown_timing,
        _empty_drawdown_timing,
        _empty_period_return_summary,
        _exit_lag_stats,
        _holding_period_stats,
        _index_day_distance,
        _period_exit_lag,
        _recovery_timing,
        _risk_adjusted_stats,
        annotations,
        cast,
        summarize_period_returns,
        yearly_compounded_returns,
    )

sys.modules[__name__] = import_module("quant_platform._portfolio._metrics_period")
