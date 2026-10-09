"""Signed execution, unfilled opportunity cost and fees on decision notional."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from math import fsum, isfinite
from typing import Literal

SHORTFALL_SCHEMA = "portfolio_backtester.order-shortfall.v1"


@dataclass(frozen=True)
class Fill:
    quantity: float
    price: float


@dataclass(frozen=True)
class OrderCost:
    order_id: str
    trade_date: str
    side: Literal["buy", "sell"]
    decision_price: float
    requested_quantity: float
    fills: tuple[Fill, ...]
    fees: float
    unfilled_price: float | None
    unfilled_at: str | None


def _number(value: float | None, label: str, *, positive: bool = False) -> float:
    if value is None or isinstance(value, (bool, str)):
        raise ValueError(f"{label} must be numeric")
    try:
        number = float(value)
    except (TypeError, ValueError) as error:
        raise ValueError(f"{label} must be finite and non-negative") from error
    if (
        isinstance(value, (bool, str))
        or not isfinite(number)
        or number < 0
        or (positive and number == 0)
    ):
        raise ValueError(f"{label} must be finite and {'positive' if positive else 'non-negative'}")
    return number


def order_shortfall(order: OrderCost) -> dict[str, object]:
    """Filled notional is valued at decision price, so coverage reflects quantity.

    Favorable execution/opportunity deviations are signed. They are not the
    non-negative fee/impact assumptions of the existing v1 calibration API.
    """
    if not isinstance(order.order_id, str) or not order.order_id.strip():
        raise ValueError("order_id required")
    if order.side not in {"buy", "sell"}:
        raise ValueError("side must be buy or sell")
    try:
        if date.fromisoformat(order.trade_date).isoformat() != order.trade_date:
            raise ValueError("non-canonical date")
    except (TypeError, ValueError) as error:
        raise ValueError("trade_date must be an ISO date") from error
    price = _number(order.decision_price, "decision_price", positive=True)
    requested = _number(order.requested_quantity, "requested_quantity", positive=True)
    fees = _number(order.fees, "fees")
    fills = [
        (_number(fill.quantity, "fill quantity"), _number(fill.price, "fill price", positive=True))
        for fill in order.fills
    ]
    filled = fsum(quantity for quantity, _ in fills)
    if filled > requested:
        raise ValueError("fill quantity exceeds requested quantity")
    remaining = requested - filled
    sign = 1.0 if order.side == "buy" else -1.0
    execution = sign * fsum(quantity * (fill_price - price) for quantity, fill_price in fills)
    opportunity = 0.0
    if remaining:
        benchmark = _number(order.unfilled_price, "unfilled_price", positive=True)
        try:
            benchmark_at = datetime.fromisoformat(order.unfilled_at or "")
            if benchmark_at.tzinfo is None or benchmark_at.utcoffset() is None:
                raise ValueError("naive benchmark timestamp")
        except (TypeError, ValueError) as error:
            raise ValueError("partial orders require timezone-aware unfilled_at") from error
        opportunity = sign * remaining * (benchmark - price)
    notional = requested * price
    components = {
        "execution": execution,
        "opportunity": opportunity,
        "fee": fees,
        "total": fsum([execution, opportunity, fees]),
    }
    if not isfinite(notional) or not all(isfinite(value) for value in components.values()):
        raise ValueError("shortfall arithmetic overflow")
    return {
        "schema_version": SHORTFALL_SCHEMA,
        "order_id": order.order_id,
        "trade_date": order.trade_date,
        "side": order.side,
        "requested_notional": notional,
        "filled_notional": filled * price,
        "coverage_ratio": filled / requested,
        "unfilled_at": order.unfilled_at,
        **{f"{key}_cash": value for key, value in components.items()},
        **{f"{key}_bps": value / notional * 10_000.0 for key, value in components.items()},
    }
