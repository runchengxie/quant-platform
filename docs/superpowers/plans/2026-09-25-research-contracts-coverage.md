# Research Contracts Coverage Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add direct behavioral tests and an enforceable coverage floor for the installed `research_contracts` package, including its time-causality contract.

**Architecture:** Tests live under `tests/contracts/` and import the installed `research_contracts` package. Coverage targets that import name so the report measures code actually executed. Tests use temporary paths and synthetic data only.

**Tech Stack:** Python 3.13, pytest, pytest-cov, uv, `research_contracts`.

**Spec:** `docs/superpowers/specs/2026-09-25-quality-modularization-and-production-design.md`

## Global Constraints

- Keep each change on a task worktree branch from current `origin/main` and submit a PR to `main`.
- Use the locked environment through `uv run --locked`.
- Keep contract schemas and consumer-visible behavior unchanged.
- Use temporary directories and generated fixtures. Do not read research data or credentials.
- Coverage must target `research_contracts` and report the imported package path.
- Set the initial statement coverage threshold to 80% only after the complete direct test set reaches it.

## Review Focus

- Naive datetimes, timezone offsets, and daylight-saving boundaries are rejected or ordered consistently.
- Missing optional execution-window fields are accepted only when execution-aware validation does not require them.
- Tampered file digests and missing files produce deterministic contract errors.
- Atomic writers leave no partial destination after failure.
- Consumer imports through the installed package resolve to the tested source tree.

---

### Task 1: Establish the actual installed-package coverage baseline

**Files:**
- Modify: `scripts/dev/run_tests.sh`
- Test: `tests/test_run_provenance.py`
- Test: `tests/alpha/test_signal_artifact.py`
- Test: `tests/test_positions_artifact.py`
- Test: `tests/alpha/test_style_replica_signal_generator.py`
- Test: `tests/test_backtest_bundle.py`

**Interfaces:**
- Consumes: current local path installation of `research-contracts`.
- Produces: a reproducible coverage command targeting `research_contracts` and a recorded baseline in the PR description.

- [ ] Run the current related tests with `COVERAGE_FILE=/tmp/quant-platform-contracts.coverage uv run --locked python -m pytest --cov=research_contracts --cov-report=term-missing -q tests/test_run_provenance.py tests/alpha/test_signal_artifact.py tests/test_positions_artifact.py tests/alpha/test_style_replica_signal_generator.py tests/test_backtest_bundle.py`.
- [ ] Confirm the report names `.venv/lib/python3.13/site-packages/research_contracts` as the imported source and records the current 24% baseline.
- [ ] Add `--cov=research_contracts` to the `coverage` case in `scripts/dev/run_tests.sh`, preserving the existing `--cov=packages` and `--cov=scripts` targets.
- [ ] Re-run the exact command and confirm the output still reports the installed package, not an unexecuted source tree.
- [ ] Commit the coverage target separately from tests.

### Task 2: Test clock and artifact contracts

**Files:**
- Create: `tests/contracts/test_research_clock.py`
- Create: `tests/contracts/test_artifact_envelope.py`
- Source under test: `packages/research-contracts/research_clock.py`
- Source under test: `packages/research-contracts/artifact_envelope.py`

**Interfaces:**
- Consumes: `ResearchClock`, `validate_research_clock`, artifact envelope public exports.
- Produces: positive and negative behavioral coverage for serialization, schema version, timestamp awareness, timeline ordering, and execution requirements.

- [ ] Write tests for a valid aware-UTC clock, a valid non-UTC clock, naive timestamps, unsupported schema, and each violated ordering relation.
- [ ] Write tests for the optional execution window being omitted, partially provided, ordered incorrectly, and required by `require_execution=True`.
- [ ] Run `uv run --locked python -m pytest tests/contracts/test_research_clock.py -q` and confirm the tests exercise current public behavior.
- [ ] Write envelope round-trip tests and reject wrong schema, missing required fields, and malformed payload types.
- [ ] Run `uv run --locked python -m pytest tests/contracts/test_artifact_envelope.py -q`.

### Task 3: Test file, ownership, manifest, publication, and lineage contracts

**Files:**
- Create: `tests/contracts/test_file_receipts.py`
- Create: `tests/contracts/test_contract_ownership.py`
- Create: `tests/contracts/test_research_run_manifest.py`
- Create: `tests/contracts/test_publication_and_lineage.py`
- Source under test: matching modules in `packages/research-contracts/`

**Interfaces:**
- Consumes: public package exports and consumer-imported submodules.
- Produces: direct checks of hashes, file existence, ownership, manifest validation, publication manifests, and target lineage.

- [ ] Use `tmp_path` to test file receipt creation, digest verification, missing files, and digest mismatch without repository data.
- [ ] Use inline mappings to test ownership and run-manifest valid/invalid cases, including a clock failure propagated through a manifest.
- [ ] Use temporary JSON files to test publication-manifest and lineage valid/invalid cases.
- [ ] Run `uv run --locked python -m pytest tests/contracts/test_file_receipts.py tests/contracts/test_contract_ownership.py tests/contracts/test_research_run_manifest.py tests/contracts/test_publication_and_lineage.py -q`.
- [ ] Add atomic-write failure coverage using a monkeypatched write/replace operation and assert the destination is absent or retains its prior complete contents.

### Task 4: Test consumer-used promotion and A-share readiness checks

**Files:**
- Create: `tests/contracts/test_promotion_evidence.py`
- Create: `tests/contracts/test_a_share_readiness.py`
- Source under test: `packages/research-contracts/promotion_evidence_checks.py`
- Source under test: `packages/research-contracts/a_share_readiness.py`

**Interfaces:**
- Consumes: APIs imported directly by `quant-research` and `quant-intel-platform`.
- Produces: valid and invalid evidence/readiness coverage, with deterministic synthetic payloads.

- [ ] Build minimal valid payload fixtures from the current exported schema and verify promotion checks accept them.
- [ ] Remove or corrupt one required field per check and verify a precise rejection.
- [ ] Cover A-share readiness positive and negative paths using generated evidence only.
- [ ] Run `uv run --locked python -m pytest tests/contracts/test_promotion_evidence.py tests/contracts/test_a_share_readiness.py -q`.

### Task 5: Enforce and verify the coverage floor

**Files:**
- Modify: `scripts/dev/run_tests.sh`
- Test: all files in `tests/contracts/`

**Interfaces:**
- Consumes: Tasks 1–4.
- Produces: a stable `research_contracts` statement-coverage gate of at least 80%.

- [ ] Run `COVERAGE_FILE=/tmp/quant-platform-contracts.coverage uv run --locked python -m pytest --cov=research_contracts --cov-report=term-missing -q tests/contracts` and identify remaining uncovered statements.
- [ ] Add direct tests for uncovered public validators that are used by current consumers; leave unreachable internal compatibility paths out of the threshold rationale only after checking imports across the workspace.
- [ ] Add `--cov-fail-under=80` to the `coverage` case in `scripts/dev/run_tests.sh` after the measured result is at least 80%.
- [ ] Run `uv run --locked python -m pytest tests/contracts -q` and the exact coverage command above.
- [ ] Run `uv run --locked ruff check tests/contracts packages/research-contracts` and `uv run --locked ty check --error-on-warning packages/research-contracts tests/contracts`.
- [ ] Commit the test suite and threshold together.
