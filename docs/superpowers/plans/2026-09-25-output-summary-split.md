# Output Summary Split Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Split `output_summary_sections.py` by summary domain while preserving every serialized key, value shape, path representation, date format, and legacy import.

**Architecture:** Keep `build_run_summary_sections` as the aggregation entrypoint. Move cohesive section builders to dedicated modules and keep a compatibility facade that re-exports current builder names. Share only formatting helpers that have multiple real callers.

**Tech Stack:** Python, pandas, pytest, Ruff, ty.

**Spec:** `docs/superpowers/specs/2026-09-25-quality-modularization-and-production-design.md`

**实施记录（2026-09-25）：**已由 [PR #52](https://github.com/runchengxie/quant-platform/pull/52) 完成。摘要模块按职责拆分，旧导入路径、章节顺序及空值行为有回归覆盖。

## Global Constraints

- Use a fresh worktree based on latest `origin/main` and a focused PR.
- Preserve the current output JSON shape exactly, including absent/null distinctions.
- Keep direct imports from `output_summary_sections.py` working.
- Do not add new output sections or schema fields during the split.
- Keep Chinese-facing documentation natural and use Chinese punctuation where appropriate.

## Review Focus

- Missing optional context values serialize exactly as before.
- `Path`, date, NumPy scalar, and DataFrame values keep the same representation.
- Summary ordering and nested keys remain stable.
- Direct imports of private builder functions used by tests still resolve.
- Pipeline outputs remain byte-equivalent for fixed fixtures where serialization is deterministic.

---

### Task 1: Snapshot output contract and import surface

**Files:**
- Test: `tests/orchestration/` summary and output tests found by `rg -l 'build_run_summary_sections|output_summary_sections' tests/orchestration`
- Source: `packages/orchestration/src/strategy_pipeline/pipeline/output_summary_sections.py`

**Interfaces:**
- Consumes: current summary builder API and existing output fixtures.
- Produces: explicit output contract assertions and a complete compatibility symbol list.

- [x] Run `uv run --locked python -m pytest tests/orchestration -q` and record summary-focused test names.
- [x] Run `rg -n '^def |^class ' packages/orchestration/src/strategy_pipeline/pipeline/output_summary_sections.py` and `rg -n 'output_summary_sections import|output_summary_sections\.' packages tests`.
- [x] Add assertions for section keys, nested keys, null/absent values, and representative path/date/scalar formatting.
- [x] Run the output-focused tests and confirm the assertions pass before moving code.

### Task 2: Extract shared formatting helpers and run/data sections

**Files:**
- Create: `packages/orchestration/src/strategy_pipeline/pipeline/output_summary_formatting.py`
- Create: `packages/orchestration/src/strategy_pipeline/pipeline/output_summary_run_sections.py`
- Modify: `packages/orchestration/src/strategy_pipeline/pipeline/output_summary_sections.py`
- Test: summary tests identified in Task 1

**Interfaces:**
- Produces: formatting helpers and run/data/model builders, re-exported from the compatibility facade.

- [x] Move only formatting helpers with multiple actual call sites, retaining argument and return behavior.
- [x] Move run input, model, and training-data summary builders as one domain group.
- [x] Re-export existing function names from `output_summary_sections.py`.
- [x] Run the output-focused tests and compare serialized fixture outputs.

### Task 3: Extract evaluation/backtest and positions/execution sections

**Files:**
- Create: `packages/orchestration/src/strategy_pipeline/pipeline/output_summary_eval_sections.py`
- Create: `packages/orchestration/src/strategy_pipeline/pipeline/output_summary_execution_sections.py`
- Modify: `packages/orchestration/src/strategy_pipeline/pipeline/output_summary_sections.py`
- Test: `tests/orchestration/` output tests identified in Task 1

**Interfaces:**
- Produces: focused builders for evaluation/backtest and holdings/execution summaries, retaining old imports.

- [x] Move evaluation and backtest section functions without changing their call order or keys.
- [x] Move holdings, fills, and execution section functions as a cohesive group.
- [x] Add direct parity assertions for missing fills, empty positions, and populated execution rows.
- [x] Run `uv run --locked python -m pytest tests/orchestration -q`.

### Task 4: Extract diagnostics and promotion sections; retain facade

**Files:**
- Create: `packages/orchestration/src/strategy_pipeline/pipeline/output_summary_diagnostic_sections.py`
- Modify: `packages/orchestration/src/strategy_pipeline/pipeline/output_summary_sections.py`
- Modify only if necessary: `packages/orchestration/src/strategy_pipeline/pipeline/__init__.py`

**Interfaces:**
- Produces: `build_run_summary_sections` aggregator and compatibility re-exports.

- [x] Move recency, factor, promotion, and readiness sections into the diagnostics module.
- [x] Keep aggregation order and output schema unchanged.
- [x] Add an import compatibility test for every builder currently imported by tests or sibling modules.
- [x] Run full orchestration tests and compare fixed-output JSON snapshots.

### Task 5: Clear static debt and verify

**Files:**
- Modify only: the new summary modules, compatibility facade, and direct tests.

**Interfaces:**
- Consumes: Tasks 1–4.
- Produces: modular summary code with no target-range Ruff/ty errors.

- [x] Run `uv run --locked ruff check packages/orchestration/src/strategy_pipeline/pipeline tests/orchestration` and fix findings without broad ignores.
- [x] Run `uv run --locked ty check --error-on-warning packages/orchestration/src/strategy_pipeline/pipeline tests/orchestration` and narrow untyped values at their source.
- [x] Remove the orchestration Ruff exclusion only after the complete owning path passes.
- [x] Run the full orchestration test selection from CI and commit file moves separately from typing/style cleanup.
