# Cost and Capacity Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Carry signed shortfall, tails and uncertainty into capacity and research reports.

**Architecture:** Separate new evidence from unchanged v1 calibration. Existing capacity grid gains optional evidence; consumer records its hash and coverage.

**Tech Stack:** pandas/NumPy, seeded date-block bootstrap, pytest.

**Spec:** [Approved design](../specs/2026-10-09-research-assurance-design.md).

## Global Constraints

The [master plan](2026-10-09-research-assurance.md) applies. No automatic promotion/model mutation. Bootstrap defaults to 500 resamples; fewer than two dates means unavailable uncertainty.

## Review Focus

- Zero fill retains opportunity cost (Task 1).
- Favorable execution can have negative signed shortfall (Task 1).
- Small samples/single dates cannot receive ready evidence (Task 2).
- Null groups and unfilled orders remain in coverage (Task 2).
- Missing evidence cannot imply calibrated capacity (Task 3).

### Task 1: Signed order shortfall

**Files:** quant-platform: create packages/portfolio-backtester/src/portfolio_backtester/shortfall.py and tests/test_order_shortfall.py. Leave tca_calibration.py v1 unchanged.

**Interfaces:** Fill(quantity: float, price: float); OrderCost(order_id: str, trade_date: str, side: Literal['buy','sell'], decision_price: float, requested_quantity: float, fills: tuple[Fill,...], fees: float, unfilled_price: float | None, unfilled_at: str | None); order_shortfall(order: OrderCost) -> dict[str, object]. Schema portfolio_backtester.order-shortfall.v1; cash/bps execution, opportunity, fee and total components.

- [ ] Test buy 100@10, fill 60@11, remainder benchmark 12, fees 5: total 145 cash/1450 bps. Test mirrored sell sign, zero fill, favorable execution, NaN, zero decision price, overfill and missing partial-order benchmark/time.
- [ ] Run uv run pytest tests/test_order_shortfall.py -q and confirm missing implementation fails.
- [ ] Compute side-signed deviations and fees over requested decision notional; permit favorable price deviations, reject invalid/nonfinite inputs.
- [ ] Pass new tests and existing TCA/accounting/ledger regressions.
- [ ] Commit: feat: decompose signed order shortfall.

### Task 2: Grouped evidence and uncertainty

**Files:** quant-platform: create packages/portfolio-backtester/src/portfolio_backtester/tca_evidence.py, tests/test_tca_evidence.py and docs/guides/cost-evidence.md.

**Interfaces:** summarize_tca(observations: pd.DataFrame, *, group_cols: Sequence[str], min_observations: int, min_coverage: float, bootstrap_samples: int = 500, seed: int = 0) -> dict[str, object]. Schema portfolio_backtester.tca-evidence.v2. Rows contain order ID/date, requested/filled notional and Task 1 components. Duplicate order IDs fail.

- [ ] Test hand-calculated mean/median/linear empirical P95, requested-notional coverage, whole-date bootstrap and seed repeatability. Null group retained, single date interval unavailable, insufficient sample/coverage has no recommendation, source frame unchanged.
- [ ] Run uv run pytest tests/test_tca_evidence.py -q; require new assertions fail.
- [ ] Implement weighted summaries, explicitly labeled unweighted empirical quantiles, date-block weighted-mean uncertainty and readiness reasons. Validate controls and unique observation identity.
- [ ] Pass new tests, shortfall and existing v1 TCA tests; verify docs example.
- [ ] Commit: feat: report grouped TCA tails and uncertainty.

### Task 3: Capacity and research report consumption

**Files:** quant-platform: modify packages/portfolio-backtester/src/portfolio_backtester/_capacity_report_grid.py, _capacity_report_cli.py and tests/test_capacity_report.py. quant-research: modify scripts/research/experiments/cashflow_indices/replication/run_cashflow_platform_replay.py, pyproject.toml and uv.lock; create tests/strategy_research/test_cost_assurance_report.py.

**Interfaces:** Existing build_capacity_report gains optional cost_evidence: Mapping[str, object] | None = None; capacity CLI and research replay accept --cost-evidence PATH. Research execution metadata records evidence schema/hash/coverage/tails. Existing no-evidence callers remain compatible.

- [ ] Test unchanged legacy report, valid evidence transfer, tampering failure, explicit missing evidence and synthetic scale/participation grid reflecting declared fill/cost truth.
- [ ] Run uv run pytest tests/test_capacity_report.py tests/test_capacity_report_phase5.py -q; confirm new cases fail.
- [ ] Implement provider report/CLI extension, merge provider, then pin platform/contracts in research and implement its report adapter. Use existing hashed artifact transport; no runtime schema change unless its inventory actually cannot carry the new artifact.
- [ ] Pass platform capacity tests and research test_cost_assurance_report.py plus replay regressions; check both CLI helps.
- [ ] Commit separately in each repository: feat: consume cost evidence in capacity research.
