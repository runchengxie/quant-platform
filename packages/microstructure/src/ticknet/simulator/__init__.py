"""Lazy exports; deterministic imports never load model training."""

from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from quant_backtest_core.microstructure.impact import ExecutionSchedule as ExecutionSchedule
    from quant_backtest_core.microstructure.impact import ImpactEstimator as ImpactEstimator
    from quant_backtest_core.microstructure.impact import ImpactResult as ImpactResult

_EXPORTS = {
    "ExecutionSchedule": ("quant_backtest_core.microstructure.impact", "ExecutionSchedule"),
    "ImpactResult": ("quant_backtest_core.microstructure.impact", "ImpactResult"),
    "ImpactEstimator": ("quant_backtest_core.microstructure.impact", "ImpactEstimator"),
}
__all__ = list(_EXPORTS)


def __getattr__(name: str):
    if name not in _EXPORTS:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    module, symbol = _EXPORTS[name]
    value = getattr(import_module(module), symbol)
    globals()[name] = value
    return value
