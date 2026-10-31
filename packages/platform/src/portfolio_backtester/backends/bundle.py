"""Module alias preserving implementation identity during compatibility migration."""

import sys
from importlib import import_module
from typing import TYPE_CHECKING

__all__ = [
    "Any",
    "BacktestBundleManifest",
    "BacktestEvidenceTier",
    "CanonicalBacktestResult",
    "Mapping",
    "Path",
    "Sequence",
    "annotations",
    "calibrate_cost_model",
    "write_backtest_bundle",
    "write_execution_aware_result_bundle",
]

if TYPE_CHECKING:
    from quant_platform._portfolio.backends.bundle import (
        Any,
        BacktestBundleManifest,
        BacktestEvidenceTier,
        CanonicalBacktestResult,
        Mapping,
        Path,
        Sequence,
        annotations,
        calibrate_cost_model,
        write_backtest_bundle,
        write_execution_aware_result_bundle,
    )

sys.modules[__name__] = import_module("quant_platform._portfolio.backends.bundle")
