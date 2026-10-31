# Backtest backend boundary

Language: English · [简体中文](backend-architecture.md)

This page describes the backtest backend APIs that exist on `main`, their limits, and the status of framework integrations. It distinguishes the registered backend from a separately callable execution API.

## Current state

`BackendRegistry` currently registers only `native.position_replay`, implemented by `NativePositionReplayBackend`. The package also exports `SequencedExecutionBackend`, which callers instantiate directly; it is not registered there. Neither API adapts a third-party backtesting framework. The `pyqlib` package is declared only in an optional dependency extra; that does not provide a Qlib backend. LEAN, Backtrader, and vn.py have no current backend adapter here.

`NativePositionReplayBackend` normalizes the existing period-return position replay into `CanonicalBacktestResult`. With `ledger=True`, it also runs the shared execution simulator and attaches orders, fills, and a daily ledger when one is produced. Its default period-return mode does not claim order-level execution evidence.

`SequencedExecutionBackend` runs targets from multiple decisions through the shared daily execution simulator. Each decision needs a `research.clock.v1` execution clock. The caller remains responsible for proving that every input used to produce each target was visible by its information cutoff. See [Sequenced execution](../guides/sequenced-execution.en.md) for the request contract.

The registry requires explicit registration and performs no plugin discovery. Framework names and historical proposals are not callable capabilities merely because they appear in old notes.

## Framework status

| Name | Status on `main` | Role |
| --- | --- | --- |
| `native.position_replay` | Registered and supported | Deterministic period-return position replay; optional execution-ledger output |
| `native.sequenced_execution` | Public standalone API; not registered | Clocked multi-decision execution through the shared simulator |
| Qlib | Historical candidate not merged | No current runtime role |
| LEAN | Historical candidate not merged | Architecture reference only; the pinned 2026-09 feasibility study rejected adoption |
| Backtrader | Planned | No adapter, dependency, or registry entry |
| vn.py | Out of scope | Gateways, live transport, and broker execution belong to an execution system |

