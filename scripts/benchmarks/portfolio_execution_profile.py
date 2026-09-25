#!/usr/bin/env python3
"""Profile deterministic synthetic portfolio execution workloads."""

from __future__ import annotations

import argparse
import cProfile
import hashlib
import json
import math
import os
import platform
import pstats
import resource
import statistics
import time
from collections.abc import Callable
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from portfolio_backtester.execution_sim import (
    ExecutionSimConfig,
    simulate_capacity_execution,
    simulate_execution_adjusted_nav,
)

SESSION_COUNT = 120
SYMBOL_COUNT = 120
TARGET_COUNT = 80
REBALANCE_INDICES = (0, 30, 60, 90)
REPETITIONS = 5


def _fixture() -> tuple[pd.DataFrame, pd.DataFrame]:
    dates = pd.bdate_range("2024-01-02", periods=SESSION_COUNT)
    symbols = np.array([f"S{index:04d}" for index in range(SYMBOL_COUNT)])
    date_index = np.repeat(np.arange(SESSION_COUNT), SYMBOL_COUNT)
    symbol_index = np.tile(np.arange(SYMBOL_COUNT), SESSION_COUNT)
    prices = pd.DataFrame(
        {
            "trade_date": dates.to_numpy()[date_index],
            "symbol": symbols[symbol_index],
            "open": 8.0 + symbol_index * 0.01 + date_index * 0.0005,
            "amount": 200_000.0 + (symbol_index % 13) * 175.0,
            "medadv20_amount": 400_000.0 + (symbol_index % 13) * 350.0,
            "is_tradable": (date_index + symbol_index) % 127 != 0,
            "is_buy_tradable": (date_index + 3 * symbol_index) % 139 != 0,
            "is_sell_tradable": (date_index + 5 * symbol_index) % 149 != 0,
            "limit_up": (date_index + 7 * symbol_index) % 251 == 0,
            "limit_down": (date_index + 11 * symbol_index) % 257 == 0,
            "listing_status": "listed",
        }
    )

    rows: list[dict[str, Any]] = []
    for rebalance_index in REBALANCE_INDICES:
        rebalance_date = dates[rebalance_index]
        entry_date = dates[rebalance_index + 1]
        start_symbol = (rebalance_index // 30) * 10
        for symbol in symbols[start_symbol : start_symbol + TARGET_COUNT]:
            rows.append(
                {
                    "rebalance_date": rebalance_date.strftime("%Y%m%d"),
                    "entry_date": entry_date.strftime("%Y%m%d"),
                    "symbol": symbol,
                    "weight": 1.0 / TARGET_COUNT,
                    "side": "long",
                }
            )
    return pd.DataFrame(rows), prices


def _config(*, participation_rate: float = 0.025, buy_max_days: int = 5) -> ExecutionSimConfig:
    return ExecutionSimConfig(
        enabled=True,
        portfolio_value=10_000_000.0,
        participation_rate=participation_rate,
        liquidity_cols=("amount", "medadv20_amount"),
        buy_max_days=buy_max_days,
        sell_max_days=10,
        round_lot=100,
        enforce_t1=True,
        enforce_price_limits=True,
        enforce_listing_status=True,
        limit_up_col="limit_up",
        limit_down_col="limit_down",
        listing_status_col="listing_status",
    )


def _case(
    name: str,
    positions: pd.DataFrame,
    pricing: pd.DataFrame,
) -> Callable[[], list[tuple[str, Any]]]:
    def daily_ledger() -> list[tuple[str, Any]]:
        result = simulate_execution_adjusted_nav(
            positions,
            pricing,
            _config(),
            price_col="open",
            tradable_col="is_tradable",
            buy_tradable_col="is_buy_tradable",
            sell_tradable_col="is_sell_tradable",
            limit_up_col="limit_up",
            limit_down_col="limit_down",
            listing_status_col="listing_status",
            transaction_cost_bps=8.0,
        )
        return _collect_result(name, result)

    def order_matching() -> list[tuple[str, Any]]:
        result = simulate_capacity_execution(
            positions,
            pricing,
            _config(),
            price_col="open",
            tradable_col="is_tradable",
            buy_tradable_col="is_buy_tradable",
            sell_tradable_col="is_sell_tradable",
            limit_up_col="limit_up",
            limit_down_col="limit_down",
            listing_status_col="listing_status",
        )
        return _collect_result(name, result)

    def scenario_sweep() -> list[tuple[str, Any]]:
        output: list[tuple[str, Any]] = []
        for participation_rate in (0.01, 0.025, 0.05, 0.10):
            for buy_max_days in (3, 5, 10):
                label = f"p{participation_rate:.3f}-days{buy_max_days}"
                result = simulate_capacity_execution(
                    positions,
                    pricing,
                    _config(
                        participation_rate=participation_rate,
                        buy_max_days=buy_max_days,
                    ),
                    price_col="open",
                    tradable_col="is_tradable",
                    buy_tradable_col="is_buy_tradable",
                    sell_tradable_col="is_sell_tradable",
                    limit_up_col="limit_up",
                    limit_down_col="limit_down",
                    listing_status_col="listing_status",
                )
                output.extend(_collect_result(label, result))
        return output

    return {
        "daily-ledger": daily_ledger,
        "order-matching": order_matching,
        "scenario-sweep": scenario_sweep,
    }[name]


def _collect_result(label: str, result: Any) -> list[tuple[str, Any]]:
    values: list[tuple[str, Any]] = [(f"{label}.summary", result.summary)]
    for frame_name in ("daily", "orders", "fills"):
        frame = getattr(result, frame_name, None)
        if isinstance(frame, pd.DataFrame):
            values.append((f"{label}.{frame_name}", frame))
    return values


def _normalized(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _normalized(item) for key, item in sorted(value.items())}
    if isinstance(value, (list, tuple)):
        return [_normalized(item) for item in value]
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating, float)):
        number = float(value)
        return number if math.isfinite(number) else None
    if isinstance(value, (np.bool_,)):
        return bool(value)
    if isinstance(value, (pd.Timestamp,)):
        return value.isoformat()
    return value


