"""Exact research-clock translation; eligibility is not an observed fill time."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, cast

import pandas as pd
from quant_backtest_core.daily.contracts import utc_ns
from quant_backtest_engine.product.types import ClockSet
from research_contracts import ResearchClock, validate_research_clock


def research_clock_nanoseconds(value: ResearchClock | Mapping[str, Any]) -> dict[str, str | None]:
    raw = value.to_mapping() if isinstance(value, ResearchClock) else value
    validate_research_clock(raw, require_execution=True)
    # ResearchClock's datetime representation has microsecond resolution. Preserve
    # the original mapping strings when the source supplies finer observations.
    names = (
        "information_cutoff_at",
        "signal_at",
        "decision_at",
        "earliest_order_at",
        "execution_window_start_at",
        "execution_window_end_at",
        "valuation_at",
    )
    values = {
        name: utc_ns(cast(pd.Timestamp, pd.Timestamp(raw[name])))
        if raw.get(name) is not None
        else None
        for name in names
    }
    for left, right in (
        ("information_cutoff_at", "signal_at"),
        ("signal_at", "decision_at"),
        ("decision_at", "earliest_order_at"),
        ("decision_at", "execution_window_start_at"),
        ("earliest_order_at", "execution_window_end_at"),
        ("execution_window_start_at", "execution_window_end_at"),
        ("execution_window_end_at", "valuation_at"),
        ("earliest_order_at", "valuation_at"),
        ("decision_at", "valuation_at"),
    ):
        left_value, right_value = values[left], values[right]
        if (
            left_value is not None
            and right_value is not None
            and int(left_value) > int(right_value)
        ):
            raise ValueError(f"reversed exact clocks: {left}/{right}")
    return values


def to_execution_clocks(value: ResearchClock | Mapping[str, Any]) -> ClockSet:
    values = research_clock_nanoseconds(value)
    bounds = [
        bound
        for name in ("earliest_order_at", "execution_window_start_at")
        if (bound := values[name]) is not None
    ]
    return ClockSet(
        available_ns=None,
        information_ns=values["information_cutoff_at"],
        decision_ns=values["decision_at"],
        entry_ns=max(bounds, key=int) if bounds else None,
        effective_ns=None,
        report_ns=None,
        valuation_ns=values["valuation_at"],
    )
