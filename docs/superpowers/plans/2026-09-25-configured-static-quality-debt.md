# Configured Static Quality Debt Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Remove avoidable Ruff exclusions and make the complete configured `ty` surface pass as an error gate without adding broad warning suppressions.

**Architecture:** First generate a reproducible complete baseline. Then fix and validate one ownership area at a time, preserving package boundaries. Ruff's Unicode diagnostics are reviewed by context so legitimate Chinese copy remains natural. Remove each exclusion only after its entire directory passes the configured rules.

**Tech Stack:** Python 3.13, Ruff, ty, pytest, uv, pip-audit, repository maintainability checks.

**Spec:** `docs/superpowers/specs/2026-09-25-quality-modularization-and-production-design.md`

## Global Constraints

- Use isolated worktrees and separate PRs for independently reviewable package groups.
- Keep `pyproject.toml`'s configured Ruff rule set; do not add broad ignore codes or directory overrides.
- Do not change valid Chinese punctuation to ASCII solely to silence Ruff.
- Fix `Unknown` types at narrow library boundaries with concrete types or small adapters.
- Final Ruff covers all former `extend-exclude` paths and final `ty check --error-on-warning` covers all configured `tool.ty.src.include` paths.

## Review Focus

- Full Ruff and `ty` commands include all configured paths, including scripts.
- Type fixes do not alter runtime branches or silently coerce invalid values.
- Import sorting does not introduce import-time side effects or dependency cycles.
- Line-length edits preserve log messages, schema keys, and command strings.
- Remaining exceptions are local, justified, and documented in the owning module.

---

### Task 1: Produce the exact lint and type baseline

**Files:**
- Review: `pyproject.toml`
- Review: all current `ruff.extend-exclude` and `tool.ty.src.include` paths
- Output: `/tmp/quant-platform-ruff-baseline.txt`
- Output: `/tmp/quant-platform-ty-baseline.txt`

**Interfaces:**
- Consumes: latest `origin/main` and locked tools.
- Produces: exact counts grouped by path and rule, plus reproducible commands.

- [ ] Run `uv run --locked ruff check --output-format json . > /tmp/quant-platform-ruff-baseline.json` and record the configured non-excluded baseline.
- [ ] Run Ruff explicitly over every excluded path from `pyproject.toml` and save JSON to `/tmp/quant-platform-ruff-excluded-baseline.json`.
- [ ] Run `uv run --locked ty check --error-on-warning > /tmp/quant-platform-ty-baseline.txt 2>&1` and save the exit status and diagnostic count.
- [ ] Use a short Python script over the two JSON/text outputs to group findings by rule and top-level package; do not commit environment-specific absolute paths.
- [ ] Update this plan's PR checklist with the exact baseline counts and path groups before source edits.

### Task 2: Clear contracts and portfolio-backtester lint debt

**Files:**
- Modify: `packages/research-contracts/**/*.py`
- Modify: `packages/portfolio-backtester/src/portfolio_backtester/**/*.py`
- Modify: corresponding `tests/` files
- Modify: `pyproject.toml`

**Interfaces:**
- Produces: both source scopes pass Ruff, and relevant portfolio types pass blocking `ty`.

- [ ] Run Ruff separately on `packages/research-contracts` and the complete portfolio-backtester source and test selections.
- [ ] Fix imports, unused names, complexity, long lines, and collection issues with behavior-preserving edits; review every Unicode warning against its surrounding Chinese text.
- [ ] Run the matching pytest selections for contracts, optimizer, execution simulation, and portfolio backtester.
- [ ] Remove the `packages/research-contracts`, `packages/portfolio-backtester/src/portfolio_backtester`, and `packages/portfolio-backtester/src/research_contracts` exclusions only after their whole source directories pass.
- [ ] Run `uv run --locked ty check --error-on-warning packages/portfolio-backtester/src` and fix concrete errors.

### Task 3: Clear orchestration and execution lint/type debt

**Files:**
- Modify: `packages/orchestration/**/*.py`
- Modify: `packages/execution/**/*.py`
- Modify: `tests/orchestration/**/*.py`
- Modify: `tests/execution/**/*.py`
- Modify: `pyproject.toml`

**Interfaces:**
- Produces: orchestration and execution code/test scopes pass Ruff and blocking `ty`.

- [ ] Run Ruff separately on both source and test scopes and review findings by file before editing.
- [ ] Fix type narrowing for optional/date/path values at the data boundary, retaining output representation.
- [ ] Run `uv run --locked python -m pytest tests/orchestration tests/execution -q`.
- [ ] Run `uv run --locked ty check --error-on-warning packages/orchestration/src packages/execution/src`.
- [ ] Remove the four corresponding source/test exclusions only after each complete directory passes Ruff.

### Task 4: Clear alpha and microstructure lint/type debt

**Files:**
- Modify: `packages/alpha/**/*.py`
- Modify: `packages/microstructure/**/*.py`
- Modify: `tests/microstructure/**/*.py`
- Modify: `pyproject.toml`

**Interfaces:**
- Produces: alpha and microstructure source/test scopes pass Ruff and blocking `ty`.

- [ ] Run Ruff separately on alpha source, microstructure source, and microstructure tests; retain JSON reports per scope.
- [ ] Fix long functions by extracting cohesive helpers only when behavior and ownership remain clear; keep event ordering and numerical operations unchanged.
- [ ] Add or adapt focused tests before any control-flow simplification.
- [ ] Run the complete alpha and microstructure pytest selections from CI.
- [ ] Run `uv run --locked ty check --error-on-warning packages/alpha/src packages/microstructure/src`.
- [ ] Remove the alpha, microstructure, and microstructure-test exclusions only after complete directory scans pass.

### Task 5: Clear script and remaining test lint debt

**Files:**
- Modify: `scripts/dev/public_surface_export.py`
- Modify: `tests/orchestration/**/*.py`
- Modify: `tests/execution/**/*.py`
- Modify: `tests/microstructure/**/*.py`
- Modify: `pyproject.toml`

**Interfaces:**
- Produces: every former Ruff-excluded script/test path passes Ruff and configured tests remain valid.

- [ ] Run Ruff on the script and each test path not already cleaned by Tasks 2–4.
- [ ] Keep script output and generated public-surface data byte-compatible for a fixed checkout.
- [ ] Run the direct tests associated with each changed test file.
- [ ] Remove the script exclusion only after the complete script file passes Ruff.

### Task 6: Make the complete configured type surface blocking in CI

**Files:**
- Modify: `pyproject.toml`
- Modify: `.github/workflows/ci.yml`
- Modify only files from Tasks 2–5 when full checks reveal remaining source findings.

**Interfaces:**
- Produces: zero unexplained Ruff findings across the repository and a blocking `ty` check over every configured include path.

- [ ] Run `uv run --locked ruff check .` and verify no target directories remain excluded.
- [ ] Remove the broad `all = "warn"` `ty` override for migrated packages after their complete `ty` findings are fixed.
- [ ] Change the CI typecheck command from `.venv/bin/ty check --exit-zero-on-warning` on selected packages to `.venv/bin/ty check --error-on-warning` with no path overrides, so `tool.ty.src.include` controls the full surface.
- [ ] Run `uv run --locked ty check --error-on-warning` and verify exit code 0.
- [ ] Run `uv run --locked python -m pytest -q`, the repository formatting check, maintainability budget, and `uv run --locked pip-audit`.
- [ ] Review the dependency graph and full import tests for new cycles caused by module splits.
- [ ] Commit each ownership group independently and keep the PR diff reviewable.
