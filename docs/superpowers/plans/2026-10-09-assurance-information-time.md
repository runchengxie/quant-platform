# Information-Time Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make revision selection and consumer label-window behavior explicit and tested.

**Architecture:** Optional public PIT operation preserves current reads. Private research consumes merged provider code; independent model research retains its own splits.

**Tech Stack:** pandas, existing ResearchClock, pytest, pinned dependencies.

**Spec:** [Approved design](../specs/2026-10-09-research-assurance-design.md).

## Global Constraints

The [master plan](2026-10-09-research-assurance.md) applies. Preserve current all-visible-row reads and keep calendar-day embargo distinct from trading-day horizons.

## Review Focus

- Ambiguous identical availability/revision keys fail (Task 1).
- Reordered input selects the same visible revision (Task 1).
- Date-only metadata cannot invent intraday release timestamps (Task 2).
- Later corrections cannot change earlier decisions (Task 2).
- Signal/entry/return-end crossing a split purges the sample (Task 3).

### Task 1: Latest visible revision

**Files:** quant-platform: modify packages/portfolio-backtester/src/portfolio_backtester/point_in_time.py, tests/test_point_in_time_view.py and docs/guides/assurance-scenarios.md.

**Interfaces:** Bound view read_latest(name: str, *, identity_cols: Sequence[str], revision_col: str) -> pd.DataFrame. Filter visibility first; select latest availability then declared comparable revision per identity. Existing read(name) stays unchanged.

- [ ] Test late publication, later correction, permutation invariance, conflicting identical timestamp/revision, null/missing keys, timezone normalization and mutation isolation.
- [ ] Run uv run pytest tests/test_point_in_time_view.py -q; confirm new operation is absent/failing.
- [ ] Implement validated selection. Reject ambiguous ties and incomparable revision values rather than choosing row order.
- [ ] Pass PIT, scenario-consumer and tests/alpha/test_temporal_validation.py regressions.
- [ ] Commit: feat: select latest visible PIT revisions.

### Task 2: Materialization to synthetic backtest

**Files:** quant-research: modify src/style_factors/cashflow_pit_materializer.py, tests/strategy_research/test_cashflow_pit_materializer.py, pyproject.toml and uv.lock; create tests/strategy_research/test_pit_assurance_pipeline.py and docs/research/pit-assurance.md.

**Interfaces:** select_timestamped_pit_revisions(frame: pd.DataFrame, *, clock: Mapping[str, object], identity_cols: Sequence[str], revision_col: str) -> pd.DataFrame, using merged platform operation. Existing materializer accepts optional information clock for explicitly timestamped schemas. Date-only assets keep existing declared date policy.

- [ ] Test source -> materializer -> synthetic public backtest: delayed data excluded, appended later correction leaves earlier decision unchanged, ambiguity rejected, old date-only inputs unchanged. Assert receipt cutoff/revision policy/data revision.
- [ ] Pin merged platform and contracts, lock, then run uv run pytest tests/strategy_research/test_pit_assurance_pipeline.py -q to demonstrate unmet behavior.
- [ ] Add opt-in timestamped materialization and carry revision evidence through the real feature/backtest entry. Do not fabricate a time for date-only assets.
- [ ] Pass test_cashflow_pit_materializer.py, test_pit_assurance_pipeline.py and tests/test_temporal_validation_adapter.py plus affected cashflow regressions.
- [ ] Commit: feat: verify PIT revisions through research consumers.

### Task 3: Independent model horizon tests

**Files:** quant-deep-learning: extend tests/test_horizon_labels.py, test_horizon_evaluation.py and test_eventstream_horizon_labels.py; update owning nextday/eventstream code only on demonstrated failure; document in docs/nextday/cross-sectional-prediction.md.

**Interfaces:** Existing split/horizon/dataset selection; existing evaluation receipt gains missing purge counts if necessary. No platform dependency.

- [ ] Test actual label/dataset paths for cross-boundary return end, timezone/session alignment and valid same-split signal/entry/end; check purge counts and unchanged valid outputs.
- [ ] Run uv run --locked --extra dev pytest tests/test_horizon_labels.py tests/test_horizon_evaluation.py tests/test_eventstream_horizon_labels.py -q; document any assertions already passing rather than claiming a new fix.
- [ ] Fix uncovered boundary/count omissions, preserving locked-test protocol.
- [ ] Pass those tests and research protocol/prediction-audit regressions.
- [ ] Commit: test: verify model horizon boundaries end to end.
