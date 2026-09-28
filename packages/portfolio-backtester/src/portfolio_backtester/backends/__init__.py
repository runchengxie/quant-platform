"""Framework-neutral backtest backend boundary."""

from .base import (
    CANONICAL_BACKTEST_RESULT_SCHEMA,
    BackendCapabilities,
    BackendRegistry,
    BacktestBackend,
    CanonicalBacktestResult,
    to_json_compatible,
)
from .bundle import write_execution_aware_result_bundle
from .native import (
    IntradayExecutionAssumption,
    NativePositionReplayBackend,
    NativePositionReplayRequest,
)
from .sequenced import SequencedExecutionBackend, SequencedExecutionRequest

__all__ = [
    "CANONICAL_BACKTEST_RESULT_SCHEMA",
    "BackendCapabilities",
    "BackendRegistry",
    "BacktestBackend",
    "CanonicalBacktestResult",
    "IntradayExecutionAssumption",
    "NativePositionReplayBackend",
    "NativePositionReplayRequest",
    "SequencedExecutionBackend",
    "SequencedExecutionRequest",
    "to_json_compatible",
    "write_execution_aware_result_bundle",
]
