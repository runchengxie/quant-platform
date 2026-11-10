"""Engine alias: quant_backtest_core.daily.execution_sim.results."""

from __future__ import annotations

import sys
from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from quant_backtest_core.daily.execution_sim.results import (
        _COST_FIELD_BY_COL as _COST_FIELD_BY_COL,
    )
    from quant_backtest_core.daily.execution_sim.results import _COST_SUB_COLS as _COST_SUB_COLS
    from quant_backtest_core.daily.execution_sim.results import Any as Any
    from quant_backtest_core.daily.execution_sim.results import CostEvidence as CostEvidence
    from quant_backtest_core.daily.execution_sim.results import (
        ExecutionAdjustedNavResult as ExecutionAdjustedNavResult,
    )
    from quant_backtest_core.daily.execution_sim.results import (
        ExecutionSimResult as ExecutionSimResult,
    )
    from quant_backtest_core.daily.execution_sim.results import Mapping as Mapping
    from quant_backtest_core.daily.execution_sim.results import UnifiedLedger as UnifiedLedger
    from quant_backtest_core.daily.execution_sim.results import (
        _add_derived_cost_columns as _add_derived_cost_columns,
    )
    from quant_backtest_core.daily.execution_sim.results import (
        _add_total_cost_row as _add_total_cost_row,
    )
    from quant_backtest_core.daily.execution_sim.results import (
        _aggregate_cost_columns as _aggregate_cost_columns,
    )
    from quant_backtest_core.daily.execution_sim.results import _as_frame as _as_frame
    from quant_backtest_core.daily.execution_sim.results import (
        _build_cost_breakdown as _build_cost_breakdown,
    )
    from quant_backtest_core.daily.execution_sim.results import (
        _build_daily_series as _build_daily_series,
    )
    from quant_backtest_core.daily.execution_sim.results import _build_targets as _build_targets
    from quant_backtest_core.daily.execution_sim.results import (
        _build_turnover_breakdown as _build_turnover_breakdown,
    )
    from quant_backtest_core.daily.execution_sim.results import (
        _cost_breakdown_columns as _cost_breakdown_columns,
    )
    from quant_backtest_core.daily.execution_sim.results import (
        _cost_breakdown_source as _cost_breakdown_source,
    )
    from quant_backtest_core.daily.execution_sim.results import _cost_row as _cost_row
    from quant_backtest_core.daily.execution_sim.results import (
        _resolve_portfolio_value as _resolve_portfolio_value,
    )
    from quant_backtest_core.daily.execution_sim.results import cast as cast
    from quant_backtest_core.daily.execution_sim.results import dataclass as dataclass
    from quant_backtest_core.daily.execution_sim.results import pd as pd
    from quant_backtest_core.daily.execution_sim.results import (
        to_unified_ledger as to_unified_ledger,
    )

sys.modules[__name__] = import_module("quant_backtest_core.daily.execution_sim.results")
