"""Module alias preserving implementation identity during compatibility migration."""

import sys
from importlib import import_module
from typing import TYPE_CHECKING

__all__ = [
    "HK_CONNECT_CALENDAR",
    "MARKET_CALENDAR",
    "_HK_CONNECT_ALIASES",
    "_MARKET_ALIASES",
    "Any",
    "Iterable",
    "Mapping",
    "_date_range",
    "_fetch_trading_dates",
    "_normalize_dates",
    "_resolve_rqdatac_module",
    "_weekday_dates",
    "annotations",
    "build_execution_date_map",
    "cast",
    "coerce_date_set",
    "execution_calendar_from_config",
    "is_execution_open",
    "normalize_execution_calendar",
    "resolve_execution_date",
    "resolve_execution_open_dates",
]

if TYPE_CHECKING:
    from quant_platform._portfolio.execution_calendar import (
        _HK_CONNECT_ALIASES,
        _MARKET_ALIASES,
        HK_CONNECT_CALENDAR,
        MARKET_CALENDAR,
        Any,
        Iterable,
        Mapping,
        _date_range,
        _fetch_trading_dates,
        _normalize_dates,
        _resolve_rqdatac_module,
        _weekday_dates,
        annotations,
        build_execution_date_map,
        cast,
        coerce_date_set,
        execution_calendar_from_config,
        is_execution_open,
        normalize_execution_calendar,
        resolve_execution_date,
        resolve_execution_open_dates,
    )

sys.modules[__name__] = import_module("quant_platform._portfolio.execution_calendar")
