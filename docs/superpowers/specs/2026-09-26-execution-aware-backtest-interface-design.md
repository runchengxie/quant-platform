# Execution-aware Backtest Interface Design

## Intent and boundary

The public `portfolio_backtester` package owns deterministic backtest execution and the versioned canonical bundle. Today, `quant-research` owns durable Job scheduling as well as private strategies and run provenance. The target is a separately deployable backtest runtime that owns Job scheduling, artifact lookup, workers, and result publication. Research retains private strategy decisions and run promotion. Published market data remains an input artifact; backtest execution does not download vendor data.

The next deliverable is a public platform interface usable by that runtime, followed by an execution-aware Job whose official evidence is `portfolio_backtester.backtest_result.v1`. Existing diagnostic v1 Jobs keep their behavior and result schema during migration. This design does not promote a run by itself: research promotion still needs a matching root `ResearchRunManifest` and its own gate.

## Current gap

`NativePositionReplayBackend(ledger=True)` calls the shared execution simulator and returns orders, fills, and a combined daily ledger in `CanonicalBacktestResult`. The official bundle writer requires an eight-frame `UnifiedLedger`. The backend currently discards that value, so a caller cannot publish the official bundle without reconstructing it outside the platform. The research Job worker consequently emits only `ticknet.backtest_job_result.v1` and rejects `execution_aware`.

## Platform provider

1. Add optional `unified_ledger: UnifiedLedger | None` to `CanonicalBacktestResult`. It is absent when the backend did not compute a full ledger. `frames()` and the existing result schema remain unchanged for diagnostic consumers.
2. When native replay has `ledger=True` and a nonempty daily ledger, attach the simulator's `UnifiedLedger`. Its orders and fills must use the same stable IDs exposed in the canonical result, including columns in zero-row tables. The daily account columns must agree with the canonical daily view. If the simulator returns no daily account rows and no lifecycle rows, preserve a diagnostic result with no full ledger. Reject a result that claims a full ledger without order lifecycle and daily ledger capabilities, or whose duplicated tables disagree.
3. Publish `write_execution_aware_result_bundle(output_dir, *, result, run_id, research_clock, producer, configuration_sha256, input_refs, diagnostics)` in `portfolio_backtester.backends`. It requires the complete ledger and at least one digest-bearing lineage input, delegates bundle validation and atomic publication to the existing `write_backtest_bundle`, and returns the official manifest. Incomplete capability, malformed or causally reversed clock, account reconciliation, or immutable output checks fail closed.
4. `CanonicalBacktestResult.performance` remains the historical period-return view. For execution-aware evidence, consumers read `daily_nav` from the official bundle. This distinction is documented in the public backend and bundle guides.

## Independent runtime and research migration after provider merge

1. Create a dedicated runtime repository and release unit (working name `quant-backtest-runtime`). Move the generic local Job lifecycle, worker controls, CLI, artifact validation, and result publication out of the research Registry into its own SQLite store. Preserve existing Job identifiers and provide a read-only migration path for historical research jobs; do not copy live implementations into two owners.
2. Add a versioned execution-aware Job request. It requires `ledger=True`, a complete caller-supplied `research.clock.v1`, producer identity, and immutable hash-addressed inputs. It rejects missing or ambiguous clock information before scheduling.
3. The worker calls the merged public platform API and stores the official bundle beside a versioned Job result manifest. Retrieval verifies both manifest digests and every official bundle file. A failure before publication leaves no successful result. Preserve diagnostic v1 request and result compatibility during cutover, with synthetic end-to-end coverage for valid and invalid clocks, capabilities, account values, corrupted files, and cancellation.
4. Replace the research-side Job implementation with a thin client/compatibility adapter. Research promotion binds a verified bundle to a separate root run manifest; the Job result alone does not satisfy promotion.
5. Build and verify a dedicated release under `/home/richard/code/production/quant-backtest-runtime/releases/<commit>` with a stable `current` pointer. Put the SQLite database, inputs, results, logs, and credentials outside releases. Run a dry-run and rollback check before switching any scheduled task or production caller.

## Delivery order

Merge the `quant-platform` provider PR, then pin that reachable commit in the independent runtime. Migrate `quant-research` consumers only after the runtime API and release path exist. Each repository uses its own PR; no production path depends on a development worktree or unmerged commit.
