"""Compare two real backends on an explicitly matched synthetic cash ledger.

This experiment normalizes evidence only. The Python backend constructs target
orders; the independent engine executes explicit quantities through its SDK.
"""

from __future__ import annotations

import argparse
import json
from decimal import Decimal
from pathlib import Path
from typing import Any

import pandas as pd

from quant_platform.backtest.legacy.execution import DetailedTradeFeeModel
from quant_platform.backtest.legacy.execution_sim import (
    ExecutionSimConfig,
    simulate_execution_adjusted_nav,
)

TOLERANCE = Decimal("0.00000001")
DATES = ("2025-01-02", "2025-01-03")
PRICES = dict(zip(DATES, (Decimal("10"), Decimal("12")), strict=True))


def session_request(*, first_mark: str = "10") -> dict[str, Any]:
    """Build declared synthetic zero-spread quotes, never convert observed bars."""
    sessions = []
    for index, day in enumerate(DATES):
        opening = pd.Timestamp(f"{day} 09:30:00", tz="Asia/Shanghai").value
        valuation = opening + 1_000_000_000
        quotes = []
        for timestamp, price in (
            (opening, str(PRICES[day])),
            (valuation, first_mark if index == 0 else "12"),
        ):
            quotes.append(
                {
                    "symbol": "AAA",
                    "ts_ns": timestamp,
                    "bid": price,
                    "ask": price,
                    "bid_size": "1000000",
                    "ask_size": "1000000",
                    "tradable": True,
                    "limit_up": False,
                    "limit_down": False,
                }
            )
        sessions.append(
            {
                "session_date": day,
                "open_ts_ns": opening,
                "valuation_ts_ns": valuation,
                "quotes": quotes,
                "orders": [
                    {
                        "id": "buy" if index == 0 else "sell",
                        "symbol": "AAA",
                        "information_ts_ns": opening - 1,
                        "side": "buy" if index == 0 else "sell",
                        "quantity": "100",
                    }
                ],
            }
        )
    return {
        "schema_version": "engine_request.v2",
        "currency": "CNY",
        "price_basis": "raw",
        "initial_cash": "10000",
        "fee_bps": "10",
        "enforce_t1": True,
        "instruments": [{"symbol": "AAA", "price_precision": 2, "buy_lot": 100}],
        "required_capabilities": ["session_ledger"],
        "sessions": sessions,
    }


def python_ledger() -> Any:
    """Run the maintained Python simulator with matching declared assumptions."""
    positions = pd.DataFrame(
        {
            "rebalance_date": ["20250101", "20250102"],
            "entry_date": ["20250102", "20250103"],
            "symbol": ["AAA", "AAA"],
            "weight": [0.1, 0.0],
            "side": ["long", "long"],
        }
    )
    pricing = pd.DataFrame(
        {
            "trade_date": pd.to_datetime(list(DATES)),
            "symbol": ["AAA", "AAA"],
            "price": [10.0, 12.0],
            "amount": [1_000_000.0, 1_000_000.0],
        }
    )
    config = ExecutionSimConfig(
        enabled=True,
        portfolio_value=10000,
        participation_rate=1,
        liquidity_cols=("amount",),
        buy_max_days=1,
        sell_max_days=1,
        round_lot=100,
        enforce_t1=True,
    )
    fees = DetailedTradeFeeModel(
        buy_commission_bps=10,
        sell_commission_bps=10,
        min_commission=0,
        sell_stamp_duty_bps=0,
        transfer_fee_bps=0,
        buy_slippage_bps=0,
        sell_slippage_bps=0,
        portfolio_value=10000,
    )
    return simulate_execution_adjusted_nav(
        positions,
        pricing,
        config,
        price_col="price",
        trade_fee_model=fees,
        price_basis="raw",
    )


def _day(value: str) -> str:
    return pd.Timestamp(value).strftime("%Y-%m-%d")


def normalize_python(result: Any) -> dict[str, Any]:
    fills = []
    quantities = dict.fromkeys(DATES, Decimal(0))
    for row in result.fills.to_dict("records"):
        day = _day(row["trade_date"])
        price = PRICES[day]
        quantity = Decimal(str(row["filled_notional"])) / price
        quantities[day] += quantity if row["side"] == "buy" else -quantity
        fills.append(
            {
                "date": day,
                "symbol": row["symbol"],
                "side": row["side"],
                "price": price,
                "quantity": quantity,
                "commission": Decimal(str(row["cost_commission"])),
            }
        )
    orders = [
        {
            "date": _day(row["entry_date"]),
            "symbol": row["symbol"],
            "side": row["side"],
            "status": row["status"].lower(),
            "filled_quantity": Decimal(str(row["filled_notional"]))
            / PRICES[_day(row["entry_date"])],
        }
        for row in result.orders.to_dict("records")
    ]
    daily = []
    quantity = Decimal(0)
    for row in result.daily.to_dict("records"):
        day = _day(row["trade_date"])
        quantity += quantities[day]
        daily.append(
            {
                "date": day,
                "cash": Decimal(str(row["cash"])),
                "quantity": quantity,
                "positions_value": Decimal(str(row["invested_value"])),
                "nav": Decimal(str(row["portfolio_value"])),
                "commission": Decimal(str(row["cost_commission"])),
            }
        )
    return {"orders": orders, "fills": fills, "daily": daily}


