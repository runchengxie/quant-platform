# Execution-aware Backtest Interface Design

## Intent and boundary

The public `portfolio_backtester` package owns deterministic backtest execution and the versioned canonical bundle. `quant-research` owns durable Job scheduling, private strategies, artifact lookup, and run provenance. Published market data remains an input artifact; neither package downloads it during a backtest.

The next deliverable is an execution-aware Job whose official evidence is `portfolio_backtester.backtest_result.v1`. Diagnostic v1 Jobs keep their existing behavior and result schema. This design does not promote a run by itself: research promotion still needs a matching root `ResearchRunManifest` and its own gate.

## Current gap

`NativePositionReplayBackend(ledger=True)` calls the shared execution simulator and returns orders, fills, and a combined daily ledger in `CanonicalBacktestResult`. The official bundle writer requires an eight-frame `UnifiedLedger`. The backend currently discards that value, so a caller cannot publish the official bundle without reconstructing it outside the platform. The research Job worker consequently emits only `ticknet.backtest_job_result.v1` and rejects `execution_aware`.

## Platform provider

1. Add optional `unified_ledger: UnifiedLedger | None` to `CanonicalBacktestResult`. It is absent when the backend did not compute a full ledger. `frames()` and the existing result schema remain unchanged for diagnostic consumers.
2. When native replay has `ledger=True`, attach the simulator's `UnifiedLedger`. Its orders and fills must use the same stable IDs exposed in the canonical result. The daily account columns must agree with the canonical daily view. Reject a result that claims a full ledger without order lifecycle and daily ledger capabilities, or whose duplicated tables disagree.
3. Publish `write_execution_aware_result_bundle(output_dir, *, result, run_id, research_clock, producer, configuration_sha256, input_refs, diagnostics)` in `portfolio_backtester.backends`. It requires the complete ledger, delegates bundle validation and atomic publication to the existing `write_backtest_bundle`, and returns the official manifest. Incomplete capability, clock, account reconciliation, or immutable output checks fail closed.
4. `CanonicalBacktestResult.performance` remains the historical period-return view. For execution-aware evidence, consumers read `daily_nav` from the official bundle. This distinction is documented in the public backend and bundle guides.

## Research consumer after provider merge

1. Add an opt-in versioned Job request for execution-aware replay. It requires `ledger=True`, a complete caller-supplied `research.clock.v1`, producer identity, and immutable hash-addressed inputs. It rejects missing or ambiguous clock information before scheduling.
2. The worker calls the merged public platform API and stores the official bundle beside the Job's versioned result manifest. The Job result points to both manifest digests, and retrieval verifies all official bundle files. A failure before publication leaves no successful result.
3. Preserve v1 diagnostic requests and result reads. Add synthetic end-to-end tests for a valid ledger and for missing clock, false capability, mismatched account values, corrupted files, cancellation, and existing diagnostic behavior.
4. The Job result does not itself satisfy research promotion. A later explicit research run may bind the verified bundle to a root run manifest.

## Delivery order

Merge the `quant-platform` provider PR, then pin that reachable commit in `quant-research` and merge the consumer PR. Do not depend on a development worktree or unmerged commit.
