"""Compatibility package; implementation and public owners are recorded in the module map."""

from importlib import import_module

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


def __getattr__(name):
    return getattr(import_module("quant_platform._portfolio.backends"), name)
