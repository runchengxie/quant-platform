"""Explicit daily requests and retained Platform research statistics.

Engine owns every daily replay. These adapters select no targets, fetch no
calendar, and do not recalculate cash, fills, fees or financial returns.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import replace
from typing import Any, Literal

import pandas as pd
from quant_backtest_core.daily.contracts import (
    DailyDecisionTiming,
    DailyInputLayout,
    DailyReplayRequest,
    ExecutionCalendar,
)
from quant_backtest_core.daily.execution_sim import ExecutionSimConfig
from quant_backtest_core.daily.execution_sim.results import ExecutionAdjustedNavResult
from quant_backtest_core.daily.runner import run_daily as _run_daily
from research_contracts import ResearchClock, validate_research_clock

from .engine_clocks import research_clock_nanoseconds, to_execution_clocks


def restore_daily_research(result: ExecutionAdjustedNavResult, trading_days_per_year: int):
    """Restore the original research formula without changing owner result classes."""
    from quant_platform._portfolio.metrics import summarize_period_returns

    daily = result.daily
    returns = (
        pd.Series(dtype=float)
        if daily.empty
        else pd.Series(
            pd.to_numeric(daily["executed_return"], errors="coerce").to_numpy(dtype=float),
            index=pd.to_datetime(daily["trade_date"], errors="coerce"),
            name="executed_return",
        ).dropna()
    )
    stats = summarize_period_returns(
        returns,
        [{"entry_idx": i, "exit_idx": i + 1} for i in range(len(returns))],
        int(trading_days_per_year) if not daily.empty else 252,
    )
    return replace(result, summary={**result.summary, "stats": stats})


def restore_period_research(result, trading_days_per_year: int):
    from quant_platform._portfolio.metrics import summarize_period_returns

    periods = result.periods.copy()
    records = []
    for row in periods.to_dict("records"):
        record = dict(row)
        for column in ("entry_date", "planned_exit_date", "exit_date", "rebalance_date"):
            if column in record:
                record[column] = pd.to_datetime(record[column], errors="coerce")
        records.append(record)
    returns = pd.Series(
        result.net_returns["net_return"].to_numpy(dtype=float),
        index=pd.to_datetime(result.net_returns["period_end"]),
        name="net_return",
    )
    stats = summarize_period_returns(returns, records, int(trading_days_per_year))
    # The eight execution aggregates remain exactly as supplied by Engine.
    stats.update(result.summary["stats"])
    return replace(result, summary={**result.summary, "stats": stats})


def _date_column(values: pd.Series) -> pd.Series:
    text = values.astype(str)
    return pd.to_datetime(text, format="mixed").dt.strftime("%Y-%m-%d")


def build_daily_request(
    *,
    positions: pd.DataFrame,
    pricing: pd.DataFrame,
    calendar: ExecutionCalendar,
    decision_clocks: Mapping[str, ResearchClock | Mapping[str, Any]],
    config: ExecutionSimConfig,
    mode: Literal["ideal", "capacity", "adjusted", "sequenced"] = "adjusted",
    price_col: str = "close",
    tradable_col: str | None = None,
    buy_tradable_col: str | None = None,
    sell_tradable_col: str | None = None,
    limit_up_col: str | None = None,
    limit_down_col: str | None = None,
    listing_status_col: str | None = None,
    price_basis: Literal["raw", "adjusted"] = "raw",
    corporate_actions: Sequence[Any] = (),
    fee_model: object | None = None,
    currency: str = "CNY",
) -> DailyReplayRequest:
    """Translate already selected targets and an explicitly supplied calendar.

    Legacy simulator arguments remain on their original direct compatibility
    functions. This opt-in neutral profile uses Engine's stricter admission.
    """
    targets, prices = positions.copy(), pricing.copy()
    for column in ("rebalance_date", "entry_date"):
        targets[column] = _date_column(targets[column])
    prices["trade_date"] = _date_column(prices["trade_date"])
    clocks, timings = {}, {}
    for key, value in decision_clocks.items():
        clock = validate_research_clock(
            value.to_mapping() if isinstance(value, ResearchClock) else value,
            require_execution=True,
        )
        day = pd.Timestamp(key).date().isoformat()
        if day in clocks:
            raise ValueError("duplicate decision clock date")
        clocks[day] = to_execution_clocks(value)
        exact = research_clock_nanoseconds(value)
        timings[day] = DailyDecisionTiming(
            exact["signal_at"],
            exact["earliest_order_at"],
            exact["execution_window_start_at"],
            exact["execution_window_end_at"],
            clock.timing_policy_id,
            clock.trading_calendar_ref,
        )
    settings = replace(
        config,
        **{
            key: value
            for key, value in {
                "limit_up_col": limit_up_col,
                "limit_down_col": limit_down_col,
                "listing_status_col": listing_status_col,
            }.items()
            if value is not None
        },
    )
    unit = (
        currency
        if config.liquidity_notional_multiplier == 1
        else (f"{config.liquidity_notional_multiplier:g} {currency}")
    )
    layout = DailyInputLayout(
        price_col,
        price_col,
        tradable_col,
        buy_tradable_col,
        sell_tradable_col,
        currency,
        f"{price_basis}_share",
        f"{currency}/{price_basis}_share",
        dict.fromkeys(config.liquidity_cols, unit),
    )
    return DailyReplayRequest(
        targets,
        prices,
        calendar,
        clocks,
        settings,
        mode,
        price_basis,
        tuple(corporate_actions),
        fee_model,
        layout=layout,
        decision_timing=timings,
    )


def run_daily(request: DailyReplayRequest, *, trading_days_per_year: int = 252):
    result = _run_daily(request)
    if isinstance(result, ExecutionAdjustedNavResult):
        return restore_daily_research(result, trading_days_per_year)
    return result
