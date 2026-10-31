"""Module alias preserving implementation identity during compatibility migration."""

import sys
from importlib import import_module
from typing import TYPE_CHECKING

__all__ = [
    "Any",
    "BackendCapabilities",
    "CanonicalBacktestResult",
    "ClassVar",
    "CorporateAction",
    "ExecutionSimConfig",
    "Iterable",
    "Mapping",
    "ResearchClock",
    "SequencedExecutionBackend",
    "SequencedExecutionRequest",
    "ZoneInfo",
    "_attach_fill_ids",
    "_attach_order_ids",
    "_date",
    "_validate_market_rules",
    "_validate_targets",
    "_validated_clocks",
    "annotations",
    "cast",
    "dataclass",
    "date",
    "replace",
    "simulate_execution_adjusted_nav",
    "to_json_compatible",
    "validate_research_clock",
]

if TYPE_CHECKING:
    from quant_platform._portfolio.backends.sequenced import (
        Any,
        BackendCapabilities,
        CanonicalBacktestResult,
        ClassVar,
        CorporateAction,
        ExecutionSimConfig,
        Iterable,
        Mapping,
        ResearchClock,
        SequencedExecutionBackend,
        SequencedExecutionRequest,
        ZoneInfo,
        _attach_fill_ids,
        _attach_order_ids,
        _date,
        _validate_market_rules,
        _validate_targets,
        _validated_clocks,
        annotations,
        cast,
        dataclass,
        date,
        replace,
        simulate_execution_adjusted_nav,
        to_json_compatible,
        validate_research_clock,
    )

sys.modules[__name__] = import_module("quant_platform._portfolio.backends.sequenced")
