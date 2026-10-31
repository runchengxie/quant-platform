"""Module alias preserving implementation identity during compatibility migration."""

import sys
from importlib import import_module
from typing import TYPE_CHECKING

__all__ = [
    "_ANCHORED_MULTIWEEK_PATTERN",
    "_MULTIWEEK_PATTERN",
    "Iterable",
    "Literal",
    "SessionRebalanceSchedule",
    "SupportsIndex",
    "_MultiweekFrequency",
    "_clean_dates",
    "_multiweek_rebalance_dates",
    "_parse_anchor",
    "_parse_multiweek_frequency",
    "_period_end_dates",
    "_positive_session_interval",
    "_sample_rebalance_frame",
    "_session_phase",
    "_timestamp_set",
    "annotations",
    "cast",
    "dataclass",
    "estimate_rebalance_gap",
    "get_rebalance_dates",
    "get_rebalance_events",
    "get_session_interval_rebalance_dates",
    "sample_rebalance_frame",
]

if TYPE_CHECKING:
    from quant_platform._portfolio.rebalance import (
        _ANCHORED_MULTIWEEK_PATTERN,
        _MULTIWEEK_PATTERN,
        Iterable,
        Literal,
        SessionRebalanceSchedule,
        SupportsIndex,
        _clean_dates,
        _multiweek_rebalance_dates,
        _MultiweekFrequency,
        _parse_anchor,
        _parse_multiweek_frequency,
        _period_end_dates,
        _positive_session_interval,
        _sample_rebalance_frame,
        _session_phase,
        _timestamp_set,
        annotations,
        cast,
        dataclass,
        estimate_rebalance_gap,
        get_rebalance_dates,
        get_rebalance_events,
        get_session_interval_rebalance_dates,
        sample_rebalance_frame,
    )

sys.modules[__name__] = import_module("quant_platform._portfolio.rebalance")
