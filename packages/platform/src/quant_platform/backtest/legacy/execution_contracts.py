"""Module alias preserving implementation identity during compatibility migration."""

import sys
from importlib import import_module
from typing import TYPE_CHECKING

__all__ = [
    "TERMINAL_ORDER_STATUSES",
    "_ALLOWED_ORDER_TRANSITIONS",
    "Any",
    "Fill",
    "Instrument",
    "Iterable",
    "LedgerSnapshot",
    "Literal",
    "Mapping",
    "OrderEvent",
    "OrderIntent",
    "OrderState",
    "OrderStatus",
    "OrderType",
    "StrEnum",
    "Target",
    "TimeInForce",
    "_assert_timezone_aware",
    "annotations",
    "asdict",
    "assert_order_transition",
    "dataclass",
    "datetime",
    "field",
    "isfinite",
    "reduce_order_events",
]

if TYPE_CHECKING:
    from quant_platform._portfolio.execution_contracts import (
        _ALLOWED_ORDER_TRANSITIONS,
        TERMINAL_ORDER_STATUSES,
        Any,
        Fill,
        Instrument,
        Iterable,
        LedgerSnapshot,
        Literal,
        Mapping,
        OrderEvent,
        OrderIntent,
        OrderState,
        OrderStatus,
        OrderType,
        StrEnum,
        Target,
        TimeInForce,
        _assert_timezone_aware,
        annotations,
        asdict,
        assert_order_transition,
        dataclass,
        datetime,
        field,
        isfinite,
        reduce_order_events,
    )

sys.modules[__name__] = import_module("quant_platform._portfolio.execution_contracts")
