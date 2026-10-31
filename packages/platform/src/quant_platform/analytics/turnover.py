"""Module alias preserving implementation identity during compatibility migration."""

import sys
from importlib import import_module
from typing import TYPE_CHECKING

__all__ = [
    "Iterable",
    "RebalanceTurnoverReport",
    "TurnoverBreakdown",
    "_aligned_weight_delta",
    "_normalized_name_set",
    "_target_name_changes",
    "annotations",
    "annualize_turnover",
    "build_rebalance_turnover_report",
    "dataclass",
    "name_turnover",
    "turnover_from_trade_weights",
]

if TYPE_CHECKING:
    from quant_platform._portfolio.turnover import (
        Iterable,
        RebalanceTurnoverReport,
        TurnoverBreakdown,
        _aligned_weight_delta,
        _normalized_name_set,
        _target_name_changes,
        annotations,
        annualize_turnover,
        build_rebalance_turnover_report,
        dataclass,
        name_turnover,
        turnover_from_trade_weights,
    )

sys.modules[__name__] = import_module("quant_platform._portfolio.turnover")
