"""Module alias preserving implementation identity during compatibility migration."""

import sys
from importlib import import_module
from typing import TYPE_CHECKING

__all__ = [
    "CANONICAL_BACKTEST_RESULT_SCHEMA",
    "Any",
    "BackendCapabilities",
    "BackendRegistry",
    "BacktestBackend",
    "CanonicalBacktestResult",
    "Mapping",
    "Protocol",
    "RequestT",
    "Sequence",
    "TypeVar",
    "UnifiedLedger",
    "_assert_daily_ledger_balanced",
    "_assert_json_compatible",
    "_assert_unique",
    "_require_columns",
    "_validate_daily_ledger",
    "_validate_order_lifecycle",
    "_validate_performance_and_positions",
    "_validate_unified_ledger",
    "annotations",
    "dataclass",
    "date",
    "datetime",
    "field",
    "isfinite",
    "reconcile_unified_ledger",
    "runtime_checkable",
    "to_json_compatible",
]

if TYPE_CHECKING:
    from quant_platform.backtest.contracts import (
        CANONICAL_BACKTEST_RESULT_SCHEMA,
        Any,
        BackendCapabilities,
        BackendRegistry,
        BacktestBackend,
        CanonicalBacktestResult,
        Mapping,
        Protocol,
        RequestT,
        Sequence,
        TypeVar,
        UnifiedLedger,
        _assert_daily_ledger_balanced,
        _assert_json_compatible,
        _assert_unique,
        _require_columns,
        _validate_daily_ledger,
        _validate_order_lifecycle,
        _validate_performance_and_positions,
        _validate_unified_ledger,
        annotations,
        dataclass,
        date,
        datetime,
        field,
        isfinite,
        reconcile_unified_ledger,
        runtime_checkable,
        to_json_compatible,
    )

sys.modules[__name__] = import_module("quant_platform._portfolio.backends.base")
