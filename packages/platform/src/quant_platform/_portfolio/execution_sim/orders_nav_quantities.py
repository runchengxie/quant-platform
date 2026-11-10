"""Engine alias: quant_backtest_core.daily.execution_sim.orders_nav_quantities."""

import sys
from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from quant_backtest_core.daily.execution_sim.orders_nav_quantities import (
        ExecutionSimConfig as ExecutionSimConfig,
    )
    from quant_backtest_core.daily.execution_sim.orders_nav_quantities import (
        _quantize_nav_sell_quantity as _quantize_nav_sell_quantity,
    )

sys.modules[__name__] = import_module(
    "quant_backtest_core.daily.execution_sim.orders_nav_quantities"
)
