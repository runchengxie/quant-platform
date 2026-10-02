# Canonical Backtest Evidence Bundle

Language: English · [简体中文](canonical-backtest-bundle.md)

`portfolio_backtester.backtest_result.v1` stores one backtest's unified ledger in a hash-verified directory that can be reloaded. It is the evidence handoff for a run. The existing `CanonicalBacktestResult` remains the in-memory result; the bundle does not introduce another order, fill, or cash model.

## Evidence tiers

`BacktestEvidenceTier` has two values:

- `diagnostic` permits ideal fills, target-weight returns, or a compatibility result without complete order and cash evidence. It can be written as a bundle, but does not establish executable NAV evidence.
- `execution_aware` requires the backend to declare `order_lifecycle` and `daily_ledger` capabilities, a valid `research.clock.v1` execution window, and a reconciled unified ledger.

An execution-aware run may have zero orders or fills when no trade is needed. Empty tables remain valid if the backend truly supports the capabilities and the required ledger frames are present.

## Directory and manifest

The writer publishes these files:

```text
backtest_result/
  manifest.json
  targets.parquet
  orders.parquet
  fills.parquet
  daily_positions.parquet
  daily_cash.parquet
  daily_nav.parquet
  cost_breakdown.parquet
  turnover_breakdown.parquet
  diagnostics.json
```

`manifest.json` records the schema, run ID, evidence tier, `research.artifact-envelope.v2`, `research.clock.v1` mapping, backend identity and capabilities, upstream artifact references, file hashes and row counts, and reconciliation result. An optional `tca_calibration` receipt records a versioned cost estimate from fill observations. The writer stores that receipt for audit; it does not apply the suggested cost or change the evidence tier.

The envelope's `content_sha256` hashes the canonical file inventory. The manifest is outside that inventory to avoid a self-reference.

## Accounting check

`reconcile_unified_ledger` aligns `daily_positions.positions_value`, `daily_cash.cash`, and `daily_nav.nav` by `trade_date` and requires:

```text
nav = cash + positions_value
```

It allows a small floating-point tolerance relative to account size. Duplicate or mismatched dates, nonnumeric accounting values, and larger differences fail validation.

## Writing and reading

`write_backtest_bundle` writes Parquet and JSON into a temporary sibling directory, calculates the inventory hash, builds the artifact envelope, and publishes the finished directory with an atomic rename. It refuses to overwrite an existing target and removes the temporary directory after an intermediate failure.

`read_backtest_bundle` validates the manifest schema, evidence-tier file requirements, artifact envelope, inventory content hash, and each file's SHA-256 by default. It does not rerun portfolio construction, orders, fills, or PnL calculations.

Callers with a `CanonicalBacktestResult` can use `portfolio_backtester.backends.write_execution_aware_result_bundle`. That helper requires a complete `unified_ledger`, checks the result against it, and then calls the bundle writer. `NativePositionReplayBackend` provides this ledger when `ledger=True` and a nonempty daily ledger exists. Empty order or fill tables retain their ID columns in a valid no-trade period. The caller supplies the execution clock, producer, configuration hash, and at least one input reference. Missing evidence or failed reconciliation prevents publication.

`daily_nav.parquet` is the execution-aware daily NAV record. The result object's `performance` remains the historical period-replay return view.

## Clock boundary

For an `execution_aware` bundle, the writer checks the required `research.clock.v1` fields and calls `research_contracts.validate_research_clock(..., require_execution=True)`. `write_execution_aware_result_bundle` accepts one decision clock and rejects a result whose `decision_count` exceeds one. A sequence of decisions needs a clock for each decision; one bundle clock cannot establish timing for the whole sequence.
