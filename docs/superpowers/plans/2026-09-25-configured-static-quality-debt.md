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

- [x] Run `uv run --locked ruff check --output-format json . > /tmp/quant-platform-ruff-baseline.json` and record the configured non-excluded baseline.
- [x] Run Ruff explicitly over every excluded path from `pyproject.toml` and save JSON to `/tmp/quant-platform-ruff-excluded-baseline.json`.
- [x] Run `uv run --locked ty check --error-on-warning > /tmp/quant-platform-ty-baseline.txt 2>&1` and save the exit status and diagnostic count.
- [x] Use a short Python script over the two JSON/text outputs to group findings by rule and top-level package; do not commit environment-specific absolute paths.
- [x] Update this plan's PR checklist with the exact baseline counts and path groups before source edits.

Baseline from `origin/main` at `f0d1348d03d95b814bd69a6093b0032b04b994ab` (Ruff 0.16.6, ty 0.0.77): configured Ruff reported 0 findings, while excluded paths reported 574. Of those, 455 were RUF001/002/003 findings for the preferred full-width Chinese punctuation `，：；（）｜` or multiplication sign `×`. The remaining findings were 60 C901, 34 I001, 5 RUF022, 7 UP rules, 3 E501, 2 F401, 2 E702, 2 RUF100, and one each of RET504, E902, UP035, and RUF007. The largest ownership groups were microstructure source (401), portfolio-backtester source (50), execution source (24), and alpha source (22), with the rest in orchestration, tests, and one development script.

The initial ty command lacked this repository's multiple source roots and therefore reported 370 false unresolved-import errors. After configuring `tool.ty.environment.extra-paths`, the complete configured source surface reported 401 diagnostics: 396 warnings and five actual type errors. Those five errors were in `corporate_actions.py` (three date comparison/operator errors and two Timestamp narrowing/return errors). Fixing the Timestamp narrowing and comparing normalized dates reduced the current full-surface result to 396 warnings and zero errors. Package-local `portfolio_backtester` plus `research_contracts` currently passes `ty --error-on-warning` with zero diagnostics.

### Task 2: Clear contracts and portfolio-backtester lint debt

**Files:**
- Modify: `packages/research-contracts/**/*.py`
- Modify: `packages/portfolio-backtester/src/portfolio_backtester/**/*.py`
- Modify: corresponding `tests/` files
- Modify: `pyproject.toml`

**Interfaces:**
- Produces: both source scopes pass Ruff, and relevant portfolio types pass blocking `ty`.

- [x] Run Ruff separately on `packages/research-contracts` and the complete portfolio-backtester source and test selections.
- [x] Fix imports, unused names, complexity, long lines, and collection issues with behavior-preserving edits; review every Unicode warning against its surrounding Chinese text.
- [x] Run the matching pytest selections for contracts, optimizer, execution simulation, and portfolio backtester.
- [x] Remove the `packages/research-contracts`, `packages/portfolio-backtester/src/portfolio_backtester`, and `packages/portfolio-backtester/src/research_contracts` exclusions only after their whole source directories pass.
- [x] Run `uv run --locked ty check --error-on-warning packages/portfolio-backtester/src` and fix concrete errors.

The complete `portfolio_backtester` and `research_contracts` sources now pass Ruff and blocking ty. Ruff's remaining source exclusions are limited to orchestration, execution, alpha, and microstructure. CI now runs ty across the full configured source surface and blocks errors; the 396 legacy warnings remain visible while subsequent packages are cleaned.

Current package work has added the ty source roots and allowed legitimate Chinese punctuation in Ruff. Auto-fixable portfolio import/collection findings and the corporate-action date types are corrected. The remaining portfolio Ruff findings are C901 complexity in 21 functions; keep the exclusion until each is decomposed and the entire source passes.

### Task 3: Clear orchestration and execution lint/type debt

**Files:**
- Modify: `packages/orchestration/**/*.py`
- Modify: `packages/execution/**/*.py`
- Modify: `tests/orchestration/**/*.py`
- Modify: `tests/execution/**/*.py`
- Modify: `pyproject.toml`

**Interfaces:**
- Produces: orchestration and execution code/test scopes pass Ruff and blocking `ty`.

