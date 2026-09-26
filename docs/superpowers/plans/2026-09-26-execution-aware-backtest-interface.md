# Execution-aware Backtest Interface Implementation Plan

本文件记录接口拆分时的实施过程。当前回测任务用法、合成示例和部署说明以 [quant-backtest-runtime 文档](https://github.com/runchengxie/quant-backtest-runtime)为准。文中的提交号和生产指针是当时的验证记录。

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Expose the platform's complete native execution ledger and publish it through the official execution-aware bundle writer so a separately deployed backtest runtime can consume it.

**Architecture:** `CanonicalBacktestResult` carries an optional full `UnifiedLedger` when native replay runs the execution simulator. A public bundle helper validates the result and delegates serialization to the existing canonical writer. The independent Job runtime and research compatibility migration follow only after this provider PR merges.

**Tech Stack:** Python 3.13, pandas, Parquet, `research-contracts`, pytest.

**Spec:** `docs/superpowers/specs/2026-09-26-execution-aware-backtest-interface-design.md`

## Global Constraints

- Keep `portfolio_backtester` import paths and diagnostic result behavior compatible.
- Keep private research logic, vendor data, credentials, Job scheduling, and deployment out of `quant-platform`.
- The official `execution_aware` tier requires real order and daily ledger capabilities, a complete `research.clock.v1`, and passed account reconciliation.
- Merge provider before consumer; use independent branches and worktrees.

## Review Focus

- A backend without a full ledger cannot publish an execution-aware bundle.
- Canonical order/fill IDs and daily account values cannot disagree with the attached ledger.
- Missing, malformed, or causally reversed execution clock fields must reject before publishing an output directory.
- Unbalanced daily NAV must reject rather than produce official evidence.
- Existing diagnostic replay output must retain its historical schema and values.
- Empty execution ledgers must retain diagnostic semantics; zero-fill bundles retain ID columns.
- Official publication requires at least one verifiable input lineage reference.

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
- [x] Fix the reviewed empty-ledger edge case: test a disabled simulator first, then retain a diagnostic result without claiming full execution evidence.

### Task 2: Publish a result with the official bundle writer

**Files:**
- Create: `packages/portfolio-backtester/src/portfolio_backtester/backends/bundle.py`
- Modify: `packages/portfolio-backtester/src/portfolio_backtester/backends/__init__.py`
- Test: `tests/test_backtest_bundle.py`

**Interfaces:**
- `write_execution_aware_result_bundle(output_dir: Path, *, result: CanonicalBacktestResult, run_id: str, research_clock: Mapping[str, Any], producer: Mapping[str, Any], configuration_sha256: str, input_refs: Sequence[Mapping[str, Any]], diagnostics: Mapping[str, Any] | None = None) -> BacktestBundleManifest`.

- [x] Write a failing synthetic test that publishes a native ledger result, reloads and verifies the official manifest, and checks the order/fill/daily tables. Add rejection tests for no ledger, false capabilities, missing clock, and unbalanced NAV.
- [x] Run `uv run pytest tests/test_backtest_bundle.py -q` and confirm the new tests fail because the helper is absent (4 expected failures).
- [x] Implement the helper using `write_backtest_bundle` and export it from `portfolio_backtester.backends`.
- [x] Run `uv run pytest tests/test_backtest_bundle.py tests/test_backtest_backends.py -q` and confirm green (28 passed).
- [x] Fix reviewed edge cases with failing tests first: reject malformed/reversed clocks and missing input lineage, and retain ID columns in zero-fill tables (33 focused tests passed).

### Task 3: Document, verify, and merge provider

**Files:**
- Modify: `docs/concepts/backend-architecture.md`
- Modify: `docs/concepts/canonical-backtest-bundle.md`

- [x] Document the full-ledger result field, official writer, and distinction between historical period performance and execution-aware daily NAV.
- [x] Run `uv run ruff check .`, `uv run ruff format --check .`, `uv run ty check --error-on-warning`, `uv run pytest`, `uv run mkdocs build --strict`, and `git diff --check` after the reviewed fixes; record exact results. All passed: 1,470 tests passed, 12 skipped, 8 existing warnings; 986 Python files formatted; strict documentation build completed. The required `input_refs` signature was tightened after this run and received focused verification.
- [x] Review, commit, push, open a PR to main, complete required checks/review, merge, and clean only this task's branch/worktree. Provider [PR #61](https://github.com/runchengxie/quant-platform/pull/61) merged as `3ede35924d124ebdb2ada89bbcd23d3f9ced82b9`; the task branch and worktree were removed.

### Task 4: Move Job orchestration into an independent runtime

**Files:**
- Create a dedicated `quant-backtest-runtime` repository and release unit after Task 3 merges.
- Migrate the generic Job contract, SQLite lifecycle, worker, CLI, artifact resolver, and result verifier from `quant-research`.
- Replace the research Job implementation with a thin CLI client and retain read-only access to historical Jobs.

- [x] Pin the merged platform commit in the runtime, introduce strict versioned execution-aware Job request validation, and preserve v1 diagnostic behavior.
- [x] Write failing end-to-end tests for official bundle publication, hash-verified retrieval, and fail-closed invalid clock/account cases.
- [x] Implement runtime Job orchestration and worker controls in its own SQLite-backed service, review and merge the runtime [PR #1](https://github.com/runchengxie/quant-backtest-runtime/pull/1). The public runtime's [main CI](https://github.com/runchengxie/quant-backtest-runtime/actions/runs/36213742003) passes locked dependency installation, Ruff, and all 18 tests.
- [x] Replace the research-side implementation with a thin client and historical-job reader, run the research repository's locked-dependency tests, and merge [PR #247](https://github.com/runchengxie/quant-research/pull/247) as `40b787811a75b4b9ab249c1dacff48c757fc9df5` (3,825 passed, 6 skipped). The old Registry remains read-only for explicit historical status/result queries.
- [x] Build a commit-addressed runtime release and dry-run its service and rollback path with data, logs, and credentials outside the release directory before any production switch. Runtime `current` points to `2dc8b44a4f3dd1bb71a3794cdaad88ffee4c79a0`; initial switch, rollback, and re-switch passed. Research `current` points to `40b787811a75b4b9ab249c1dacff48c757fc9df5` after the old-Job preflight passed. A production research CLI → stable runtime v2 Job completed and its official result verified with isolated data.
