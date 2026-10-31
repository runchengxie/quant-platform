"""Module alias preserving implementation identity during compatibility migration."""

import sys
from importlib import import_module
from typing import TYPE_CHECKING

__all__ = [
    "CanonicalBacktestResult",
    "ExecutionSimConfig",
    "IntradayExecutionAssumption",
    "NativePositionReplayBackend",
    "NativePositionReplayRequest",
    "PositionBacktestConfig",
    "SlippageModel",
    "annotations",
    "build_position_replay_periods",
    "run_native_position_replay",
]

if TYPE_CHECKING:
    from quant_platform._portfolio.position_replay import (
        CanonicalBacktestResult,
        ExecutionSimConfig,
        IntradayExecutionAssumption,
        NativePositionReplayBackend,
        NativePositionReplayRequest,
        PositionBacktestConfig,
        SlippageModel,
        annotations,
        build_position_replay_periods,
        run_native_position_replay,
    )

sys.modules[__name__] = import_module("quant_platform._portfolio.position_replay")