def _digest(values: list[tuple[str, Any]]) -> tuple[str, list[dict[str, Any]]]:
    digest = hashlib.sha256()
    inventory = []
    for name, value in values:
        digest.update(name.encode("utf-8"))
        digest.update(b"\0")
        if isinstance(value, pd.DataFrame):
            encoded = value.to_json(
                orient="records",
                date_format="iso",
                double_precision=15,
                force_ascii=False,
            ).encode("utf-8")
            inventory.append(
                {"name": name, "rows": int(value.shape[0]), "columns": list(value.columns)}
            )
        else:
            encoded = json.dumps(
                _normalized(value),
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
                allow_nan=False,
                default=str,
            ).encode("utf-8")
            inventory.append({"name": name, "type": "summary"})
        digest.update(encoded)
        digest.update(b"\n")
    return digest.hexdigest(), inventory


def _profile_summary(profiler: cProfile.Profile) -> list[dict[str, Any]]:
    functions = pstats.Stats(profiler).get_stats_profile().func_profiles
    rows = []
    for function, profile in sorted(
        functions.items(), key=lambda item: item[1].cumtime, reverse=True
    )[:20]:
        rows.append(
            {
                "function": f"{profile.file_name}:{profile.line_number}({function})",
                "calls": profile.ncalls,
                "total_seconds": round(profile.tottime, 6),
                "cumulative_seconds": round(profile.cumtime, 6),
            }
        )
    return rows


def _cpu_model() -> str:
    try:
        for line in Path("/proc/cpuinfo").read_text(encoding="utf-8").splitlines():
            if line.startswith("model name"):
                return line.split(":", maxsplit=1)[1].strip()
    except OSError:
        pass
    return platform.processor() or platform.machine()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--scenario",
        required=True,
        choices=("daily-ledger", "order-matching", "scenario-sweep"),
    )
    parser.add_argument("--repetitions", type=int, default=REPETITIONS)
    args = parser.parse_args()
    if args.repetitions < 3:
        parser.error("at least three repetitions are required")

    positions, pricing = _fixture()
    run_case = _case(args.scenario, positions, pricing)
    expected_digest, inventory = _digest(run_case())
    elapsed = []
    for _ in range(args.repetitions):
        started = time.perf_counter()
        current_digest, current_inventory = _digest(run_case())
        elapsed.append(time.perf_counter() - started)
        if current_digest != expected_digest or current_inventory != inventory:
            raise RuntimeError("synthetic execution output was not deterministic")

    profiler = cProfile.Profile()
    profiler.enable()
    current_digest, _ = _digest(run_case())
    profiler.disable()
    if current_digest != expected_digest:
        raise RuntimeError("profiled output digest changed")

    peak_rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    payload = {
        "scenario": args.scenario,
        "workload": {
            "sessions": SESSION_COUNT,
            "symbols": SYMBOL_COUNT,
            "pricing_rows": int(pricing.shape[0]),
            "position_rows": int(positions.shape[0]),
            "rebalances": len(REBALANCE_INDICES),
            "repetitions": args.repetitions,
        },
        "software": {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "pandas": pd.__version__,
            "platform": platform.platform(),
            "cpu_model": _cpu_model(),
            "logical_cpus": os.cpu_count(),
        },
        "median_wall_seconds": round(statistics.median(elapsed), 6),
        "repetition_wall_seconds": [round(value, 6) for value in elapsed],
        "peak_rss_kib": int(peak_rss),
        "output_sha256": expected_digest,
        "output_inventory": inventory,
        "profile_top_cumulative": _profile_summary(profiler),
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
