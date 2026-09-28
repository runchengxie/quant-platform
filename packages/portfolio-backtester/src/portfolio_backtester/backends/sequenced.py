"""Canonical daily execution of a schedule of independently timed decisions."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass, replace
from datetime import date
from typing import Any, ClassVar, cast
from zoneinfo import ZoneInfo

import pandas as pd
from research_contracts import ResearchClock, validate_research_clock

from ..corporate_actions import CorporateAction
from ..execution_sim import ExecutionSimConfig, simulate_execution_adjusted_nav
from .base import BackendCapabilities, CanonicalBacktestResult, to_json_compatible
from .native import _attach_fill_ids, _attach_order_ids


def _date(value: object, label: str) -> date:
    if value is None or pd.isna(value):
        raise ValueError(f"{label} has an unknown date")
    text = str(value).strip()
    try:
        parsed = pd.to_datetime(
            text, format="%Y%m%d" if len(text) == 8 and text.isdigit() else None
        )
    except (TypeError, ValueError) as error:
        raise ValueError(f"{label} has an invalid date: {text}") from error
    if pd.isna(parsed):
        raise ValueError(f"{label} has an invalid date: {text}")
    return cast(date, pd.Timestamp(parsed).date())


@dataclass(frozen=True)
class SequencedExecutionRequest:
    positions: pd.DataFrame
    pricing: pd.DataFrame
    decision_clocks: Mapping[str, ResearchClock | Mapping[str, Any]]
    config: ExecutionSimConfig
    price_col: str = "close"
    tradable_col: str | None = None
    buy_tradable_col: str | None = None
    sell_tradable_col: str | None = None
    limit_up_col: str | None = None
    limit_down_col: str | None = None
    listing_status_col: str | None = None
    transaction_cost_bps: float = 0.0
    corporate_actions: Iterable[CorporateAction] | None = None
    price_basis: str | None = None


class SequencedExecutionBackend:
    """Execute many target decisions through the common daily ledger engine.

    Clocks constrain target and execution dates. Callers must separately prove
    that every input used to generate each target was visible at its cutoff.
    """

    name: ClassVar[str] = "native.sequenced_execution"

    def run(self, request: SequencedExecutionRequest) -> CanonicalBacktestResult:
        clocks = self._validate(request)
        result = simulate_execution_adjusted_nav(
            request.positions,
            request.pricing,
            request.config,
            price_col=request.price_col,
            tradable_col=request.tradable_col,
            buy_tradable_col=request.buy_tradable_col,
            sell_tradable_col=request.sell_tradable_col,
            limit_up_col=request.limit_up_col,
            limit_down_col=request.limit_down_col,
            listing_status_col=request.listing_status_col,
            transaction_cost_bps=request.transaction_cost_bps,
            corporate_actions=request.corporate_actions,
            price_basis=request.price_basis,
        )
        if result.summary.get("status") != "ok" or result.daily.empty:
            raise ValueError(f"sequenced execution failed: {result.summary.get('status')}")
        ledger = result.to_unified_ledger(portfolio_value=request.config.portfolio_value)
        orders = _attach_order_ids(ledger.orders)
        fills = _attach_fill_ids(ledger.fills, orders)
        ledger = replace(ledger, orders=orders, fills=fills)
        daily_ledger = pd.DataFrame(
            {
                "trade_date": ledger.daily_cash["trade_date"].to_numpy(),
                "cash": ledger.daily_cash["cash"].to_numpy(),
                "positions_value": ledger.daily_positions["positions_value"].to_numpy(),
                "nav": ledger.daily_nav["nav"].to_numpy(),
            }
        )
        canonical = CanonicalBacktestResult(
            backend_name=self.name,
            capabilities=BackendCapabilities(
                order_lifecycle=True,
                partial_fills=True,
                daily_ledger=True,
                market_rules=tuple(
                    rule
                    for enabled, rule in (
                        (request.tradable_col is not None, "tradability"),
                        (request.config.enforce_price_limits, "price_limits"),
                        (request.config.enforce_listing_status, "listing_status"),
                    )
                    if enabled
                ),
            ),
            performance=result.daily.rename(
                columns={"trade_date": "period_end", "executed_return": "net_return"}
            ),
            positions=request.positions.copy(),
            orders=orders,
            fills=fills,
            daily_ledger=daily_ledger,
            unified_ledger=ledger,
            summary=to_json_compatible(result.summary),
            metadata={
                "decision_count": len(clocks),
                "clock_schema": "research.clock.v1",
                "input_visibility": "caller_must_prove",
                "price_basis": request.price_basis,
            },
        )
        canonical.validate()
        return canonical

    def _validate(self, request: SequencedExecutionRequest) -> dict[date, ResearchClock]:
        if not request.config.enabled:
            raise ValueError("sequenced execution requires an enabled simulator")
        required = {"rebalance_date", "entry_date", "symbol", "weight"}
        if missing := required - set(request.positions.columns):
            raise ValueError(f"positions are missing {sorted(missing)}")
        if request.positions.empty or request.pricing.empty:
            raise ValueError("positions and pricing must be nonempty")
        clocks = _validated_clocks(request.decision_clocks)
        _validate_targets(request.positions, clocks)
        if "trade_date" not in request.pricing:
            raise ValueError("pricing is missing trade_date")
        _validate_market_rules(request)
        last_valuation = max(clock.valuation_at.date() for clock in clocks.values())
        if any(
            _date(value, "pricing trade_date") > last_valuation
            for value in request.pricing["trade_date"]
        ):
            raise ValueError("pricing extends past the final decision valuation")
        return clocks


def _validated_clocks(
    values: Mapping[str, ResearchClock | Mapping[str, Any]],
) -> dict[date, ResearchClock]:
    clocks: dict[date, ResearchClock] = {}
    for key, raw in values.items():
        day = _date(key, "decision clock key")
        if day in clocks:
            raise ValueError(f"duplicate decision clock date: {day}")
        clock = validate_research_clock(
            raw.to_mapping() if isinstance(raw, ResearchClock) else raw,
            require_execution=True,
        )
        local_cutoff = clock.information_cutoff_at.astimezone(ZoneInfo(clock.timezone)).date()
        if local_cutoff != day:
            raise ValueError(f"decision clock cutoff date does not match {day}")
        clocks[day] = clock
    return clocks


def _validate_market_rules(request: SequencedExecutionRequest) -> None:
    for enabled, column in (
        (request.config.enforce_price_limits, request.limit_up_col),
        (request.config.enforce_price_limits, request.limit_down_col),
        (request.config.enforce_listing_status, request.listing_status_col),
    ):
        if enabled and (column is None or column not in request.pricing):
            raise ValueError("enabled market rule is missing its pricing column")
        if enabled and column is not None and request.pricing[column].isna().any():
            raise ValueError(f"enabled market rule {column} contains unknown values")
    if request.config.enforce_price_limits and (
        request.config.limit_up_col != request.limit_up_col
        or request.config.limit_down_col != request.limit_down_col
    ):
        raise ValueError("price-limit columns must agree with simulator config")
    if request.config.enforce_listing_status and (
        request.config.listing_status_col != request.listing_status_col
    ):
        raise ValueError("listing-status column must agree with simulator config")


def _validate_targets(positions: pd.DataFrame, clocks: Mapping[date, ResearchClock]) -> None:
    dates = positions["rebalance_date"].map(lambda x: _date(x, "rebalance_date"))
    entries = positions["entry_date"].map(lambda x: _date(x, "entry_date"))
    if set(dates) != set(clocks):
        raise ValueError("decision clocks must match every rebalance date exactly")
    weights = pd.to_numeric(positions["weight"], errors="coerce")
    if weights.isna().any() or (weights < 0).any():
        raise ValueError("target weights must be nonnegative finite numbers")
    if positions.assign(_day=dates).duplicated(["_day", "symbol"]).any():
        raise ValueError("duplicate symbols in a decision")
    if weights.groupby(dates).sum().gt(1.0 + 1e-9).any():
        raise ValueError("target weights exceed full investment")
    for day, entry in zip(dates, entries, strict=True):
        clock = clocks[day]
        earliest = clock.earliest_order_at
        window_end = clock.execution_window_end_at
        assert earliest is not None and window_end is not None
        if not earliest.date() <= entry <= window_end.date():
            raise ValueError(f"entry date for {day} falls outside its execution clock")


__all__ = ["SequencedExecutionBackend", "SequencedExecutionRequest"]
