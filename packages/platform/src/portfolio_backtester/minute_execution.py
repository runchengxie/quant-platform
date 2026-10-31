"""Module alias preserving implementation identity during compatibility migration."""

import sys
from importlib import import_module
from typing import TYPE_CHECKING

__all__ = [
    "VALUATION_LEDGER_COLUMNS",
    "CorporateAction",
    "MinuteExecutionConfig",
    "MinuteExecutionResult",
    "ValuationEvent",
    "_MinuteSimulation",
    "_validate",
    "_validate_bar_numbers",
    "_validate_intervals",
    "_validate_target_weights",
    "annotations",
    "cast",
    "dataclass",
    "field",
    "normalize_corporate_actions",
    "normalize_valuation_events",
    "simulate_minute_execution",
]

if TYPE_CHECKING:
    from quant_platform._portfolio.minute_execution import (
        VALUATION_LEDGER_COLUMNS,
        CorporateAction,
        MinuteExecutionConfig,
        MinuteExecutionResult,
        ValuationEvent,
        _MinuteSimulation,
        _validate,
        _validate_bar_numbers,
        _validate_intervals,
        _validate_target_weights,
        annotations,
        cast,
        dataclass,
        field,
        normalize_corporate_actions,
        normalize_valuation_events,
        simulate_minute_execution,
    )

sys.modules[__name__] = import_module("quant_platform._portfolio.minute_execution")