The [framework integration ledger](https://github.com/runchengxie/quant-platform/blob/main/docs/framework-integration-ledger.yml) records machine-readable status. The [LEAN feasibility report](lean-differential-spike-2026-09.md) did not run runtime parity and does not claim that its coverage or performance gates passed.

## Stable contracts

`portfolio_backtester.backends` exports `BacktestBackend`, `BackendCapabilities`, `CanonicalBacktestResult`, `BackendRegistry`, both native APIs, and `write_execution_aware_result_bundle`. A backend declares its supported order lifecycle, partial fills, daily ledger, and long/short behavior. A result must not imply capabilities it did not produce.

For native position replay, the default `ledger=False` path leaves order, fill, and daily-ledger views unavailable. When ledger mode produces a non-empty daily ledger, the canonical result also carries the unified execution ledger. The execution-aware bundle writer validates the result against that ledger and requires valid clock and provenance inputs before publishing. In that bundle, `daily_nav.parquet` is the execution-aware NAV source; `CanonicalBacktestResult.performance` remains the period-return replay view. See [Canonical backtest bundle](canonical-backtest-bundle.en.md).

The native position-replay adapter rejects short positions and negative weights. Stale execution prices require explicit opt-in. Intraday inputs require an explicit timing assumption or caller-windowed data.

## Market behavior stays in the native simulator

The shared implementation owns the A-share behaviors used by current research, including T+1 sellable quantity, round-lot buys and odd-lot sells, directional price limits, suspensions and listing events, dated fees, corporate actions, point-in-time inputs, and execution timestamps. A framework adapter must preserve the relevant semantics rather than silently narrowing them.

Before adding an adapter, compare it against the fixed scenarios in the [integration ledger](https://github.com/runchengxie/quant-platform/blob/main/docs/framework-integration-ledger.yml): liquid long-only parity, A-share market rules, and capacity with partial fills. Adoption also requires canonical outputs, classified residual differences, preserved market semantics, documented rollback, and the registered replacement gates. Passing these gates permits review; it does not automatically replace the native implementation.

## Project boundary

This repository maintains reusable portfolio, accounting, and execution mechanisms. It does not add a generic event engine, gateway, order-management system, strategy lifecycle, parameter optimizer, data feed, or market-agnostic broker simulator. Strategy assumptions, proprietary features, data access, and orchestration belong to callers or other projects.

## Independent Rust engine

[quant-backtest-engine](https://github.com/runchengxie/quant-backtest-engine) is the
independent Rust library and CLI for new direct NautilusTrader integration. Its first
release uses a versioned order-intent/quote request and final-snapshot result contract.
The engine depends on neither this platform nor the runtime; the runtime supervises
its executable through an opt-in job version and retains state/publication ownership.

This platform continues to own portfolio construction, analytics and its existing
Python backends as compatibility references. No existing imports, default backends or
financial results change. Do not copy the whole portfolio-backtester package into the
new repository: it also contains portfolio and research utilities. Target weights need
an explicit sizing contract before they become engine orders.

The new engine currently covers synthetic USD cash equities and market orders. It
has no verified A-share T+1, price-limit, corporate-action, capacity or daily-ledger
parity. Its final snapshot cannot be presented as this platform's execution-aware
bundle. Migration requires matched timing, fees, account balances and per-trade
comparisons, then an explicitly versioned adapter; old APIs remain until consumers
have migrated and those comparisons pass. The new engine's published supported
capabilities are the authority for its own request version.

### Explicit session engine client

`portfolio_backtester.backends.engine_sessions.EngineClient` is an opt-in consumer
of the independent engine's `size` and `run` commands. Existing registry entries,
Python defaults, and package namespaces are unchanged. Select an absolute executable
path and its SHA256 content digest explicitly; the client verifies the digest before
every subprocess call, executes a private snapshot of those verified bytes,
uses an argument list and a temporary JSON request file,
and applies a finite timeout (30 seconds by default).

```python
from pathlib import Path
from portfolio_backtester.backends.engine_sessions import EngineClient

client = EngineClient(
    Path("/absolute/release/quant-backtest-engine"),
    sha256=release_digest,
    source_revision=release_commit,
)
plan = client.size(sizing_request)  # sizing_request.v1 -> sizing_result.v1
result = client.run_sessions(session_request)  # engine_request.v2 -> canonical result
```

Requests follow the provider's versioned contracts; decimal amounts remain strings.
The client delegates validation of trading inputs, sizing, admission and execution to
the engine. A sizing plan's projected sale proceeds and cash are estimates. Actual
execution rechecks available cash; a plan does not guarantee fills. Synthetic examples
live in `tests/fixtures/engine_sessions/`.

Session results map daily balances, positions, orders and fills into
`CanonicalBacktestResult`. Dates use Asia/Shanghai for CNY and UTC for USD.
Reconciliation checks identity, quantities, daily cash, positions, fees and NAV;
wire accounting uses exact Decimal equality, with fill notionals rounded to two
currency decimals using ROUND_HALF_EVEN, matching upstream Money conversion. Decimal wire values and
all denial reasons, active-rule metadata and backend metadata remain available in
`result.metadata['engine_result']`. Canonical daily money columns and weights use
floats for compatibility. Fill IDs are stable indices within the provider output.
The executable digest and optional caller-supplied source revision record provenance;
the caller is responsible for trusting the selected binary and its release source.

This adapter does not create a unified execution ledger or claim the platform's
full `execution_aware` bundle. It has no corporate-action, adjusted-price, shorting,
strategy-generation, data-loading, or runtime orchestration support. It never
registers itself automatically. The provider owns engine contracts and financial
semantics; this repository owns only transport, reconciliation and normalization.

To run the optional real binary integration test, set `SESSION_ENGINE_BINARY` to
the explicitly selected absolute path and `SESSION_ENGINE_SHA256` to its digest.
The test skips when no binary is selected; the synthetic malformed-response tests
always run.

The synthetic wire fixtures were verified against merged provider revision
`3ee74bfa21d743e595ce61d0ac06b97dd588ebd6` (NautilusTrader 0.66.0).
