from __future__ import annotations

import importlib
import importlib.util

import pytest


def _order(**changes):
    assert importlib.util.find_spec("portfolio_backtester.shortfall"), "shortfall API missing"
    api = importlib.import_module("portfolio_backtester.shortfall")
    values = {
        "order_id": "A",
        "trade_date": "2024-01-02",
        "side": "buy",
        "decision_price": 10.0,
        "requested_quantity": 100.0,
        "fills": (api.Fill(60.0, 11.0),),
        "fees": 5.0,
        "unfilled_price": 12.0,
        "unfilled_at": "2024-01-02T15:00:00Z",
    }
    values.update(changes)
    return api, api.OrderCost(**values)


def test_signed_partial_shortfall_has_exact_components():
    api, order = _order()
    row = api.order_shortfall(order)
    assert row["execution_cash"] == 60.0
    assert row["opportunity_cash"] == 80.0
    assert row["fee_cash"] == 5.0
    assert row["total_cash"] == 145.0
    assert row["total_bps"] == 1450.0
    assert row["requested_notional"] == 1000.0
    assert row["filled_notional"] == 600.0
    assert row["coverage_ratio"] == 0.6
    assert row["unfilled_at"] == "2024-01-02T15:00:00Z"


def test_sell_sign_and_zero_fill_opportunity():
    api, order = _order(side="sell")
    assert api.order_shortfall(order)["total_cash"] == -135.0
    api, order = _order(fills=())
    assert api.order_shortfall(order)["total_cash"] == 205.0
    assert api.order_shortfall(order)["coverage_ratio"] == 0.0


def test_favorable_full_fill_needs_no_unfilled_benchmark():
    api, order = _order()
    order = api.OrderCost(
        "A", "2024-01-02", "buy", 10.0, 100.0, (api.Fill(100.0, 9.0),), 0.0, None, None
    )
    assert api.order_shortfall(order)["total_bps"] == -1000.0


@pytest.mark.parametrize(
    "change",
    [
        {"decision_price": 0.0},
        {"requested_quantity": -1.0},
        {"fees": -1.0},
        {"decision_price": float("nan")},
        {"unfilled_price": None},
        {"unfilled_at": None},
        {"unfilled_at": "2024-01-02"},
        {"side": "unknown"},
        {"order_id": ""},
        {"trade_date": "not-a-date"},
    ],
)
def test_invalid_order_rejected(change):
    api, order = _order(**change)
    with pytest.raises(ValueError):
        api.order_shortfall(order)


@pytest.mark.parametrize(
    "quantity,price", [(101.0, 10.0), (-1.0, 10.0), (1.0, 0.0), (1.0, float("inf"))]
)
def test_invalid_fills_rejected(quantity, price):
    api, order = _order()
    order = api.OrderCost(
        "A",
        "2024-01-02",
        "buy",
        10.0,
        100.0,
        (api.Fill(quantity, price),),
        0.0,
        12.0,
        "2024-01-02T15:00:00Z",
    )
    with pytest.raises(ValueError):
        api.order_shortfall(order)
