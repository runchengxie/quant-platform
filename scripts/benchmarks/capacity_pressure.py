#!/usr/bin/env python3
"""Reproducible synthetic fixed-target capacity sensitivity; no live capacity claim."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import subprocess
from dataclasses import asdict, dataclass, replace
from pathlib import Path

import pandas as pd

from quant_platform.backtest.legacy.minute_execution import (
    MinuteExecutionConfig,
    simulate_minute_execution,
)


@dataclass(frozen=True)
class Scenario:
    capital: int = 1_000_000
    participation: float = 0.05
    latency: int = 1
    cost_bp: int = 0
    mode: str = "capital_normalized_target"


def digest(frame: pd.DataFrame) -> str:
    encoded = frame.to_json(orient="records", date_format="iso")
    assert isinstance(encoded, str)
    return hashlib.sha256(encoded.encode()).hexdigest()


def fixture(scenario: Scenario) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Five rotating allocation sessions and two explicit unwind sessions."""
    rows, targets = [], []
    weight = 0.5 if scenario.mode == "scaled_weight" else 50_000 / scenario.capital
    for day, date in enumerate(pd.bdate_range("2026-01-05", periods=7)):
        start = pd.Timestamp(date).tz_localize("Asia/Shanghai") + pd.Timedelta(hours=9, minutes=29)
        for symbol in range(20):
            name = f"SYNTH{symbol:02d}"
            allocation = (1.5 if (symbol + day) % 2 else 0.5) / 20
            targets.append(
                {
                    "decision_time": start,
                    "entry_time": start + pd.Timedelta(minutes=1),
                    "symbol": name,
                    "weight": weight * allocation if day < 5 else 0.0,
                }
            )
            for minute in range(33):
                price = 10 + symbol * 0.02 + day * 0.1 + minute * 0.001
                rows.append(
                    {
                        "time": start + pd.Timedelta(minutes=minute),
                        "symbol": name,
                        "open": price,
                        "high": price,
                        "low": price,
                        "close": price,
                        "volume": 10_000,
                        "amount": price * 10_000,
                        "up_limit": 20.0,
                        "down_limit": 1.0,
                        "tradable": True,
                    }
                )
    return pd.DataFrame(targets), pd.DataFrame(rows)


def experiment(scenario: Scenario) -> tuple[dict, dict[str, pd.DataFrame]]:
    targets, bars = fixture(scenario)
    result = simulate_minute_execution(
        targets,
        bars,
        MinuteExecutionConfig(
            initial_cash=scenario.capital,
            participation_rate=scenario.participation,
            buy_fee_bp=scenario.cost_bp,
            sell_fee_bp=scenario.cost_bp,
            latency_minutes=scenario.latency,
            execution_minutes=30,
        ),
    )
    frames = {
        "targets": targets,
        "bars": bars,
        "orders": result.orders,
        "fills": result.fills,
        "daily": result.daily,
        "holdings": result.holdings,
    }
    terminal = result.holdings[result.holdings.date == result.daily.iloc[-1].date]
    final = result.daily.iloc[-1]
    if not math.isclose(final.cash + final.positions_value, final.nav, abs_tol=1e-7):
        raise RuntimeError("terminal NAV does not reconcile")
    row = dict(
        **asdict(scenario),
        **{f"{k}_sha256": digest(v) for k, v in frames.items()},
        nav_valid=bool(pd.notna(result.daily.iloc[-1].nav)),
        terminal_cash_cny=float(final.cash),
        terminal_positions_value_cny=float(final.positions_value),
        fill_rate_denominator="generated_parent_quantity_not_released_slices",
        fees_cny=result.summary["transaction_cost"],
        terminal_inventory_shares=float(terminal.quantity.sum()),
        terminal_nav_cny=float(result.daily.iloc[-1].nav),
        net_pnl_cny=float(result.daily.iloc[-1].nav - scenario.capital),
        expired_orders=int((result.orders.status == "expired").sum()),
        cash_or_participation_blocked_orders=int(
            (result.orders.reason.isin(["cash_or_participation", "fee_cash"])).sum()
        ),
    )
    for side in ("buy", "sell"):
        orders = result.orders[result.orders.side == side]
        desired, filled = float(orders.quantity.sum()), float(orders.filled_quantity.sum())
        row.update(
            {
                f"{side}_desired_shares": desired,
                f"{side}_filled_shares": filled,
                f"{side}_fill_rate": filled / desired if desired else None,
                f"{side}_unfilled_reference_cny": float(
                    ((orders.quantity - orders.filled_quantity) * orders.reference_price).sum()
                ),
            }
        )
    return row, frames


def fixed_fill_cost_control(fills: pd.DataFrame, zero_fee_pnl: float) -> list[dict]:
    """Conditional accounting replay: frozen quantities/prices; no rematching or cash test."""
    return [
        {
            "cost_bp": bp,
            "fixed_fills_sha256": digest(fills),
            "fees_cny": float(fills.gross_amount.sum()) * bp / 10_000,
            "net_pnl_cny": zero_fee_pnl - float(fills.gross_amount.sum()) * bp / 10_000,
        }
        for bp in (0, 10, 30)
    ]


def scenarios() -> list[Scenario]:
    base = Scenario()
    grid = [
        base,
        replace(base, capital=100_000),
        replace(base, capital=10_000_000),
        replace(base, participation=0.01),
        replace(base, participation=0.10),
        replace(base, latency=0),
        replace(base, latency=3),
        replace(base, cost_bp=10),
        replace(base, cost_bp=30),
        replace(base, capital=10_000_000, participation=0.01, latency=3, cost_bp=30),
    ]
    return [
        replace(case, mode=mode)
        for mode in ("capital_normalized_target", "scaled_weight")
        for case in grid
    ]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    manifest = {
        "scenarios": [asdict(case) for case in scenarios()],
        "bars_sha256": digest(fixture(Scenario())[1]),
        "source_revision": subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
        "pandas": pd.__version__,
        "symbols": 20,
        "sessions": 7,
        "bars": 4620,
        "entry_sessions": 5,
        "unwind_sessions": 2,
        "deadline_minutes": 30,
    }
    (args.output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    rows = []
    for index, scenario in enumerate(scenarios()):
        row, frames = experiment(scenario)
        if row != experiment(scenario)[0]:
            raise RuntimeError("nondeterministic output")
        directory = args.output / f"case-{index:02d}"
        directory.mkdir()
        for name, frame in frames.items():
            frame.to_json(directory / f"{name}.json", orient="records", date_format="iso")
        rows.append(row)
    base, frames = experiment(Scenario())
    payload = {
        "source_revision": subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
        "synthetic_only": True,
        "rows": rows,
        "fixed_fill_cost_control": fixed_fill_cost_control(frames["fills"], base["net_pnl_cny"]),
    }
    (args.output / "results.json").write_text(json.dumps(payload, indent=2, allow_nan=False) + "\n")
    pd.DataFrame(rows).to_csv(args.output / "results.csv", index=False)


if __name__ == "__main__":
    main()
