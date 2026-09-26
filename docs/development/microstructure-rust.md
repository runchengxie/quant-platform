# Rust microstructure kernel

`packages/microstructure/rust` is an optional PyO3 wheel for the public
`ticknet.simulator` package. Python remains the reference implementation and
the default backend. The wheel provides a price and time priority order book,
batch replay of generated background and intervention orders, and event index
ordering. Research orchestration, model generation, impact analysis, and the
execution engine remain in Python.

## Build and use

Install project dependencies first, then build and install the wheel in the
same environment. `rust-toolchain.toml` selects Rust 1.98.1, and the root
development dependency group supplies the Maturin version locked in `uv.lock`:

```bash
uv sync --locked --all-groups --extra microstructure
uv run --locked maturin build --release \
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
