# Factor Composition Implementation Plan

> **For agentic workers:** Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Deliver reusable static and fitted composition with an auditable private research consumer.

**Architecture:** Public typed contracts and numerical operators in `alpha_research.factor_composition`. Research calls this implementation and retains experiment governance and private artifacts.

**Tech Stack:** Python 3.12/3.13, pandas, NumPy, existing sklearn extra, optional LightGBM.

**Spec:** `docs/superpowers/specs/2026-11-23-factor-composition-design.md`

## Global Constraints

No real data, private parameters or experiment orchestration in Platform. No portfolio execution in composition. Strictly matured labels, explicit missing policy, versioned provenance. Provider merges before consumer dependency pin.

## Review Focus

- Reject duplicate keys, unknown configuration and nonfinite coefficients.
- Preserve missing scores, including constant/empty fitting samples.
- Never include same-time/unmatured labels in fits.
- Compare methods only on a common OOS scored sample.
- Record holdout exposure truthfully, including failed evaluation attempts.

### Task 1: Public contract and static composition

**Files:** `packages/alpha/src/alpha_research/factor_composition*.py`, `tests/alpha/test_factor_composition.py`, package exports.
**Interfaces:** `FactorInput`, `FactorCompositionSpec.from_mapping/to_mapping/fingerprint`, `compose_factors(...) -> FactorCompositionResult`.
- [ ] Write hand-calculated static scores, validation, missing, group and residual tests; observe missing API failure.
- [ ] Implement validated immutable specs, per-date preprocessing and static algorithms.
- [ ] Run focused tests and commit.

### Task 2: Chronological fitted methods

**Files:** `_composition_temporal.py`, `_composition_models.py`, temporal tests.
**Interfaces:** same composer with labels and availability Series; weights and fit-audit frames.
- [ ] Write matured-label, prefix-invariance, warmup and model prediction tests; observe failures.
- [ ] Implement rolling IC/ICIR, covariance shrinkage, turnover cap, historical PCA/Ridge/PLS/optional LightGBM.
- [ ] Run focused and required Platform checks; document API and commit.

### Task 3: Private experiment consumer

**Files:** Research `research_alpha/composition_experiment.py`, CLI, example configuration, tests and docs.
**Interfaces:** `CompositionExperimentSpec`, `run_composition_experiment(...)`, explicit private artifact writer.
- [ ] Write synthetic end-to-end common-sample and registry/holdout tests; observe failure.
- [ ] Integrate diagnostics and governance with no duplicate numerical implementation.
- [ ] Merge provider, pin merged revision and lock dependencies; validate installed provider and consumer together.

### Task 4: Review and delivery

- [ ] Review complete changes in a fresh context; resolve material findings with regression tests.
- [ ] Record actual validation, open and merge provider then consumer PRs under repository controls.
- [ ] Remove only task branches/worktrees, fast-forward clean primary checkouts and report limitations.
