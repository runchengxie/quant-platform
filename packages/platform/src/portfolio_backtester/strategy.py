"""Module alias preserving implementation identity during compatibility migration."""

import sys
from importlib import import_module
from typing import TYPE_CHECKING

__all__ = [
    "Any",
    "ExecutionModel",
    "GroupCap",
    "StrategySpec",
    "_mapping",
    "annotations",
    "build_positions_by_rebalance",
    "construct_positions_from_strategy",
    "strategy_from_config",
    "strategy_lineage",
]

if TYPE_CHECKING:
    from quant_platform._portfolio.strategy import (
        Any,
        ExecutionModel,
        GroupCap,
        StrategySpec,
        _mapping,
        annotations,
        build_positions_by_rebalance,
        construct_positions_from_strategy,
        strategy_from_config,
        strategy_lineage,
    )

sys.modules[__name__] = import_module("quant_platform._portfolio.strategy")
