# Rust microstructure kernel

Language: English · [简体中文](microstructure-rust.md)

`packages/microstructure/rust` is an optional PyO3 wheel for the public
`ticknet.simulator` package. Python remains the reference implementation and
the default backend. The wheel provides a price and time priority order book,
batch replay of generated background and intervention orders, and event index
ordering. Research orchestration, model generation, impact analysis, and the
execution engine remain in Python.

## Build and use

Install project dependencies first, then build and install the wheel in the
same environment. `rust-toolchain.toml` selects Rust 1.99.1, and the root
development dependency group supplies the Maturin version locked in `uv.lock`:

```bash
uv sync --locked --all-groups --extra microstructure
uv run --locked maturin build --locked --release \
  -m packages/microstructure/rust/Cargo.toml --out /tmp/microstructure-wheels
uv pip install --python .venv/bin/python /tmp/microstructure-wheels/*.whl
TICKNET_REQUIRE_RUST=1 .venv/bin/pytest tests/microstructure -q
```

Use `MatchingEngine(backend="rust")` for the native book. `ReplaySession` then
sends all pending orders through one native call, preserving intervention
priority for equal timestamps and the public `Tick` output type. Call
`sort_simulator_events(events, backend="rust")` for native ordering. These
choices are explicit so an ordinary source install does not require a Rust
compiler or silently switch backends. If the Rust backend is requested and
the wheel is absent, Python raises `ModuleNotFoundError`.

The native wheel targets Python 3.12 and later through `abi3`. Its build is
separate from the root setuptools package; deployments using the native
backend must install both wheels. Order identifiers are assumed unique within
a live book, as in the simulator event contract. Prices and quantities use
signed 64-bit integers in the Rust boundary. No real market data, credentials,
or benchmark output is committed to this repository.

## Correctness and measurement

`tests/microstructure/test_rust_parity.py` compares both backends over seeded
random order streams, cancels, initial levels, anonymous level reduction,
event ordering, and batch replay. The CI Rust job builds the wheel and runs
these tests with `TICKNET_REQUIRE_RUST=1`; without the optional wheel they are
skipped in the regular Python job.

The benchmark generates the same synthetic events for both backends, checks
all ticks and final best prices for equality, and reports median wall time:

```bash
.venv/bin/python scripts/benchmarks/microstructure_replay.py \
  --events 100000 --seed 42 --repeats 5
```

On 2026-09-24 in the development worktree, CPython 3.13.14 and Rust 1.98.1
processed 100,000 background orders and 1,000 interventions in 1.137 seconds
for Python and 0.250 seconds for Rust (4.54× median speedup). Both outputs
were equal. This is a synthetic single-process replay measurement, not a claim
about exchange latency, live execution, or arbitrary market data.

## Fill evidence and impact estimation limits

`ImpactEstimator` currently supports only the Python backend. Rust returns an aggregate trade with the last execution price and counterparty ID, while batch replay returns book ticks only. Neither provides per-fill quantities and prices. Requesting Rust impact estimation raises `NotImplementedError` before changing the session; it does not switch backends or manufacture a VWAP. Existing backend parity tests do not establish per-fill evidence parity.

Python `Trade.fills` retains each actual execution's buyer/seller IDs, price and quantity. Existing `Trade.price` and counterparty ID fields retain their last-fill compatibility meaning. `ReplaySession.fills` adds the triggering event's time and source, including background orders hitting resting child orders. Each `run()` consumes only queued new orders, with cumulative tick and fill history; rerunning an empty queue cannot trade again. Direct book operations are outside replay evidence.

Replay timestamps must be integer milliseconds at or after the processed clock, initially the snapshot timestamp. Earlier events and noninteger times are rejected before enqueueing. `run()` rechecks mutable queued orders before allocating automatic IDs or matching, so a rejected time edit leaves the book, ticks and fills unchanged. Correcting the pending timestamp allows the caller to retry. The impact estimator also validates its child times and pending queue before reserving IDs. Future events may be enqueued out of order within a batch. Equal timestamps may be appended across batches in append order. Intervention-first priority applies within each batch, not retroactively to an earlier batch.

`ImpactResult.filled_volume` counts actual fills attributed to the current schedule's unique child IDs. `unfilled_volume` is requested minus filled quantity, and `execution_vwap` is executed notional divided by executed quantity. With no executions, VWAP and `execution_slippage_bps` are `None`. Execution slippage uses the pre-execution midpoint and adjusts for side, so positive values mean adverse execution. Existing `slippage_bps` retains its side-adjusted midpoint-change meaning; it is neither execution slippage nor causal impact net of background flow.

Children remain limit orders priced at the best opposing quote when the schedule is submitted. Unfilled quantity remains in the book. Results cover only the current `run()` window; later batches do not retroactively revise earlier results. This synthetic execution evidence reconciles simulator accounting and does not establish real-market impact calibration.

`estimate_sqrt_law` remains a synthetic observation helper: its regression uses requested quantity rather than actual executions on the x-axis, and absolute midpoint changes floored at `1e-6` on the y-axis. Its slope is not a calibration of actual execution impact. Such an interpretation requires separately designed execution-volume, background-control and sample-selection rules.
