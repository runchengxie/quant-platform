"""Reproducible synthetic replay benchmark; prints measurements as JSON.

Run after installing the optional Rust wheel into the project environment:
    .venv/bin/python scripts/benchmarks/microstructure_replay.py --events 100000
"""

from __future__ import annotations

import argparse
import json
import random
import statistics
import time

from ticknet.simulator.matching import MatchingEngine
from ticknet.simulator.replay import InterventionOrder, ReplaySession


def _events(count: int, seed: int) -> tuple[list[tuple], list[InterventionOrder]]:
    rng = random.Random(seed)
    background = [
        (i, rng.choice((-1, 1)), rng.randrange(97, 104), rng.randrange(1, 51), f"B{i}")
        for i in range(count)
    ]
    interventions = [InterventionOrder(i, 1, 103, 30, f"I{i}") for i in range(0, count, 100)]
    return background, interventions


def _run(backend: str, background: list[tuple], interventions: list[InterventionOrder]):
    engine = MatchingEngine(backend=backend)
    session = ReplaySession(engine, (99, 500), (101, 500))
    for row in background:
        session.add_background(*row)
    for order in interventions:
        session.add_intervention(order)
    start = time.perf_counter()
    ticks = session.run()
    duration = time.perf_counter() - start
    return duration, ticks, engine.lob.best_bid(), engine.lob.best_ask()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--events", type=int, default=100_000)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--repeats", type=int, default=5)
    args = parser.parse_args()
    if args.events <= 0 or args.repeats <= 0:
        parser.error("events and repeats must be positive")
    background, interventions = _events(args.events, args.seed)
    timings: dict[str, list[float]] = {"python": [], "rust": []}
    reference = None
    for _ in range(args.repeats):
        for backend in ("python", "rust"):
            seconds, ticks, bid, ask = _run(backend, background, interventions)
            result = (ticks, bid, ask)
            if reference is None:
                reference = result
            elif result != reference:
                raise RuntimeError(f"{backend} replay differs from Python reference")
            timings[backend].append(seconds)
    python_median = statistics.median(timings["python"])
    rust_median = statistics.median(timings["rust"])
    print(
        json.dumps(
            {
                "events": args.events,
                "interventions": len(interventions),
                "seed": args.seed,
                "repeats": args.repeats,
                "python_median_seconds": python_median,
                "rust_median_seconds": rust_median,
                "speedup": python_median / rust_median,
                "results_equal": True,
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
