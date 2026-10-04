# Modeled USD Execution Evidence Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add an opt-in, reusable modeled-execution reference path to the USD replay ledger while keeping verified execution eligibility strict and separate.

**Architecture:** Add a distinct input record for prices modeled from dated daily bars and caller-supplied session timestamps. The USD replay may consume those records only when explicitly opted in, emits them as modeled transactions, and keeps them out of broker order/fill evidence. The existing verified price path remains unchanged by default.

**Tech Stack:** Python 3.12+, dataclasses, Decimal, pandas, pytest, existing `research-contracts` and portfolio-backtester APIs.

**Spec:** `docs/superpowers/specs/2026-10-05-modeled-usd-execution-evidence-design.md`

## Global Constraints

- The platform path is opt-in; existing callers retain current behavior by default.
- Modeled reference prices never set `execution_eligible=True`, never create broker orders/fills, and never satisfy the verified-price selector.
- The platform remains strategy/provider/data agnostic and uses synthetic tests only.
- An assumed FX observation may support a modeled reference transaction only when both assumed-availability and modeled-reference options are explicitly enabled.
- Input and result lineage remains immutable and validated by the existing bundle writer.

## Review Focus

- A modeled observation must never pass the verified execution selector — Task 1 pins selector separation.
- A model record with the wrong instrument, session policy, timestamp or duplicate identity must fail closed — Task 1 tests each invalid identity.
- A modeled transaction with assumed FX must remain diagnostic and reconcile costs/cash — Task 2 tests status, arithmetic and opt-in flags.
- Bundle replay must reject corrupted model provenance or assumptions while preserving old verified bundles — Task 3 covers both branches.
- Missing modeled reference data must not silently fall back to a close or a verified mark from another session — Task 2 tests exact timestamp selection and no fallback.

---

### Task 1: Define and validate modeled execution references

**Files:**
- Modify: `packages/portfolio-backtester/src/portfolio_backtester/usd_ledger_models.py`
- Modify: `packages/portfolio-backtester/src/portfolio_backtester/usd_ledger_inputs.py`
- Modify: `packages/portfolio-backtester/src/portfolio_backtester/__init__.py`
- Test: `tests/test_usd_ledger_inputs.py`

**Interfaces:**
- Add `USDModeledExecutionPrice(instrument_id: str, session_date: date, scheduled_open_at: datetime, reference_price: Decimal, unit: str, source_ref: ArtifactRef, session_policy_id: str, model_id: str)`; this type has no execution-eligible flag and is never treated as a verified mark.
- Add `USDReplayRequest.modeled_execution_prices: tuple[USDModeledExecutionPrice, ...] = ()`.
- Add `USDReplayConfig.allow_modeled_execution_prices: bool = False`.
- Allow `USDFXObservation.availability_basis == "assumed_market_session"` only through the existing assumed-availability opt-in; the default verified path must continue rejecting it for execution.
- Add `select_usd_modeled_execution_price(request: USDReplayRequest, instrument_id: str, at: datetime) -> USDModeledExecutionPrice`.

- [ ] **Step 1: Write failing tests**
  - `test_modeled_execution_price_requires_explicit_opt_in` rejects modeled input with the default config.
  - `test_modeled_execution_price_requires_exact_scheduled_open` rejects a session/time mismatch and duplicate `(instrument_id, scheduled_open_at)` identity.
  - `test_modeled_execution_price_requires_positive_price_and_matching_policy` rejects invalid price, unknown instrument and mismatched `session_policy_id`.
  - `test_verified_execution_selector_never_accepts_modeled_reference` keeps `select_usd_price(..., execution=True)` verified-only.
  - `test_assumed_market_session_fx_requires_assumed_availability_opt_in` rejects assumed FX by default.
- [ ] **Step 2: Run the focused tests and confirm the expected failures**

Run: `uv run --locked --no-default-groups --group test pytest tests/test_usd_ledger_inputs.py -q`

Expected: the new imports/validation tests fail because the modeled record and selector do not exist; existing tests remain green.

- [ ] **Step 3: Implement the record, config/request fields, validation and selector**

Validate aware UTC scheduled opens, positive finite Decimal prices, `currency_per_share`, `ArtifactRef`, instrument identity, matching session policy, unique instrument/time pairs, and explicit config opt-in. `select_usd_modeled_execution_price` requires an exact timestamp match and never uses as-of or fallback selection.

- [ ] **Step 4: Re-run `tests/test_usd_ledger_inputs.py` and confirm all tests pass**

- [ ] **Step 5: Commit Task 1**

```bash
git add packages/portfolio-backtester/src/portfolio_backtester/usd_ledger_models.py packages/portfolio-backtester/src/portfolio_backtester/usd_ledger_inputs.py packages/portfolio-backtester/src/portfolio_backtester/__init__.py tests/test_usd_ledger_inputs.py
git commit -m "feat: add modeled USD execution references"
```

---

### Task 2: Replay modeled references without verified-fill claims

**Files:**
- Modify: `packages/portfolio-backtester/src/portfolio_backtester/usd_ledger.py`
- Modify: `packages/portfolio-backtester/src/portfolio_backtester/usd_ledger_accounting.py`
- Test: `tests/test_usd_ledger_replay.py`
- Test: `tests/test_usd_ledger_accounting.py`

