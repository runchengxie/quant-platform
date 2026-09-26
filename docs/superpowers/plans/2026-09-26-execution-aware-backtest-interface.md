# Execution-aware Backtest Interface Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Expose the platform's complete native execution ledger and publish it through the official execution-aware bundle writer so a durable research Job can consume it.

**Architecture:** `CanonicalBacktestResult` carries an optional full `UnifiedLedger` when native replay runs the execution simulator. A public bundle helper validates the result and delegates serialization to the existing canonical writer. Research Job integration follows only after this provider PR merges.

**Tech Stack:** Python 3.13, pandas, Parquet, `research-contracts`, pytest.

**Spec:** `docs/superpowers/specs/2026-09-26-execution-aware-backtest-interface-design.md`

## Global Constraints

- Keep `portfolio_backtester` import paths and diagnostic result behavior compatible.
- Keep private research logic, vendor data, credentials, and Job scheduling out of `quant-platform`.
- The official `execution_aware` tier requires real order and daily ledger capabilities, a complete `research.clock.v1`, and passed account reconciliation.
- Merge provider before consumer; use independent branches and worktrees.

## Review Focus

- A backend without a full ledger cannot publish an execution-aware bundle.
- Canonical order/fill IDs and daily account values cannot disagree with the attached ledger.
- Missing execution clock fields must reject before publishing an output directory.
- Unbalanced daily NAV must reject rather than produce official evidence.
- Existing diagnostic replay output must retain its historical schema and values.

---

### Task 1: Expose the full ledger on the public backend result

**Files:**
- Modify: `packages/portfolio-backtester/src/portfolio_backtester/backends/base.py`
- Modify: `packages/portfolio-backtester/src/portfolio_backtester/backends/native.py`
- Test: `tests/test_backtest_backends.py`

**Interfaces:**
- `CanonicalBacktestResult.unified_ledger: UnifiedLedger | None` defaults to `None`.
- `NativePositionReplayBackend.run(NativePositionReplayRequest(ledger=True))` returns a result with the full ledger and matching order/fill/daily views.

- [x] Write a failing test asserting a native ledger result exposes all eight tables with matching stable order/fill IDs and reconciled daily account columns; the diagnostic request exposes no ledger.
- [x] Run `uv run pytest tests/test_backtest_backends.py -q` and confirm the new assertion fails because the field is absent (2 expected failures).
- [x] Add the optional field and attach the native simulator ledger after stable IDs are added; validate capability and duplicated frame consistency.
- [x] Run `uv run pytest tests/test_backtest_backends.py -q` and confirm green (10 passed).

### Task 2: Publish a result with the official bundle writer

**Files:**
- Create: `packages/portfolio-backtester/src/portfolio_backtester/backends/bundle.py`
- Modify: `packages/portfolio-backtester/src/portfolio_backtester/backends/__init__.py`
- Test: `tests/test_backtest_bundle.py`

**Interfaces:**
- `write_execution_aware_result_bundle(output_dir: Path, *, result: CanonicalBacktestResult, run_id: str, research_clock: Mapping[str, Any], producer: Mapping[str, Any], configuration_sha256: str, input_refs: Sequence[Mapping[str, Any]] = (), diagnostics: Mapping[str, Any] | None = None) -> BacktestBundleManifest`.

- [x] Write a failing synthetic test that publishes a native ledger result, reloads and verifies the official manifest, and checks the order/fill/daily tables. Add rejection tests for no ledger, false capabilities, missing clock, and unbalanced NAV.
- [x] Run `uv run pytest tests/test_backtest_bundle.py -q` and confirm the new tests fail because the helper is absent (4 expected failures).
- [x] Implement the helper using `write_backtest_bundle` and export it from `portfolio_backtester.backends`.
- [x] Run `uv run pytest tests/test_backtest_bundle.py tests/test_backtest_backends.py -q` and confirm green (28 passed).

### Task 3: Document, verify, and merge provider

**Files:**
- Modify: `docs/concepts/backend-architecture.md`
- Modify: `docs/concepts/canonical-backtest-bundle.md`

- [x] Document the full-ledger result field, official writer, and distinction between historical period performance and execution-aware daily NAV.
- [x] Run `uv run ruff check .`, `uv run ty check --error-on-warning`, `uv run pytest`, `uv run mkdocs build --strict`, and `git diff --check`; record exact results. Ruff and ty passed; after fixing the two new Chinese punctuation style violations, full pytest passed (1,465 passed, 12 skipped, 8 existing warnings), strict MkDocs passed, and diff check passed.
- [ ] Review, commit, push, open a PR to main, complete required checks/review, merge, and clean only this task's branch/worktree.

### Task 4: Consume the merged provider in research Jobs

**Files:**
- Create a separate `quant-research` worktree after Task 3 merges.
- Modify: `src/ticknet/research/backtest_jobs.py`, `src/ticknet/research/backtest_worker.py`, `docs/agents/backtest-jobs.md`.
- Test: `tests/microstructure/test_backtest_jobs.py` and relevant worker tests.

- [ ] Pin the merged platform commit, introduce strict versioned execution-aware Job request validation, and preserve v1 diagnostic behavior.
- [ ] Write failing end-to-end tests for official bundle publication, hash-verified retrieval, and fail-closed invalid clock/account cases.
- [ ] Implement the worker integration, run the research repository's required locked-dependency tests and static checks, then review and merge its own PR.
