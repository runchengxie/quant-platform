"""Module alias preserving implementation identity during compatibility migration."""

import sys
from importlib import import_module
from typing import TYPE_CHECKING

__all__ = [
    "_build_active_exposure_summary_table",
    "annotations",
    "compute_backtest_exposure_analysis",
]

if TYPE_CHECKING:
    from quant_platform._portfolio.exposure import (
        _build_active_exposure_summary_table,
        annotations,
        compute_backtest_exposure_analysis,
    )

sys.modules[__name__] = import_module("quant_platform._portfolio.exposure")
