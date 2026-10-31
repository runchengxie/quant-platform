"""Module alias preserving implementation identity during compatibility migration."""

import sys
from importlib import import_module
from typing import TYPE_CHECKING

__all__ = [
    "POSITION_COLUMNS",
    "PortfolioBuildContext",
    "PortfolioPositionSetup",
    "RebalanceSelection",
    "RebalanceState",
    "annotations",
    "apply_rank_offset",
    "apply_rebalance_buffer",
    "build_position_weights",
    "build_positions_by_rebalance",
    "limit_weight_turnover",
    "normalize_position_weights",
    "normalize_weighting_mode",
    "select_holdings",
]

if TYPE_CHECKING:
    from quant_platform._portfolio.portfolio import (
        POSITION_COLUMNS,
        PortfolioBuildContext,
        PortfolioPositionSetup,
        RebalanceSelection,
        RebalanceState,
        annotations,
        apply_rank_offset,
        apply_rebalance_buffer,
        build_position_weights,
        build_positions_by_rebalance,
        limit_weight_turnover,
        normalize_position_weights,
        normalize_weighting_mode,
        select_holdings,
    )

sys.modules[__name__] = import_module("quant_platform._portfolio.portfolio")
