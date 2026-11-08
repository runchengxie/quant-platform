"""Synthetic real-backend prefix audit and single-account shared-capacity probe."""

from __future__ import annotations

import argparse
import hashlib
import inspect
import json
import subprocess
from decimal import Decimal
from pathlib import Path

import pandas as pd

from quant_platform.analytics.execution_integrity import compare_prefixes, fill_prefixes
from quant_platform.backtest.impact import LinearImpact
from quant_platform.backtest.minute import MinuteExecutionConfig
from quant_platform.backtest.minute_session import MinuteSession
from quant_platform.portfolio.sleeves import pool_sleeves
from scripts.benchmarks.compare_engine_ledgers import compare, normalize_engine


class ProposedPolicy:
    def __call__(self, _state, proposed):
        return proposed

    def checkpoint(self):
        return {"schema": "synthetic-proposed.v1"}


def _inputs(case):
    targets, bars, sessions = [], [], []
    partial = case == "ioc_continuation"
    for index, date in enumerate(("2025-01-02", "2025-01-03")):
        base = pd.Timestamp(date, tz="Asia/Shanghai")
        price = 10.0 if index == 0 else 12.0
        entry = base + pd.Timedelta(hours=9, minutes=30)
        targets.append(
            {
                "decision_time": entry - pd.Timedelta(minutes=1),
                "entry_time": entry,
                "symbol": "AAA",
                "weight": (0.3 if partial else 0.1) if not index else 0.0,
            }
        )
        quotes = []
        for minutes in (29, 32, 33, 35):
            time = base + pd.Timedelta(hours=9, minutes=minutes)
            bars.append(
                {
                    "time": time,
                    "interval_start": time - pd.Timedelta(seconds=30),
                    "symbol": "AAA",
                    "open": price,
                    "high": price,
                    "low": price,
                    "close": price,
                    "volume": 1000,
                    "amount": 1000 * price,
                    "tradable": True,
                    "up_limit": 100.0,
                    "down_limit": 1.0,
                }
            )
            quote_price = (
                11.0 if case == "valuation_difference" and not index and minutes == 35 else price
            )
            quotes.append(
                {
                    "symbol": "AAA",
                    "ts_ns": int(time.value),
                    "bid": str(quote_price),
                    "ask": str(quote_price),
                    "bid_size": "100" if partial else "1000000",
                    "ask_size": "100" if partial else "1000000",
                    "tradable": True,
                    "limit_up": False,
                    "limit_down": False,
                }
            )
        sessions.append(
            {
                "session_date": date,
                "open_ts_ns": quotes[0]["ts_ns"],
                "valuation_ts_ns": quotes[-1]["ts_ns"],
                "quotes": quotes,
                "orders": [
                    {
                        "id": "buy" if not index else "sell",
                        "symbol": "AAA",
                        "information_ts_ns": int((entry + pd.Timedelta(minutes=1)).value),
                        "side": "buy" if not index else "sell",
                        "quantity": "300" if partial and not index else "100",
                    }
                ],
            }
        )
    request = {
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
    return pd.DataFrame(targets), pd.DataFrame(bars), request


def _recorded_fills(rows, *, engine):
    return [
        {
            "fill_id": f"source-row-{index}",
            "ts_ns": int(row["ts_ns"]) if engine else int(row["time"].value),
            "symbol": row["symbol"],
            "side": row["side"],
            "quantity": str(row["quantity"]),
            "price": str(row["price"]),
            "fee": str(row["commission"] if engine else row["transaction_cost"]),
        }
        for index, row in enumerate(rows)
    ]


def _python_daily(result):
    rows = []
    for row in result.daily.itertuples():
        quantity = result.holdings.loc[result.holdings.date == row.date, "quantity"].sum()
        commission = result.fills.loc[
            result.fills.time.dt.date == row.date, "transaction_cost"
        ].sum()
        rows.append(
            {
                "date": str(row.date),
                "quantity": Decimal(str(quantity)),
                "cash": Decimal(str(row.cash)),
                "positions_value": Decimal(str(row.positions_value)),
                "nav": Decimal(str(row.nav)),
                "commission": Decimal(str(commission)),
            }
        )
    return rows


def _expected(case):
    times = [
        int(pd.Timestamp(f"{day} {clock}", tz="Asia/Shanghai").value)
        for day, clock in (
            ("2025-01-02", "09:32"),
            ("2025-01-02", "09:33"),
            ("2025-01-03", "09:32"),
            ("2025-01-03", "09:33"),
        )
    ]

    def rows(states):
        return [
            {"ts_ns": t, "cash": Decimal(c), "quantities": {"AAA": Decimal(q)} if q else {}}
            for t, c, q in states
        ]

    full = rows([(0, "10000", 0), (times[0], "8999", 100), (times[2], "10197.8", 0)])
    partial = rows(
        [
            (0, "10000", 0),
            (times[0], "8999", 100),
            (times[1], "7998", 200),
            (times[2], "9196.8", 100),
            (times[3], "10395.6", 0),
        ]
    )

    def daily(cash, quantity, value, nav, fees):
        return [
            {
                "date": day,
                **{
                    key: Decimal(str(values[i]))
                    for key, values in (
                        ("cash", cash),
                        ("quantity", quantity),
                        ("positions_value", value),
                        ("nav", nav),
                        ("commission", fees),
                    )
                },
            }
            for i, day in enumerate(("2025-01-02", "2025-01-03"))
        ]

    normal = daily(["8999", "10197.8"], [100, 0], [1000, 0], ["9999", "10197.8"], [1, "1.2"])
    marked = daily(["8999", "10197.8"], [100, 0], [1100, 0], ["10099", "10197.8"], [1, "1.2"])
    continued = daily(["7998", "10395.6"], [200, 0], [2000, 0], ["9998", "10395.6"], [2, "2.4"])
    left = partial if case == "ioc_continuation" else full
    differences = (
        compare(continued, normal)
        if case == "ioc_continuation"
        else compare(normal, marked)
        if case == "valuation_difference"
        else []
    )
    return left, full, differences


def run_prefix_comparison(binary, digest, case):
    from quant_backtest_engine import EngineClient

    if case not in {"roundtrip", "valuation_difference", "ioc_continuation"}:
        raise ValueError("declared synthetic comparison case required")
    targets, bars, request = _inputs(case)
    owner = MinuteSession(
        targets,
        bars,
        MinuteExecutionConfig(10000, 0.1, 10, 10, execution_minutes=4),
        policy=ProposedPolicy(),
    )
    result = owner.run()
    engine = EngineClient(binary, digest).run_sessions(request)
    left = fill_prefixes(_recorded_fills(result.fills.to_dict("records"), engine=False), "10000")
    right = fill_prefixes(_recorded_fills(engine["fills"], engine=True), "10000")
    prefixes = compare_prefixes(left, right)
    daily = compare(_python_daily(result), normalize_engine(engine, request)["daily"])
    expected_left, expected_right, expected_daily = _expected(case)
    expectation = not (
        compare(left, expected_left)
        or compare(right, expected_right)
        or compare(daily, expected_daily)
    )
    return {
        "case": case,
        "expectation_met": expectation,
        "prefix_differences": prefixes,
        "daily_differences": daily,
        "python_fill_prefixes": left,
        "engine_fill_prefixes": right,
        "python_daily": _python_daily(result),
        "engine_result": engine,
        "request": request,
        "engine_sha256": digest,
        "basis": "fill_prefix_audit_plus_daily_ledger_not_intraday_account_snapshots",
        "semantic_difference": "IOC cancels remainder; Python parent continues on later bars"
        if case == "ioc_continuation"
        else None,
    }


def pooled_capacity_probe():
    targets, bars, _ = _inputs("roundtrip")
    targets = targets.iloc[:1].copy().assign(weight=1.0)
    bars = bars.loc[(bars.time.dt.day == 2) & bars.time.dt.minute.isin([29, 32, 33])]
    pooled = pool_sleeves({"one": targets, "two": targets}, {"one": 0.5, "two": 0.5})
    impact = LinearImpact(permanent=0.001)
    joint = MinuteSession(
        pooled,
        bars,
        MinuteExecutionConfig(10000, 0.1, 0, 0),
        policy=ProposedPolicy(),
        impact=impact,
    ).run()
    isolated = [
        MinuteSession(
            targets,
            bars,
            MinuteExecutionConfig(5000, 0.1, 0, 0),
            policy=ProposedPolicy(),
            impact=LinearImpact(permanent=0.001),
        ).run()
        for _ in range(2)
    ]
    return {
        "pooled_filled_shares": int(joint.fills.quantity.sum()),
        "isolated_filled_shares_sum": int(sum(r.fills.quantity.sum() for r in isolated)),
        "same_total_initial_cash": True,
        "pooled_impact_permanent": impact.checkpoint()["states"]["AAA"]["permanent"],
        "basis": "single_shared_cash_account_not_independent_brokers_or_sleeve_PnL_attribution",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--binary", type=Path, required=True)
    parser.add_argument("--sha256", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.resolve().is_relative_to(Path(__file__).resolve().parents[2]):
        raise ValueError("benchmark output must be outside source")
    report = {
        "schema": "execution-integrity-benchmark.v1",
        "source_revision": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=Path(__file__).resolve().parents[2], text=True
        ).strip(),
        "source_hashes": {
            Path(inspect.getfile(obj)).name: hashlib.sha256(
                Path(inspect.getfile(obj)).read_bytes()
            ).hexdigest()
            for obj in (ProposedPolicy, fill_prefixes, pool_sleeves, MinuteSession, LinearImpact)
        },
        "comparisons": [
            run_prefix_comparison(args.binary, args.sha256, name)
            for name in ("roundtrip", "valuation_difference", "ioc_continuation")
        ],
        "pooled_capacity": pooled_capacity_probe(),
    }
    with args.output.open("x") as stream:
        json.dump(report, stream, indent=2, default=str, allow_nan=False)
    if not all(r["expectation_met"] for r in report["comparisons"]):
        raise ValueError("unexpected cross-engine difference retained in report")


if __name__ == "__main__":
    main()