- [x] Run Ruff separately on both source and test scopes and review findings by file before editing.
- [x] Fix type narrowing for optional/date/path values at the data boundary, retaining output representation.
- [x] Run `uv run --locked python -m pytest tests/orchestration tests/execution -q`.
- [x] Run `uv run --locked ty check --error-on-warning packages/orchestration/src packages/execution/src`.
- [x] Remove the four corresponding source/test exclusions only after each complete directory passes Ruff.

Execution/orchestration results: Ruff and `ty --error-on-warning` pass for both full source scopes, and the matching tests pass (144 passed). Ruff exclusions and warning-only `ty` scope overrides for these four paths were removed. The public execution package now exports only adapters present in this repository; its former module entrypoint referenced a nonexistent private CLI and was removed. The optional Rich renderer keeps one file-scoped unresolved-import exception because Rich is not a platform dependency and plain-text rendering remains available.

### Task 4: Clear alpha and microstructure lint/type debt

**Files:**
- Modify: `packages/alpha/**/*.py`
- Modify: `packages/microstructure/**/*.py`
- Modify: `tests/microstructure/**/*.py`
- Modify: `pyproject.toml`

**Interfaces:**
- Produces: alpha and microstructure source/test scopes pass Ruff and blocking `ty`.

- [x] Run Ruff separately on alpha source, microstructure source, and microstructure tests; retain JSON reports per scope.
- [x] Fix long functions by extracting cohesive helpers only when behavior and ownership remain clear; keep event ordering and numerical operations unchanged.
- [x] Add or adapt focused tests before any control-flow simplification.
- [x] Run the complete alpha and microstructure pytest selections from CI.
- [x] Run `uv run --locked ty check --error-on-warning packages/alpha/src packages/microstructure/src`.
- [x] Remove the alpha, microstructure, and microstructure-test exclusions only after complete directory scans pass.

Task 4 result: alpha and microstructure sources/tests pass Ruff and strict `ty`. The full relevant test selection passes (443 passed, 12 skipped). The Rust extension wheel includes its new type stub and its required Rust parity test selection passes (71 passed). The missing target-overlay loader was restored with manifest binding, partition, shard-path and partition-size validation, plus direct tests and development-guide documentation.

### Task 5: Clear script and remaining test lint debt

**Files:**
- Modify: `scripts/dev/public_surface_export.py`
- Modify: `tests/orchestration/**/*.py`
- Modify: `tests/execution/**/*.py`
- Modify: `tests/microstructure/**/*.py`
- Modify: `pyproject.toml`

**Interfaces:**
- Produces: every former Ruff-excluded script/test path passes Ruff and configured tests remain valid.

- [x] Run Ruff on the script and each test path not already cleaned by Tasks 2–4.
- [x] Keep script output and generated public-surface data byte-compatible for a fixed checkout.
- [x] Run the direct tests associated with each changed test file.
- [x] Remove the script exclusion only after the complete script file passes Ruff.

### Task 6: Make the complete configured type surface blocking in CI

**Files:**
- Modify: `pyproject.toml`
- Modify: `.github/workflows/ci.yml`
- Modify only files from Tasks 2–5 when full checks reveal remaining source findings.

**Interfaces:**
- Produces: zero unexplained Ruff findings across the repository and a blocking `ty` check over every configured include path.

- [x] Run `uv run --locked ruff check .` and verify no target directories remain excluded.
- [x] Remove the broad `all = "warn"` `ty` override for migrated packages after their complete `ty` findings are fixed.
- [x] Change the CI typecheck command from `.venv/bin/ty check --exit-zero-on-warning` on selected packages to `.venv/bin/ty check --error-on-warning` with no path overrides, so `tool.ty.src.include` controls the full surface.
- [x] Run `uv run --locked ty check --error-on-warning` and verify exit code 0.
- [x] Run `uv run --locked python -m pytest -q`, the repository formatting check, maintainability budget, and `uv run --locked pip-audit`.
- [x] Review the dependency graph and full import tests for new cycles caused by module splits.
- [ ] Commit each ownership group independently and keep the PR diff reviewable.
