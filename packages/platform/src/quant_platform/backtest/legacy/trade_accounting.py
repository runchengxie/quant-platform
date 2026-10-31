"""Module alias preserving implementation identity during compatibility migration."""

import sys
from importlib import import_module
from typing import TYPE_CHECKING

__all__ = [
    "_compute_trade_summary",
    "_drift_previous_weights",
    "annotations",
    "cast",
    "compute_trade_summary",
    "drift_previous_weights",
    "normalize_position_weights",
]

if TYPE_CHECKING:
    from quant_platform._portfolio.trade_accounting import (
        _compute_trade_summary,
        _drift_previous_weights,
        annotations,
        cast,
        compute_trade_summary,
        drift_previous_weights,
        normalize_position_weights,
    )

sys.modules[__name__] = import_module("quant_platform._portfolio.trade_accounting")
