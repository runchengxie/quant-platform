"""Explicit minute execution API; importing this module loads the simulator."""

from quant_platform._portfolio.minute_execution import (
    MinuteDecisionState,
    MinuteExecutionConfig,
    MinuteExecutionResult,
    simulate_minute_execution,
)

__all__ = [
    "MinuteDecisionState",
    "MinuteExecutionConfig",
    "MinuteExecutionResult",
    "simulate_minute_execution",
]
