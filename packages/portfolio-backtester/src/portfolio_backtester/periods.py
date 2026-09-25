from __future__ import annotations

from typing import Literal

import pandas as pd

from .execution_calendar import resolve_execution_date
from .types import BacktestPeriodPlan


def resolve_backtest_period_plan(
    *,
    rebalance_dates: list[pd.Timestamp],
    rebalance_index: int,
    rebalance_date: pd.Timestamp,
    exit_mode: Literal["rebalance", "label_horizon"],
    exit_horizon_days: int | None,
    shift_days: int,
    prev_exit_idx: int | None,
    trade_dates: list[pd.Timestamp],
    date_to_idx: dict[pd.Timestamp, int],
    execution_calendar: str,
    execution_open_dates: tuple,
    execution_closed_dates: tuple,
) -> BacktestPeriodPlan | None:
    if rebalance_date not in date_to_idx:
        return None

    entry_date = resolve_execution_date(
        rebalance_date,
        shift_days,
        trade_dates,
        calendar=execution_calendar,
        open_dates=execution_open_dates,
        closed_dates=execution_closed_dates,
    )
    if entry_date is None:
        return None
    entry_idx = date_to_idx.get(entry_date)
    if entry_idx is None:
        return None

    planned_exit_idx = _resolve_planned_exit_index(
        exit_mode=exit_mode,
        rebalance_dates=rebalance_dates,
        rebalance_index=rebalance_index,
        entry_idx=entry_idx,
        exit_horizon_days=exit_horizon_days,
        prev_exit_idx=prev_exit_idx,
        trade_dates=trade_dates,
        date_to_idx=date_to_idx,
        shift_days=shift_days,
        execution_calendar=execution_calendar,
        execution_open_dates=execution_open_dates,
        execution_closed_dates=execution_closed_dates,
    )
    if planned_exit_idx is None:
        return None

    if prev_exit_idx is not None and entry_idx < prev_exit_idx:
        return None
    if (
        entry_idx >= len(trade_dates)
        or planned_exit_idx >= len(trade_dates)
        or entry_idx >= planned_exit_idx
    ):
        return None

    return BacktestPeriodPlan(
        entry_idx=entry_idx,
        planned_exit_idx=planned_exit_idx,
        entry_date=trade_dates[entry_idx],
        planned_exit_date=trade_dates[planned_exit_idx],
    )


def _resolve_planned_exit_index(
    *,
    exit_mode: Literal["rebalance", "label_horizon"],
    rebalance_dates: list[pd.Timestamp],
    rebalance_index: int,
    entry_idx: int,
    exit_horizon_days: int | None,
    prev_exit_idx: int | None,
    trade_dates: list[pd.Timestamp],
    date_to_idx: dict[pd.Timestamp, int],
    shift_days: int,
    execution_calendar: str,
    execution_open_dates: tuple,
    execution_closed_dates: tuple,
) -> int | None:
    if exit_mode == "label_horizon":
        return _label_horizon_exit_index(
            entry_idx, exit_horizon_days=exit_horizon_days, prev_exit_idx=prev_exit_idx
        )
    if rebalance_index >= len(rebalance_dates) - 1:
        return None
    next_rebalance = rebalance_dates[rebalance_index + 1].normalize()
    if next_rebalance not in date_to_idx:
        return None
    planned_exit_date = resolve_execution_date(
        next_rebalance,
        shift_days,
        trade_dates,
        calendar=execution_calendar,
        open_dates=execution_open_dates,
        closed_dates=execution_closed_dates,
    )
    if planned_exit_date is None:
        return None
    return date_to_idx.get(planned_exit_date)


def _label_horizon_exit_index(
    entry_idx: int, *, exit_horizon_days: int | None, prev_exit_idx: int | None
) -> int:
    if exit_horizon_days is None:
        raise ValueError("exit_horizon_days is required for exit_mode='label_horizon'.")
    if prev_exit_idx is not None and entry_idx < prev_exit_idx:
        raise ValueError(
            "exit_mode='label_horizon' overlaps with rebalance_dates. "
            "Increase rebalance_frequency or use exit_mode='rebalance'."
        )
    return entry_idx + exit_horizon_days
