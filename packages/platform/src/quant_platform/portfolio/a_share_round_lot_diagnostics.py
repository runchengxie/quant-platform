"""Module alias preserving implementation identity during compatibility migration."""

import sys
from importlib import import_module
from typing import TYPE_CHECKING

__all__ = [
    "Any",
    "RoundLotSimulationCalendar",
    "RoundLotSimulationRows",
    "RoundLotSimulationState",
    "RoundLotVariant",
    "_append_daily_row",
    "_apply_rebalance",
    "_entry_dates_for_rebalances",
    "_holding_values",
    "_rebalance_diag_payload",
    "_run_variant_simulation",
    "_summary_from_outputs",
    "_trade_to_target",
    "allocate_round_lot",
    "annotations",
    "compute_round_lot_simulation_stats",
    "dataclass",
    "next_trade_date",
    "portfolio_value",
    "prepare_round_lot_simulation_calendar",
    "rebalance_dates",
    "select_round_lot_targets",
    "simulate_round_lot_variant",
    "trading_dates",
]

if TYPE_CHECKING:
    from quant_platform._portfolio.a_share_round_lot_diagnostics import (
        Any,
        RoundLotSimulationCalendar,
        RoundLotSimulationRows,
        RoundLotSimulationState,
        RoundLotVariant,
        _append_daily_row,
        _apply_rebalance,
        _entry_dates_for_rebalances,
        _holding_values,
        _rebalance_diag_payload,
        _run_variant_simulation,
        _summary_from_outputs,
        _trade_to_target,
        allocate_round_lot,
        annotations,
        compute_round_lot_simulation_stats,
        dataclass,
        next_trade_date,
        portfolio_value,
        prepare_round_lot_simulation_calendar,
        rebalance_dates,
        select_round_lot_targets,
        simulate_round_lot_variant,
        trading_dates,
    )

sys.modules[__name__] = import_module("quant_platform._portfolio.a_share_round_lot_diagnostics")
