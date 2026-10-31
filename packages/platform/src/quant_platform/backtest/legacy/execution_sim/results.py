"""Module alias preserving implementation identity during compatibility migration."""

import sys
from importlib import import_module
from typing import TYPE_CHECKING

__all__ = [
    "_COST_FIELD_BY_COL",
    "_COST_SUB_COLS",
    "Any",
    "ExecutionAdjustedNavResult",
    "ExecutionSimResult",
    "Mapping",
    "UnifiedLedger",
    "_add_derived_cost_columns",
    "_add_total_cost_row",
    "_aggregate_cost_columns",
    "_as_frame",
    "_build_cost_breakdown",
    "_build_daily_series",
    "_build_targets",
    "_build_turnover_breakdown",
    "_cost_breakdown_columns",
    "_cost_breakdown_source",
    "_cost_row",
    "_resolve_portfolio_value",
    "annotations",
    "cast",
    "dataclass",
    "to_unified_ledger",
]

if TYPE_CHECKING:
    from quant_platform._portfolio.execution_sim.results import (
        _COST_FIELD_BY_COL,
        _COST_SUB_COLS,
        Any,
        ExecutionAdjustedNavResult,
        ExecutionSimResult,
        Mapping,
        UnifiedLedger,
        _add_derived_cost_columns,
        _add_total_cost_row,
        _aggregate_cost_columns,
        _as_frame,
        _build_cost_breakdown,
        _build_daily_series,
        _build_targets,
        _build_turnover_breakdown,
        _cost_breakdown_columns,
        _cost_breakdown_source,
        _cost_row,
        _resolve_portfolio_value,
        annotations,
        cast,
        dataclass,
        to_unified_ledger,
    )

sys.modules[__name__] = import_module("quant_platform._portfolio.execution_sim.results")
