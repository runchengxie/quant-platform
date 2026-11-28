# Point-in-time price windows implementation plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Provide a public, vendor-neutral RAW/HFQ/PIT-QFQ price-window converter with explicit information vintages and synthetic acceptance.

**Architecture:** Platform converts prices only; Core continues to own financial accounting. Quotes and factors have independent observation clocks, selected before joining by security/session. A frozen result wrapper carries the converted frame and anchor/source metadata.

**Tech Stack:** Python 3.12/3.13, pandas, NumPy, pytest; no new dependencies.

**Spec:** [Approved cross-repository design](https://github.com/runchengxie/quant-research/blob/744f107d2498b14114fd4246bc9028591a5e596b/docs/superpowers/specs/2026-11-28-price-basis-migration-design.md).

## Global constraints

- Keep financial accounting in Core; do not change existing adjusted asset meanings.
- Use synthetic inputs only. Retain environments, logs and outputs outside source; disposable caches have explicit ownership and closeout.
- RAW needs raw lineage, not adjustment factors. Adjusted bases require factor lineage; unknown historical availability is not certified PIT.
- Provider PR merges precede consumer dependency updates. This plan covers the first provider deliverable; subsequent consumer/account plans remain required.

## Interface decisions

Create `packages/platform/src/quant_platform/prices.py`:

`convert_price_window(prices: pd.DataFrame, *, basis: Literal["raw", "hfq", "pit_qfq"], as_of: str | pd.Timestamp, source_ref: str, factors: pd.DataFrame | None = None, factor_source_ref: str | None = None, price_columns: Sequence[str] = ("open", "high", "low", "close")) -> PriceWindow`.

`PriceWindow` exposes `prices: pd.DataFrame`, `basis: str`, `as_of: pd.Timestamp`, `source_ref: str`, `factor_source_ref: str | None`, `anchors: pd.DataFrame`. Anchors have `symbol`, `trade_date`, `adj_factor`, `available_at`; RAW/HFQ return an empty anchor table with those columns. Frames are independent copies, not immutable pandas objects; `frozen=True` protects wrapper fields only.

Quotes require `symbol`, `trade_date`, `available_at`, requested raw price columns. Factors require `symbol`, `trade_date`, `available_at`, `adj_factor`. Observation clocks and `as_of` must be timezone-aware; normalize to UTC. Trade dates must be timezone-naive midnight dates (ISO dates or date-like objects); market horizon is the Shanghai date of `as_of`. Each source must have a nonempty caller-supplied reference. These declarations require independent source audit; the converter cannot authenticate source timestamps.

Multiple vintages of one security/session are allowed; duplicate `(symbol, trade_date, available_at)` is rejected. Choose latest available vintage per key with both market date and observation time within cutoff. Future rows are ignored. An unavailable historical required factor rejects rather than falling back to a different market date. Empty eligible quotes reject. Extra quote columns survive unchanged. Missing quote prices remain NaN; nonmissing prices must be finite positive numbers. Factor values must be finite positive numbers. Never adjust volume, turnover or raw source factors.

HFQ multiplies by each date's factor. PIT QFQ divides that product by each symbol's latest eligible factor at/before the market horizon, even when its latest quote predates that factor. Current quote equals raw when its own factor is the anchor. Compute PIT ratios before multiplying, reject nonfinite/zero converted nonmissing prices and preserve quote index without mutation. Revisions need real observation vintages; latest reconstructed history with invented old clocks is not certified by this mechanism.

## Review focus

- Separate factor and quote revisions: tests must demonstrate no future revision enters an earlier window.
- Multiple securities and halted last quote: anchors must be per symbol and may be newer than the last quote.
- Missing/invalid values: unknown quotes remain unknown; missing factors never become 1.
- Numeric/date ambiguity: reject naive clocks, numeric dates, duplicate vintages and arithmetic overflow.
- Input ownership: caller frames and extra volume/amount columns must not change.

### Task 1: Converter and synthetic semantics

**Files:** create `packages/platform/src/quant_platform/prices.py`; create `tests/test_price_windows.py`.

**Interfaces:** consumes the quote/factor schemas above; produces `PriceWindow` and `convert_price_window` exactly as above.

- [ ] Write tests importing the new API and hand-checking RAW/HFQ/PIT outputs: raw closes `[100, 50, 60]`, factors `[1, 2, 2]`, HFQ `[100, 100, 120]`, PIT `[50, 50, 60]`; RAW must work with no factors.
- [ ] Add independent two-symbol factors, future append invariance, revised vintages, anchor newer than last quote, NaN marks, nonmutation and unchanged volume tests.
- [ ] Add parameterized rejection tests for missing columns/lineage, naive/invalid clocks and dates, duplicate vintages, invalid factors/prices, missing factor coverage, empty windows and overflow.
- [ ] Run `python -m pytest tests/test_price_windows.py -q`; expected failure: new public module is absent.
- [ ] Implement the converter with separate parsing, vintage selection and arithmetic helpers. Run focused tests until all pass without weakening assertions.
- [ ] Commit the public API and tests.

### Task 2: Documentation and full validation

**Files:** create `docs/price-windows.md`, `docs/price-windows.zh-CN.md`; modify `docs/data/README.md`, `docs/data/README.zh-CN.md`.

**Interfaces:** consumes Task 1's public API; produces linked user documentation explaining supplier scale, clocks, lineage limits and executable example.

- [ ] Document both quote/factor tables, exact units, result wrapper, missing-data behavior and conversion example. Explain why adjusted returns need matched reinvestment assumptions to equal raw-account returns.
- [ ] Run `uv sync --locked --all-groups`, `ruff check .`, `ruff format --check` for changed Python, configured type checks and the full `pytest` suite in the isolated external environment. Record actual failures/skips and source identity; do not report targeted tests as full-suite evidence.
- [ ] Run strict docs build when its environment is available, `git diff --check`, and an independent whole-branch review. Resolve correctness findings with failing regression tests first.
- [ ] Commit documentation and validation record; push the verified destination and create provider PR. Merge only after required checks pass against current main, then clean up only this task's branches/worktree.
