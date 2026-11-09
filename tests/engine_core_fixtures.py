"""Synthetic caller fixtures retained from Platform 7a618bd for integration tests."""

import pandas as pd

from quant_platform.backtest.quantity_locks import QuantityLock


def targets(times=("2026-01-05 09:30",), weights=(1.0,)):
    return pd.DataFrame(
        [
            {
                "decision_time": pd.Timestamp(t, tz="Asia/Shanghai") - pd.Timedelta(minutes=1),
                "entry_time": pd.Timestamp(t, tz="Asia/Shanghai"),
                "symbol": "A",
                "weight": w,
            }
            for t, w in zip(times, weights, strict=False)
        ]
    )


def bars(
    times=("2026-01-05 09:29", "2026-01-05 09:32", "2026-01-05 09:33"), price=10.0, volume=1000
):
    return pd.DataFrame(
        [
            {
                "time": pd.Timestamp(t, tz="Asia/Shanghai"),
                "interval_start": pd.Timestamp(t, tz="Asia/Shanghai") - pd.Timedelta(seconds=30),
                "symbol": "A",
                "open": price,
                "high": price,
                "low": price,
                "close": price,
                "volume": volume,
                "amount": price * volume,
                "up_limit": 11.0,
                "down_limit": 9.0,
                "tradable": True,
            }
            for t in times
        ]
    )


class Policy:
    def __init__(self):
        self.rows = []

    def __call__(self, state, proposed):
        self.rows.append(
            {
                "cash": state.cash,
                "holdings": dict(state.holdings),
                "pending": bool(state.pending_orders),
            }
        )
        return None if state.pending_orders else proposed

    def checkpoint(self):
        return self.rows.copy()


def at(value):
    return pd.Timestamp(value, tz="Asia/Shanghai")


def notice(start, end, symbols=("A",), available=None):
    return QuantityLock(
        available_ns=int(at(available or start).value),
        start_ns=int(at(start).value),
        end_ns=int(at(end).value),
        symbols=symbols,
        source_binding="synthetic-notice-v1",
    )


def parents(**changes):
    row = {
        "parent_id": "p",
        "side": "buy",
        "requested_shares": 100,
        "reference_price": 10,
        "reference_ns": 1,
        "reference_available_ns": 2,
        "decision_ns": 3,
        "arrival_price": 10.1,
        "arrival_ns": 4,
        "arrival_available_ns": 5,
        "completed_ns": 10,
        "available_ns": 20,
        "status": "completed",
        "source_binding": "synthetic-source-v1",
        "evidence_kind": "synthetic",
        "quantity_unit": "shares",
        "currency": "CNY",
        "price_convention": "includes_spread_and_impact",
        "brokerage_terms_version": "fixture-v1",
        "opportunity_price": 10.5,
        "opportunity_ns": 15,
        "opportunity_available_ns": 16,
        "opportunity_benchmark": "terminal_mid",
        "market_volume_shares": 1000,
        "market_amount_cny": 10000,
        "liquidity_start_ns": 4,
        "liquidity_end_ns": 10,
        "liquidity_available_ns": 12,
        "liquidity_quantity_unit": "shares",
        "liquidity_amount_unit": "CNY",
        "liquidity_bucket": "liquid",
        "execution_minutes": 30,
        "cluster_id": "2026-01-01",
    }
    row.update(changes)
    return pd.DataFrame([row])


def fills(**changes):
    row = {
        "fill_id": "f1",
        "parent_id": "p",
        "child_id": "c1",
        "price": 10.2,
        "shares": 40,
        "fill_ns": 6,
        "receipt_ns": 7,
        "source_binding": "synthetic-source-v1",
        "evidence_kind": "synthetic",
        "quantity_unit": "shares",
        "currency": "CNY",
    }
    row.update(changes)
    return pd.DataFrame([row])
