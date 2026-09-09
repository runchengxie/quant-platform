# Runtime Hardening Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Make `quant-platform` a more auditable runtime kernel by enforcing provenance, order lifecycle invariants, point-in-time data access, explicit risk decisions, and deterministic local lifecycle events.

**Architecture:** Extend existing public contracts and typed execution models in place. Keep runtime events local to `quant-platform`; cross-repository exchange remains versioned artifacts and CLI/API. Add small, pure modules with focused tests rather than introducing a global environment or plugin registry.

**Tech Stack:** Python 3.11+, dataclasses, `typing.Protocol`, pandas, pytest, ruff, uv.

**Spec:** User-approved RQAlpha-inspired runtime hardening proposal in the conversation on 2026-09-09.

## Global Constraints

- Preserve the `portfolio_backtester` namespace and the quant-research → quant-platform → immutable artifact → quant-intel-platform boundary.
- No credentials, real market data, strategy IP, or provider implementations in `quant-platform`.
- Runtime events are deterministic and in-process; artifacts remain immutable and versioned.
- Every new public contract must reject ambiguous or non-point-in-time inputs with clear `ValueError` messages.

### Task 1: Order lifecycle state machine

**Files:**
- Create: `packages/execution/src/quant_execution_engine/lifecycle.py`
- Modify: `packages/execution/src/quant_execution_engine/domain.py`
- Test: `tests/execution/test_order_lifecycle.py`

**Interfaces:**
- Produces `validate_order_transition(current: OrderStatus, event: ExecutionEventType, *, filled_quantity: Decimal, order_quantity: Decimal) -> OrderStatus` and `OrderLifecycleError`.

- [ ] Add failing tests for legal submit/ack/fill/cancel/expire transitions and illegal terminal-state transitions, duplicate fills, and overfills.
- [ ] Implement a table-driven transition map and quantitative invariants using `Decimal`.
- [ ] Export the validator from `domain.py` and run the focused test.
- [ ] Commit `feat: enforce typed order lifecycle transitions`.

### Task 2: Run provenance contract

**Files:**
- Modify: `packages/research-contracts/research_run_manifest.py`
- Modify: `packages/portfolio-backtester/src/portfolio_backtester/backtest_bundle.py`
- Test: `tests/test_run_provenance.py`

**Interfaces:**
- Extend `ResearchRunManifest` with an optional, serialized `provenance: Mapping[str, str]` carrying `data_vintage`, `calendar_version`, `strategy_version`, `engine_version`, `execution_policy`, `cost_model`, and `random_seed`.
- Add `validate_provenance()` requiring non-empty values for execution-aware bundles.

- [ ] Add failing tests for round-trip serialization, missing required provenance, and rejection of blank values.
- [ ] Implement immutable normalization and bundle validation without breaking legacy non-execution manifests.
- [ ] Run manifest and bundle tests.
- [ ] Commit `feat: record runtime provenance in research manifests`.

### Task 3: Point-in-time market data port

**Files:**
- Create: `packages/portfolio-backtester/src/market_data_platform/ports.py`
- Modify: `packages/portfolio-backtester/src/market_data_platform/published_assets.py`
- Test: `tests/test_market_data_pit_port.py`

**Interfaces:**
- `MarketDataPort(Protocol)` exposes `bars(instrument, *, start, end, as_of, knowledge_time)`, `instruments(*, as_of, knowledge_time)`, and `trading_calendar(*, calendar_version)`.
- `MarketDataView` validates `effective_time <= knowledge_time <= as_of` for each returned record and carries `data_vintage` and `calendar_version`.

- [ ] Add failing tests for valid snapshots and future-information rejection.
- [ ] Implement protocol, immutable view, and a dataframe adapter over published assets.
- [ ] Run market-data contract tests and lint.
- [ ] Commit `feat: add point-in-time market data port`.

### Task 4: Explicit pre-trade risk decisions

**Files:**
- Create: `packages/execution/src/quant_execution_engine/risk_pipeline.py`
- Modify: `packages/execution/src/quant_execution_engine/risk.py`
- Test: `tests/execution/test_risk_pipeline.py`

**Interfaces:**
- `RiskOutcome` (`PASS`, `REJECT`, `ADJUST`), `RiskDecision`, `RiskRule(Protocol)`, and `PreTradeRiskPipeline.evaluate(order, portfolio, market_state, config) -> RiskDecision`.

- [ ] Add failing tests for ordered rule evaluation, first rejection, adjustment chaining, and deterministic decision records.
- [ ] Adapt existing `RiskGateChain` guards into pure rules while preserving current summary behavior.
- [ ] Run execution tests.
- [ ] Commit `feat: expose explicit pre-trade risk pipeline`.

### Task 5: Runtime-local lifecycle events

**Files:**
- Create: `packages/execution/src/quant_execution_engine/runtime_events.py`
- Test: `tests/execution/test_runtime_events.py`

**Interfaces:**
- Frozen event dataclasses `TradingDayStarted`, `MarketDataAvailable`, `StrategyEvaluated`, `OrderRequested`, `PreTradeRiskChecked`, `FillGenerated`, `PortfolioUpdated`, `ValuationCompleted`, `TradingDayCompleted`.
- `LocalEventBus.subscribe(event_type, handler)` and `publish(event)`, preserving subscription order and rejecting publication after close.

- [ ] Add failing tests for typed payloads, deterministic ordering, and closed-bus behavior.
- [ ] Implement the in-process bus with no external dependencies.
- [ ] Run the full execution and contract test suites.
- [ ] Commit `feat: add deterministic runtime lifecycle events`.

### Task 6: Documentation and verification

**Files:**
- Create: `docs/architecture/runtime-kernel.md`
- Modify: `README.md`

- [ ] Document ownership, PIT rules, lifecycle transitions, risk outcomes, and the distinction between immutable artifacts and mutable checkpoints.
- [ ] Run `uv sync --locked --all-groups`, `uv run ruff check .`, and `uv run pytest` from the worktree.
- [ ] Commit `docs: describe runtime kernel contracts`.