def normalize_engine(result: dict[str, Any], request: dict[str, Any]) -> dict[str, Any]:
    order_info = {
        row["id"]: (session["session_date"], row["side"])
        for session in request["sessions"]
        for row in session["orders"]
    }
    orders = [
        {
            "date": order_info[row["id"]][0],
            "symbol": row["symbol"],
            "side": order_info[row["id"]][1],
            "status": row["status"].lower(),
            "filled_quantity": Decimal(row["filled_quantity"]),
        }
        for row in result["orders"]
    ]
    fills = [
        {
            "date": order_info[row["order_id"]][0],
            "symbol": row["symbol"],
            "side": row["side"],
            **{key: Decimal(row[key]) for key in ("price", "quantity", "commission")},
        }
        for row in result["fills"]
    ]
    quantity = {row["session_date"]: Decimal(row["quantity"]) for row in result["daily_positions"]}
    daily = [
        {
            "date": row["session_date"],
            "quantity": quantity.get(row["session_date"], Decimal(0)),
            **{key: Decimal(row[key]) for key in ("cash", "positions_value", "nav", "commission")},
        }
        for row in result["daily_ledger"]
    ]
    return {"orders": orders, "fills": fills, "daily": daily}


def _flatten(value: Any, path: str = "") -> dict[str, Any]:
    if isinstance(value, dict):
        return {
            key: item
            for name, child in value.items()
            for key, item in _flatten(child, f"{path}.{name}").items()
        }
    if isinstance(value, list):
        rows = {f"{path}.length": len(value)}
        for index, child in enumerate(value):
            rows.update(_flatten(child, f"{path}[{index}]"))
        return rows
    return {path: value}


def compare(left: dict[str, Any], right: dict[str, Any]) -> list[dict[str, Any]]:
    """Compare all normalized fields; use a fixed absolute float boundary tolerance."""
    a, b = _flatten(left), _flatten(right)
    mismatches = []
    for key in sorted(a.keys() | b.keys()):
        old, new = a.get(key), b.get(key)
        equal = (
            abs(old - new) <= TOLERANCE
            if isinstance(old, Decimal) and isinstance(new, Decimal)
            else old == new
        )
        if not equal:
            mismatches.append({"field": key, "python": old, "engine": new})
    return mismatches


def run_comparison(executable: Path, digest: str, *, source_revision: str | None = None) -> dict:
    from quant_backtest_engine import EngineClient

    request = session_request()
    legacy = python_ledger()
    client = EngineClient(executable, digest, source_revision=source_revision)
    wire = client.run_sessions(request)
    python = normalize_python(legacy)
    engine = normalize_engine(wire, request)
    mismatches = compare(python, engine)
    return {
        "schema_version": "synthetic_ledger_comparison.v1",
        "synthetic_only": True,
        "executable_sha256": digest,
        "engine_source_revision": source_revision,
        "absolute_tolerance": str(TOLERANCE),
        "matched": not mismatches,
        "mismatches": mismatches,
        "python_derived_fields": {
            "fills.price": "declared fixture price; no independent Python fill-price field",
            "fills.quantity": "filled_notional divided by declared fixture price",
            "orders.filled_quantity": "filled_notional divided by declared fixture price",
            "daily.quantity": "cumulative signed inferred fill quantities",
            "independent_share_ledger": False,
        },
        "python": python,
        "engine": engine,
        "engine_request": request,
        "engine_result": wire,
        "python_orders": legacy.orders.to_dict("records"),
        "python_fills": legacy.fills.to_dict("records"),
        "python_daily": legacy.daily.to_dict("records"),
        "excluded": [
            "intraday clock parity",
            "T+1 rejection",
            "partial fills",
            "corporate actions",
            "dated taxes",
            "real market data",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--engine-executable", type=Path, required=True)
    parser.add_argument("--engine-sha256", required=True)
    parser.add_argument("--engine-source-revision")
    args = parser.parse_args()
    report = run_comparison(
        args.engine_executable, args.engine_sha256, source_revision=args.engine_source_revision
    )
    print(json.dumps(report, default=str, indent=2, allow_nan=False))
    return 0 if report["matched"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
