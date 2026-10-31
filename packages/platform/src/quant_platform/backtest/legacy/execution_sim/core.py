"""Module alias preserving implementation identity during compatibility migration."""

import sys
from importlib import import_module
from typing import TYPE_CHECKING

__all__ = [
    "SupportedTradeFeeModel",
    "TradeFeeModel",
    "_build_execution_tables",
    "_build_tradable_table",
    "annotations",
    "prepare_execution_tables",
    "required_execution_sim_columns",
    "simulate_capacity_execution",
    "simulate_execution_adjusted_nav",
    "simulate_ideal_daily_nav",
]

if TYPE_CHECKING:
    from quant_platform._portfolio.execution_sim.core import (
        SupportedTradeFeeModel,
        TradeFeeModel,
        _build_execution_tables,
        _build_tradable_table,
        annotations,
        prepare_execution_tables,
        required_execution_sim_columns,
        simulate_capacity_execution,
        simulate_execution_adjusted_nav,
        simulate_ideal_daily_nav,
    )

sys.modules[__name__] = import_module("quant_platform._portfolio.execution_sim.core")
