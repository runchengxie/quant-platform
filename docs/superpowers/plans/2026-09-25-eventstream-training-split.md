# Eventstream Training Split Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Decompose `eventstream/train.py` into focused training modules without changing training samples, metrics, checkpoint behavior, deterministic seeds, or current imports.

**Architecture:** Put training configuration, data loading, evaluation, checkpoint handling, training orchestration, and CLI in separate modules. Keep `train.py` as a compatibility facade for symbols imported by the CLI and sibling consumers.

**Tech Stack:** Python, PyTorch, NumPy, pytest, Ruff, ty; Rust parity CI remains unchanged.

**Spec:** `docs/superpowers/specs/2026-09-25-quality-modularization-and-production-design.md`

**实施记录（2026-09-25）：**模块拆分已由 [PR #51](https://github.com/runchengxie/quant-platform/pull/51) 完成，后续严格类型与 Ruff 债务由 PR #55 清理。训练样本顺序、checkpoint 签名、兼容导入和 CLI 均有回归覆盖。

## Global Constraints

- Use a fresh worktree from latest `origin/main` and a focused PR.
- Keep existing imports from `ticknet.eventstream.train` working.
- Preserve date sorting, sample selection, dataset compatibility checks, RNG seeds, checkpoint format/signatures, and training results.
- Do not modify the Rust implementation or parity contract in this split.
- Remove exclusions only after the entire owning scope passes configured Ruff rules.

## Review Focus

- Empty and single-day packed datasets retain their current behavior.
- Checkpoint resume rejects incompatible experiment signatures and restores compatible checkpoints.
- A fixed seed and fixed input produce the same sample order and metric values.
- `DataLoader` and NumPy arrays have concrete types without `Any` leakage.
- Existing sibling imports continue to resolve from `train.py`.

---

### Task 1: Capture API and deterministic behavior

**Files:**
- Test: `tests/microstructure/` eventstream tests identified by `rg -l 'eventstream|EventstreamConfig|list_packed_days' tests/microstructure`
- Source: `packages/microstructure/src/ticknet/eventstream/train.py`

**Interfaces:**
- Consumes: current eventstream public and sibling-used symbols.
- Produces: an explicit compatibility export list and regression assertions for deterministic behavior.

- [x] Run `uv run --locked python -m pytest tests/microstructure -q` and record the relevant eventstream test files.
- [x] Run `rg -n '^class |^def |^    def ' packages/microstructure/src/ticknet/eventstream/train.py` and `rg -n 'from ticknet\.eventstream\.train|import ticknet\.eventstream\.train' packages tests`.
- [x] Add tests for the fixed-seed sample order, checkpoint signature compatibility, and `list_packed_days` ordering if those behaviors lack assertions.
- [x] Run the focused eventstream tests and confirm they pass before moving code.

### Task 2: Extract training configuration and data loading

**Files:**
- Create: `packages/microstructure/src/ticknet/eventstream/training_config.py`
- Create: `packages/microstructure/src/ticknet/eventstream/data_loading.py`
- Modify: `packages/microstructure/src/ticknet/eventstream/train.py`
- Test: the eventstream test files found in Task 1

**Interfaces:**
- Produces: `EventstreamConfig` and data loader helpers at their new owners, with old imports re-exported by `train.py`.

- [x] Move `EventstreamConfig` and validation into `training_config.py` without editing field names, defaults, validation messages, or serialization.
- [x] Move packed-day listing and dataset construction into `data_loading.py` while preserving sorting and filtering.
- [x] Re-export the existing names from `train.py` and add import assertions for sibling call sites.
- [x] Run focused config, input profile, materialized dataset, and eventstream data loader tests.

### Task 3: Extract evaluation and checkpoint handling

**Files:**
- Create: `packages/microstructure/src/ticknet/eventstream/evaluation.py`
- Create: `packages/microstructure/src/ticknet/eventstream/checkpoints.py`
- Modify: `packages/microstructure/src/ticknet/eventstream/train.py`
- Test: eventstream evaluation and checkpoint tests found in Task 1

**Interfaces:**
- Produces: typed evaluation/checkpoint helpers; `train.py` retains current symbols used externally.

- [x] Move metric calculation and evaluation loops into `evaluation.py` without changing metric names or reduction order.
- [x] Move checkpoint read/write, signature validation, and restore helpers into `checkpoints.py` without changing checkpoint payload structure.
- [x] Add tests for compatible restore, incompatible signature, missing checkpoint, and deterministic metric output.
- [x] Run the focused evaluation and checkpoint test files.

### Task 4: Extract training loop and CLI

**Files:**
- Create: `packages/microstructure/src/ticknet/eventstream/training.py`
- Create: `packages/microstructure/src/ticknet/eventstream/cli.py`
- Modify: `packages/microstructure/src/ticknet/eventstream/train.py`
- Modify only if required: `packages/microstructure/src/ticknet/eventstream/__init__.py`

**Interfaces:**
- Produces: a training entrypoint and CLI owner with all prior `train.py` imports preserved.

- [x] Move the training loop to `training.py`, injecting loader/evaluator/checkpoint helpers through direct imports with no new general framework layer.
- [x] Move argument parsing and command entrypoint to `cli.py`, preserving flags, exit codes, and output text.
- [x] Keep `train.py` as re-exports and a thin callable facade.
- [x] Run all `tests/microstructure` tests and the eventstream CLI smoke test from CI.

### Task 5: Type, lint, and parity verification

**Files:**
- Modify only: eventstream modules and directly related tests.

**Interfaces:**
- Consumes: Tasks 1–4.
- Produces: split modules without new ignored typing/lint debt.

- [x] Run `uv run --locked ruff check packages/microstructure/src/ticknet/eventstream tests/microstructure` and fix all reported findings.
- [x] Run `uv run --locked ty check --error-on-warning packages/microstructure/src/ticknet/eventstream tests/microstructure`; use concrete `DataLoader` and NumPy array types at the boundary.
- [x] Remove `packages/microstructure` and `tests/microstructure` from Ruff exclusions only when their full directory checks pass.
- [x] Run the repository Rust parity workflow's local command if available and retain the public CI parity job.
- [x] Commit the moves separately from type/lint-only edits.
