"""Lazy exports; deterministic imports never load model training."""

from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from quant_backtest_core.microstructure.impact import ExecutionSchedule as ExecutionSchedule
    from quant_backtest_core.microstructure.impact import ImpactEstimator as ImpactEstimator
    from quant_backtest_core.microstructure.impact import ImpactResult as ImpactResult

    from ticknet.dataset import NUM_CLASSES as NUM_CLASSES
    from ticknet.dataset import NUM_FEATURES as NUM_FEATURES
    from ticknet.dataset import WINDOW_SIZE as WINDOW_SIZE
    from ticknet.dataset import get_dummy_batch as get_dummy_batch
    from ticknet.model import DeepLOB as DeepLOB
    from ticknet.model import build_model as build_model

_EXPORTS = {
    "NUM_CLASSES": ("ticknet.dataset", "NUM_CLASSES"),
    "NUM_FEATURES": ("ticknet.dataset", "NUM_FEATURES"),
    "WINDOW_SIZE": ("ticknet.dataset", "WINDOW_SIZE"),
    "get_dummy_batch": ("ticknet.dataset", "get_dummy_batch"),
    "DeepLOB": ("ticknet.model", "DeepLOB"),
    "build_model": ("ticknet.model", "build_model"),
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
