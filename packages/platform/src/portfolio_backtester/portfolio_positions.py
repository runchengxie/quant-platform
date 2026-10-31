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
    "build_positions_by_rebalance",
]

if TYPE_CHECKING:
    from quant_platform._portfolio.portfolio_positions import (
        POSITION_COLUMNS,
        PortfolioBuildContext,
        PortfolioPositionSetup,
        RebalanceSelection,
        RebalanceState,
        annotations,
        build_positions_by_rebalance,
    )

sys.modules[__name__] = import_module("quant_platform._portfolio.portfolio_positions")
