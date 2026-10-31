"""Platform result contracts; importing them does not load a simulator."""

from .contracts import (
    BackendCapabilities,
    BackendRegistry,
    BacktestBackend,
    CanonicalBacktestResult,
)
from .ledger import UnifiedLedger, reconcile_unified_ledger

__all__ = [
    "BackendCapabilities",
    "BackendRegistry",
    "BacktestBackend",
    "CanonicalBacktestResult",
    "UnifiedLedger",
    "reconcile_unified_ledger",
]
