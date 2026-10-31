"""Module alias preserving implementation identity during compatibility migration."""

import sys
from importlib import import_module
from typing import TYPE_CHECKING

__all__ = [
    "BackendCapabilities",
    "CanonicalBacktestResult",
    "ClassVar",
    "ExecutionSimConfig",
    "IntradayExecutionAssumption",
    "Literal",
    "NativePositionReplayBackend",
    "NativePositionReplayRequest",
    "PositionBacktestConfig",
    "PositionBacktestResult",
    "SlippageModel",
    "_aligned_performance_frame",
    "_attach_fill_ids",
    "_attach_order_ids",
    "_optional_rule_col",
    "_validate_request",
    "annotations",
    "dataclass",
    "replace",
    "run_position_backtest",
    "simulate_execution_adjusted_nav",
    "to_json_compatible",
]

if TYPE_CHECKING:
    from quant_platform._portfolio.backends.native import (
        BackendCapabilities,
        CanonicalBacktestResult,
        ClassVar,
        ExecutionSimConfig,
        IntradayExecutionAssumption,
        Literal,
        NativePositionReplayBackend,
        NativePositionReplayRequest,
        PositionBacktestConfig,
        PositionBacktestResult,
        SlippageModel,
        _aligned_performance_frame,
        _attach_fill_ids,
        _attach_order_ids,
        _optional_rule_col,
        _validate_request,
        annotations,
        dataclass,
        replace,
        run_position_backtest,
        simulate_execution_adjusted_nav,
        to_json_compatible,
    )

sys.modules[__name__] = import_module("quant_platform._portfolio.backends.native")
