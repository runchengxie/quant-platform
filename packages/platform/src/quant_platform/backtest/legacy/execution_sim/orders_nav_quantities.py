"""Module alias preserving implementation identity during compatibility migration."""

import sys
from importlib import import_module
from typing import TYPE_CHECKING

__all__ = ["ExecutionSimConfig", "_quantize_nav_sell_quantity"]

if TYPE_CHECKING:
    from quant_platform._portfolio.execution_sim.orders_nav_quantities import (
        ExecutionSimConfig,
        _quantize_nav_sell_quantity,
    )

sys.modules[__name__] = import_module(
    "quant_platform._portfolio.execution_sim.orders_nav_quantities"
)
