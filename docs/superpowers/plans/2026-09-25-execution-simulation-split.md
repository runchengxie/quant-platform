# Execution Simulation Split Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Split the 1,065-line execution simulation core by responsibility while preserving every current import path, simulation result, and table schema.

**Architecture:** Move function groups into capacity simulation, adjusted NAV, ideal NAV, and table preparation modules. Retain `execution_sim.core` as a compatibility facade. Update the white-box monkeypatch test to patch the true function owner or preserve a tested compatibility hook.

**Tech Stack:** Python, pandas, NumPy, pytest, Ruff, ty.

**Spec:** `docs/superpowers/specs/2026-09-25-quality-modularization-and-production-design.md`

**实施记录（2026-09-25）：**模块拆分已由 [PR #49](https://github.com/runchengxie/quant-platform/pull/49) 完成，后续静态检查债务由 PR #53–55 清理。兼容导入、结果列和顺序均有回归覆盖。

## Global Constraints

- Build a fresh worktree from latest `origin/main` and submit one focused PR.
- Preserve all public and currently used `core.py` symbols and `execution_sim.__init__` exports.
- Preserve numerical results, event order, fees, corporate actions, row order, and output schemas.
- Keep the lifecycle distinction `desired target -> rebalance plan -> order -> fill` visible in tests and docs.
- Do not combine behavior changes with file moves.

## Review Focus

- A patched `_build_execution_tables` is called by the simulation path.
- Empty, one-row, and multi-day inputs produce the same schema and values.
- Missing and non-tradable securities preserve current handling.
- Corporate-action dates and order/fill dates remain aligned.
- All compatibility imports resolve through both `core.py` and package exports.

---

### Task 1: Record golden behavior and public symbols

**Files:**
- Test: `tests/test_execution_sim.py`
- Source: `packages/portfolio-backtester/src/portfolio_backtester/execution_sim/core.py`
- Source: `packages/portfolio-backtester/src/portfolio_backtester/execution_sim/__init__.py`

**Interfaces:**
- Consumes: existing simulator API and deterministic fixtures.
- Produces: recorded exports, baseline outputs, and a list of function groups before moving code.

- [x] Run `uv run --locked python -m pytest tests/test_execution_sim.py -q` and save the baseline output through pytest assertions rather than checked-in generated files.
- [x] List functions and their callers with `rg -n '^def |^class |from .*execution_sim\.core|import .*execution_sim\.core' packages tests`.
- [x] Add assertions for stable output columns, row ordering, and key numeric values to tests using existing small fixtures.
- [x] Record `execution_sim.__init__.__all__`, all public names available from `core.py`, and every direct consumer import.

### Task 2: Move table preparation behind a compatibility facade

**Files:**
- Create: `packages/portfolio-backtester/src/portfolio_backtester/execution_sim/table_preparation.py`
- Modify: `packages/portfolio-backtester/src/portfolio_backtester/execution_sim/core.py`
- Modify: `tests/test_execution_sim.py`

**Interfaces:**
- Produces: the table preparation functions consumed by the other simulation modules; `core.py` re-exports existing function names.

- [x] Move only table/pre-tradability preparation helpers and their direct imports.
- [x] Keep `core.py` names as imported re-exports and verify function signatures with `inspect.signature` assertions for public names.
- [x] Patch `_build_execution_tables` at its new defining module in the test, then assert the public simulation entry invokes the patched function.
- [x] Run `uv run --locked python -m pytest tests/test_execution_sim.py -q`.

### Task 3: Move adjusted and ideal NAV flows

**Files:**
- Create: `packages/portfolio-backtester/src/portfolio_backtester/execution_sim/adjusted_nav.py`
- Create: `packages/portfolio-backtester/src/portfolio_backtester/execution_sim/ideal_nav.py`
- Modify: `packages/portfolio-backtester/src/portfolio_backtester/execution_sim/core.py`
- Test: `tests/test_execution_sim.py`

**Interfaces:**
- Consumes: table-preparation helpers and existing data models.
- Produces: unchanged adjusted-NAV and ideal-NAV entrypoints through `core.py`.

- [x] Move adjusted NAV planning, daily execution, ledger, and output helpers as one cohesive group.
- [x] Move ideal NAV target, ledger, and daily result helpers as a separate cohesive group.
- [x] Preserve target, feasible-plan, and realized-fill columns exactly.
- [x] Run `uv run --locked python -m pytest tests/test_execution_sim.py tests/test_execution_sim_market_rules.py tests/test_execution_sim_quote_safety.py -q`.

### Task 4: Move capacity simulation and verify package exports

**Files:**
- Create: `packages/portfolio-backtester/src/portfolio_backtester/execution_sim/capacity_simulation.py`
- Modify: `packages/portfolio-backtester/src/portfolio_backtester/execution_sim/core.py`
- Modify: `packages/portfolio-backtester/src/portfolio_backtester/execution_sim/__init__.py`
- Test: `tests/test_execution_sim.py`

**Interfaces:**
- Produces: all existing `execution_sim` public functions through the old import locations.

- [x] Move capacity execution and its private cohesive helpers.
- [x] Keep `core.py` as re-exports and update `__init__.py` only when needed to preserve the same public surface.
- [x] Compare sorted old/new public names with a test and import each public name through the package and compatibility module.
- [x] Run `uv run --locked python -m pytest tests/test_execution_sim.py tests/test_execution_sim_market_rules.py tests/test_execution_sim_quote_safety.py -q`.

### Task 5: Clean static debt and commit

**Files:**
- Modify only: execution simulation source and tests above.

**Interfaces:**
- Consumes: Tasks 1–4.
- Produces: split modules with no Ruff or blocking `ty` diagnostics.

- [x] Run `uv run --locked ruff check packages/portfolio-backtester/src/portfolio_backtester/execution_sim tests/test_execution_sim.py tests/test_execution_sim_market_rules.py tests/test_execution_sim_quote_safety.py` and fix each finding without broad rule suppressions.
- [x] Run `uv run --locked ty check --error-on-warning packages/portfolio-backtester/src/portfolio_backtester/execution_sim tests/test_execution_sim.py tests/test_execution_sim_market_rules.py tests/test_execution_sim_quote_safety.py` and fix type issues at their source.
- [x] Remove the relevant Ruff exclusion only when the full owning package is clean under the configured rules.
- [x] Run the complete portfolio backtester unit test selection from CI.
- [x] Commit code movement and static cleanup separately, with the golden behavior tests included before the moves.
