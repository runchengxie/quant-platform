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
