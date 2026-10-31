"""Module alias preserving implementation identity during compatibility migration."""

import sys
from importlib import import_module
from typing import TYPE_CHECKING

__all__ = [
    "annotations",
    "apply_position_postprocess",
    "positions_postprocess_enabled",
    "rebuild_backtest_from_positions",
]

if TYPE_CHECKING:
    from quant_platform._portfolio.position_postprocess import (
        annotations,
        apply_position_postprocess,
        positions_postprocess_enabled,
        rebuild_backtest_from_positions,
    )

sys.modules[__name__] = import_module("quant_platform._portfolio.position_postprocess")
