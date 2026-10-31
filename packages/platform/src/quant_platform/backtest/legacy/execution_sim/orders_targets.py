"""Module alias preserving implementation identity during compatibility migration."""

import sys
from importlib import import_module
from typing import TYPE_CHECKING

__all__ = [
    "Any",
    "DetailedTradeFeeModel",
    "Mapping",
    "TradeFeeModel",
    "_build_targets_by_rebalance",
    "_cash_weight_breakdown",
    "_cost_adjusted_target_notional",
    "_target_cash_notional",
    "annotations",
    "cast",
]

if TYPE_CHECKING:
    from quant_platform._portfolio.execution_sim.orders_targets import (
        Any,
        DetailedTradeFeeModel,
        Mapping,
        TradeFeeModel,
        _build_targets_by_rebalance,
        _cash_weight_breakdown,
        _cost_adjusted_target_notional,
        _target_cash_notional,
        annotations,
        cast,
    )

sys.modules[__name__] = import_module("quant_platform._portfolio.execution_sim.orders_targets")
