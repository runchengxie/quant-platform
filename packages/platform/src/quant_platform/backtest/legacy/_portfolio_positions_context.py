"""Module alias preserving implementation identity during compatibility migration."""

import sys
from importlib import import_module
from typing import TYPE_CHECKING

__all__ = [
    "POSITION_COLUMNS",
    "ExecutionModel",
    "PortfolioBuildContext",
    "PortfolioPositionSetup",
    "RebalanceSelection",
    "RebalanceState",
    "SelectionConstraints",
    "_apply_liquidity_floor_to_day",
    "_build_optional_tables",
    "_empty_positions",
    "_group_by_trade_date",
    "_merge_pricing_supplemental_columns",
    "_prepare_portfolio_context",
    "_prepare_position_setup",
    "_resolve_rebalance_selection",
    "annotations",
    "build_execution_date_map",
    "cast",
    "dataclass",
    "normalize_weighting_mode",
    "resolve_pricing_source",
]

if TYPE_CHECKING:
    from quant_platform._portfolio._portfolio_positions_context import (
        POSITION_COLUMNS,
        ExecutionModel,
        PortfolioBuildContext,
        PortfolioPositionSetup,
        RebalanceSelection,
        RebalanceState,
        SelectionConstraints,
        _apply_liquidity_floor_to_day,
        _build_optional_tables,
        _empty_positions,
        _group_by_trade_date,
        _merge_pricing_supplemental_columns,
        _prepare_portfolio_context,
        _prepare_position_setup,
        _resolve_rebalance_selection,
        annotations,
        build_execution_date_map,
        cast,
        dataclass,
        normalize_weighting_mode,
        resolve_pricing_source,
    )

sys.modules[__name__] = import_module("quant_platform._portfolio._portfolio_positions_context")
