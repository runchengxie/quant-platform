# Signal reliability implementation plan

> **For agentic workers:** Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox syntax for tracking.

**Goal:** Ship tail, marginal and conditional evidence with a research consumer.
**Architecture:** Independent public alpha API; private research CLI consumes its merged revision.
**Tech Stack:** NumPy, Pandas, pytest, uv.
**Spec:** ../specs/2026-11-21-signal-reliability-design.md

## Global constraints

Preserve existing APIs. No real data or strategy parameters in public source.
Rank before inspecting labels. Pointwise time-block intervals are descriptive.
Retain incomplete dates and missing labels. Merge provider before consumer.

## Review focus

- Ambiguous identities and normalized duplicate keys must reject input.
- Missing labels must never alter ranked selections.
- Rank and linear designs can have different identifiability.
- Paired predictions must share a declared research identity.
- Output paths must not permit writes into any source worktree.

### Task 1: Tail and marginal profiles

Files: `packages/alpha/src/alpha_research/signal_reliability.py`,
`_signal_reliability_common.py`, `_signal_reliability_tail.py`,
`tests/alpha/test_signal_reliability.py`.
Interfaces: `SignalReliabilityResult(summary, by_date, profile)`;
`tail_return_profile(panel, *, score_col, target_col, ks, statistics, ...)` and
`marginal_alpha_profile` with the same input conventions.

- [ ] Write failing tests for monotone/reversed/saturated returns, tie ordering,
  incomplete bands, duplicate keys, missing labels and deterministic intervals.
- [ ] Run focused pytest; expect missing module failure.
- [ ] Implement validation, normalized fingerprints, time-block statistics,
  per-date bands and paired spreads; expose public functions.
- [ ] Run focused tests, expect all pass; commit.

### Task 2: Conditional and incremental evidence

Files: `_signal_reliability_conditional.py`,
`tests/alpha/test_signal_reliability_conditional.py`; extend public exports.
Interface: `conditional_factor_profile(panel, *, factor_cols, target_col,
control_cols, industry_col, baseline_col, augmented_col, paired_provenance,
ks, statistics, ...) -> SignalReliabilityResult`.

- [ ] Write failing tests for confounded sign reversal, independent noise,
  industry/missing controls, unidentified designs, paired matching and absent
  or incompatible incremental evidence.
- [ ] Run new tests, expect missing conditional API failure.
- [ ] Implement complete-case raw/partial-rank/OLS evidence and paired model
  IC/Top K evidence with explicit status and conditioning diagnostics.
- [ ] Run full alpha regression tests and focused checks; commit.

### Task 3: Public documentation and provider delivery

Files: `docs/alpha/signal-reliability.md`, Chinese companion, documentation index.

- [ ] Document exact schema, units, settings, warnings and example with synthetic data.
- [ ] Run locked sync, Ruff, full pytest, whitespace and independent branch review.
- [ ] Fix review findings and validate current main integration, commit, push PR,
  wait for required checks, merge and record provider SHA.

### Task 4: Research consumer

Files in quant-research: `src/strategy_app/research/signal_reliability.py`
(or nearest established package), tests, bilingual usage docs, pyproject/uv lock.
Interface: config JSON + input Parquet + provenance JSON -> versioned report
files under explicit configured project data root.

- [ ] Create isolated research worktree from current main.
- [ ] Write failing integration tests for public API calls, provenance and
  strict JSON serialization, invalid config/output paths and no overwrite.
- [ ] Implement CLI, pin merged provider and regenerate locked dependencies.
- [ ] Run affected tests/static/documentation checks and record revisions.
- [ ] Inventory historical inputs read-only; run compatible inputs or record
  missing fields and reproduction command without overstating evidence.
- [ ] Independently review, validate against current main, commit/push/merge.
- [ ] Verify merge state, clean only task resources and fast-forward clean primaries.