**Interfaces:**
- `run_usd_price_replay(request: USDReplayRequest) -> USDReplayResult` consumes `modeled_execution_prices` only when explicitly enabled.
- Every transaction includes `execution_evidence_kind`, equal to `verified` or `modeled_reference`; modeled transactions additionally carry `modeled_price_session_date` and `modeled_price_model_id`.
- Replay diagnostics record `modeled_execution_enabled`; result summary continues to report `orders_submitted=False`.

- [ ] **Step 1: Write failing replay tests**
  - `test_modeled_reference_replay_uses_exact_open_and_marks_noneligible` uses a daily-close mark plus a separate modeled open reference and asserts the transaction uses only the modeled reference, has `execution_evidence_kind == "modeled_reference"`, and cannot populate verified order/fill output.
  - `test_modeled_reference_applies_signed_slippage_and_separate_costs` checks buy and sell price direction plus one-time commission and FX cost reconciliation.
  - `test_modeled_reference_allows_assumed_fx_only_in_opted_in_mode` checks the modeled path accepts `assumed_market_session` only with both opt-ins while the verified path rejects it.
  - `test_missing_modeled_reference_never_falls_back_to_daily_close` rejects a missing exact open reference even when a close mark exists.
- [ ] **Step 2: Run the focused tests and confirm the expected failures**

Run: `uv run --locked --no-default-groups --group test pytest tests/test_usd_ledger_replay.py tests/test_usd_ledger_accounting.py -q`

Expected: new modeled replay assertions fail; existing verified replay and accounting tests remain green.

- [ ] **Step 3: Implement the explicit modeled execution branch**

At each scheduled execution event, require exactly one permitted evidence path. For modeled events select the exact `USDModeledExecutionPrice`, map only to modeled-reference transaction metadata, apply the existing accounting/cost path once, and preserve assumed FX basis. Do not relax verified selection or silently fall back between evidence classes.

- [ ] **Step 4: Re-run the focused tests and confirm all tests pass**

- [ ] **Step 5: Commit Task 2**

```bash
git add packages/portfolio-backtester/src/portfolio_backtester/usd_ledger.py packages/portfolio-backtester/src/portfolio_backtester/usd_ledger_accounting.py tests/test_usd_ledger_replay.py tests/test_usd_ledger_accounting.py
git commit -m "feat: replay modeled USD execution references"
```

---

### Task 3: Validate and document modeled evidence bundles

**Files:**
- Modify: `packages/portfolio-backtester/src/portfolio_backtester/usd_ledger_bundle.py`
- Modify: `packages/portfolio-backtester/src/portfolio_backtester/usd_ledger.py`
- Modify: `docs/reference/usd-price-ledger.md`
- Test: `tests/test_usd_ledger_bundle.py`

**Interfaces:**
- `write_usd_price_replay_bundle(...)` validates modeled-reference transactions using the modeled record’s source hash, model ID, session date, assumed scheduled timestamp and noneligible status.
- Existing verified bundles keep their current schema meaning; bundle validation does not relabel modeled transactions as broker fills.

- [ ] **Step 1: Write failing bundle tests**
  - `test_bundle_round_trip_preserves_modeled_reference_and_assumptions` writes and reads a synthetic modeled replay and checks lineage, cost columns, `execution_eligible=False`, `orders_submitted=False`, and diagnostic evidence status.
  - `test_bundle_rejects_corrupted_modeled_reference_lineage_or_eligibility` rejects a modified source hash, missing model ID or modeled row marked eligible.
  - `test_verified_bundle_validation_remains_unchanged` preserves the existing verified path.
- [ ] **Step 2: Run `tests/test_usd_ledger_bundle.py` and confirm the new tests fail**

- [ ] **Step 3: Implement branch-aware publisher validation and update the reference guide**

The publisher must replay model metadata from request/result evidence, validate sources against the existing lineage set, and retain all modeled metadata without claiming point-in-time availability.

- [ ] **Step 4: Run the focused bundle tests, then all USD ledger tests**

Run: `uv run --locked --no-default-groups --group test pytest tests/test_usd_ledger_inputs.py tests/test_usd_ledger_accounting.py tests/test_usd_ledger_replay.py tests/test_usd_ledger_bundle.py -q`

Expected: all USD ledger tests pass, including existing verified behavior.

- [ ] **Step 5: Commit Task 3**

```bash
git add packages/portfolio-backtester/src/portfolio_backtester/usd_ledger_bundle.py packages/portfolio-backtester/src/portfolio_backtester/usd_ledger.py docs/reference/usd-price-ledger.md tests/test_usd_ledger_bundle.py
git commit -m "feat: publish modeled USD execution evidence"
```

## Delivery

Run the focused USD ledger tests after each task. Before proposing a PR, run `uv run ruff check` on changed Python files, `uv run ruff format --check` on changed Python files, `uv run ty check`, `uv run pytest`, and `git diff --check` from the task worktree. Do not trigger Actions unless the user separately asks for remote validation; keep all fixtures synthetic. Merge this interface before implementing the `quant-research` consumer, then pin the exact merged platform commit there.
