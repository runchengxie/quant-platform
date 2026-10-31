"""Module alias preserving implementation identity during compatibility migration."""

import sys
from importlib import import_module
from typing import TYPE_CHECKING

__all__ = [
    "VALUATION_LEDGER_COLUMNS",
    "Iterable",
    "ValuationEvent",
    "_market_timezone",
    "annotations",
    "cast",
    "dataclass",
    "datetime",
    "isfinite",
    "normalize_valuation_events",
    "replace",
]

if TYPE_CHECKING:
    from quant_platform._portfolio.valuation_events import (
        VALUATION_LEDGER_COLUMNS,
        Iterable,
        ValuationEvent,
        _market_timezone,
        annotations,
        cast,
        dataclass,
        datetime,
        isfinite,
        normalize_valuation_events,
        replace,
    )

sys.modules[__name__] = import_module("quant_platform._portfolio.valuation_events")
