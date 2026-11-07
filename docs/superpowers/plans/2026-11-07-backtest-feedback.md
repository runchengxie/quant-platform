# Backtest Feedback Implementation Plan

> **For agentic workers:** Use superpowers:executing-plans task by task.

**Goal:** Connect economic account state to subsequent research decisions and
provide inspectable paired execution and impact research mechanisms.

**Architecture:** Extend the existing Platform minute engine. Research consumes
its public API without copying accounting. Engine and Runtime retain ownership.

**Tech Stack:** Python, pandas, pytest, existing locked environments.

**Spec:** ../specs/2026-11-07-backtest-feedback-design.md

## Global Constraints

Synthetic fixtures in Platform; no private strategy or real data in public code.
Use isolated task worktrees and PRs. Preserve default replay behavior.

## Review Focus

- Decision clocks earlier than entry cannot see intermediate observations.
- Callbacks must not mutate simulator state through snapshots.
- Missing marks and failed scenarios must remain visible.
- Restored impact must reject backwards clocks and incompatible parameters.
- Duplicate scenarios and mismatched return dates must fail comparisons.

### Task 1: Causal account feedback

Files: `_portfolio/minute_execution.py`, `tests/test_minute_execution_feedback.py`.
Interface: `decision_policy(state, proposed_weights) -> Mapping[str,float] | None`.
- [x] Write partial-fill, preserve-pending, immutable-state and causal-prefix tests.
- [x] Watch tests fail, implement decision-clock scheduling and frozen weights.
- [x] Run minute execution regression tests and commit.

### Task 2: Cost coverage and persistent impact

Files: `_portfolio/_execution_models.py`, `backtest/impact.py`, focused tests.
Interfaces: explicit coverage policy; `LinearImpact.execute(symbol,time,quantity)`
returns average price offset; checkpoint/restore maintain all symbol states.
- [x] Write missing-liquidity, out-of-range, round-trip, splitting and restore tests.
- [x] Watch tests fail, implement and run regression tests.
- [x] Document uncalibrated units and cost accounting; commit.

### Task 3: Paired historical execution research

Files in Research: `src/strategy_research/paired_execution_paths.py`, direct tests,
and linked research documentation.
Interface: run fixed targets and feedback callback over identical historical bars,
independent scenarios; preserve every failure and compute paired daily returns.
- [ ] Write independent-account, scenario-failure and paired-return tests.
- [ ] Watch tests fail; implement reusable runner and historical artifact CLI.
- [ ] Record provenance, limitations and all scenarios; run related research tests.

### Task 4: Delivery

- [ ] Run required Platform checks and relevant Research regression/static checks.
- [ ] Review full changes; correct material findings and rerun affected checks.
- [ ] Verify push destinations, commit, push, create PRs, merge provider first.
- [ ] Validate consumer against merged provider; clean only task resources.

## Execution ledger

Task worktrees start at Platform f16bcf8 and Research dad051156.
Ruling: use native inline execution under the user's request to progress all work;
no additional design confirmation is needed for the scope already presented.
Environment setup initially failed because default uv cache is read-only; use a
separate temporary cache without modifying shared configuration.

Ruling after review: process effective account/day events before delivering state,
while keeping same-clock market bars excluded. Historical source decisions are
close plus one nanosecond, and risk observations use close availability, resolving
the original inconsistent clock. Strict cost coverage is the default; legacy
fallback requires explicit opt-in. Validation helpers move to _minute_validation.py
to preserve the existing file-size maintainability gate without changing its budget.
