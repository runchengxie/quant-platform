# Daily Microstructure State Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add a public, strategy-agnostic NumPy aggregation API that converts one packed L2 trading day into an interpretable daily microstructure state.

**Architecture:** Add one pure module, `ticknet.eventstream.daily`, with small private helpers for timestamp merging, snapshot returns, and safe statistics. The public `aggregate_day()` consumes the existing packed structured arrays and returns a fixed-key `dict[str, float]`; it does not touch the Transformer, dataset sampling, or on-disk formats.

**Tech Stack:** Python 3.12+, NumPy structured arrays, pytest, existing `ticknet.eventstream.config` dtypes. No new dependencies.

**Spec:** `docs/superpowers/specs/2026-09-20-daily-microstructure-state-design.md`

## Global Constraints

- Keep the public framework strategy-agnostic and do not add private alpha definitions.
- Accept the existing packed `order`, `trade`, and `snap` dtypes without mutation.
- Return the same complete key set for empty and non-empty inputs; missing/non-finite measurements are `0.0`.
- Do not add dependencies or change `L2WindowDataset`, packing formats, or model behavior.
- Keep `ticknet.eventstream` importable without optional Torch installation.

## Review Focus

- Empty or partially empty streams must return the complete schema with finite zeros; covered by Task 1 `test_aggregate_day_empty_streams_returns_complete_finite_schema`.
- Inputs whose stream timestamps are interleaved must use global event ordering for duration, split, final price, and recovery; covered by Task 1 `test_aggregate_day_uses_global_timestamp_order`.
- Unknown trade sides must contribute notional but not signed flow; covered by Task 1 `test_unknown_trade_side_is_not_signed`.
- Zero/negative prices, zero turnover, and zero depth denominators must not create NaN/inf; covered by Task 1 `test_aggregate_day_handles_zero_denominators`.
- Caller-owned arrays must remain unchanged after aggregation; covered by Task 1 `test_aggregate_day_does_not_mutate_inputs`.

### Task 1: Implement daily state aggregation

**Files:**
- Create: `packages/microstructure/src/ticknet/eventstream/daily.py`
- Test: `tests/microstructure/test_eventstream_daily.py`

**Interfaces:**
- Consumes: `ORDER_DTYPE`, `TRADE_DTYPE`, `SNAP_DTYPE` from `ticknet.eventstream.config`.
- Produces: `aggregate_day(order: np.ndarray, trade: np.ndarray, snap: np.ndarray, prev_close_cent: float) -> dict[str, float]` and `DAILY_STATE_KEYS: tuple[str, ...]`.

- [ ] **Step 1: Write the failing test for the public schema and core measures**

```python
def test_aggregate_day_reports_core_state():
    order, trade, snap = make_day_arrays()
    state = aggregate_day(order, trade, snap, prev_close_cent=1000.0)

    assert state["order_count"] == 2.0
    assert state["trade_count"] == 3.0
    assert state["snapshot_count"] == 3.0
    assert state["trade_amount"] == 450.0
    assert state["signed_trade_amount"] == 150.0
    assert state["realized_variance"] == pytest.approx(0.0002)
    assert state["upside_semivariance"] == pytest.approx(0.0001)
    assert state["downside_semivariance"] == pytest.approx(0.0001)
    assert set(state) == set(DAILY_STATE_KEYS)
    assert all(np.isfinite(value) for value in state.values())
```

The fixture must use `ORDER_DTYPE`, `TRADE_DTYPE`, and `SNAP_DTYPE` directly. Use snapshot prices `[1000, 1010, 1000]` cents and trades with positive, negative, and unknown `side` values so the expected values pin down units and side semantics.

- [ ] **Step 2: Run the focused test and verify the expected missing-module failure**

Run: `uv run pytest tests/microstructure/test_eventstream_daily.py::test_aggregate_day_reports_core_state -q`

Expected: FAIL during collection with `ModuleNotFoundError: No module named 'ticknet.eventstream.daily'`.

- [ ] **Step 3: Add the fixed schema and minimal aggregation implementation**

Implement `DAILY_STATE_KEYS` and `aggregate_day()` with these exact keys:

```text
order_count, trade_count, snapshot_count, total_event_count,
event_duration_hours, event_rate_per_hour,
trade_amount, signed_trade_amount, signed_trade_ratio,
realized_variance, upside_semivariance, downside_semivariance,
snapshot_return, snapshot_return_observations,
price_impact_per_turnover, price_impact_observations,
spread_bps_mean, spread_bps_observations,
depth_mean, depth_observations,
l1_imbalance_mean, l1_imbalance_observations,
early_signed_trade_amount, late_signed_trade_amount,
early_snapshot_return, late_snapshot_return,
last_snapshot_to_final_return, recovery_observations
```

Use private helpers `_finite_or_zero`, `_global_timestamps`, `_snapshot_returns`, and `_safe_mean`. Derive snapshot returns from consecutive positive `last` prices sorted by their existing time order; use `prev_close_cent` only for `snapshot_return` when it is finite and positive. Compute spread in bps from `ask_px[0]`/`bid_px[0]`, depth as `total_bidvol + total_askvol`, and L1 imbalance with a zero-denominator guard. Use turnover in cents consistently so `price_impact_per_turnover` is a dimensionless cents-return-per-cent notional proxy. Use median global timestamp as the early/late split and global max timestamp for the final observed price.

- [ ] **Step 4: Run the focused test and verify it passes**

Run: `uv run pytest tests/microstructure/test_eventstream_daily.py::test_aggregate_day_reports_core_state -q`

Expected: PASS.

- [ ] **Step 5: Add edge-case tests before extending the implementation**

```python
def test_aggregate_day_empty_streams_returns_complete_finite_schema():
    state = aggregate_day(
        np.empty(0, dtype=ORDER_DTYPE),
        np.empty(0, dtype=TRADE_DTYPE),
        np.empty(0, dtype=SNAP_DTYPE),
        prev_close_cent=1000.0,
    )
    assert set(state) == set(DAILY_STATE_KEYS)
    assert all(value == 0.0 and np.isfinite(value) for value in state.values())


def test_unknown_trade_side_is_not_signed():
    _order, trade, _snap = make_day_arrays()
    trade[2]["side"] = 0
    state = aggregate_day(_order, trade, _snap, prev_close_cent=1000.0)
    assert state["trade_amount"] == 450.0
    assert state["signed_trade_amount"] == 50.0


def test_aggregate_day_uses_global_timestamp_order():
    order, trade, snap = make_day_arrays()
    order[0]["time_ms"] = 3000
    trade[0]["time_ms"] = 1000
    snap[0]["time_ms"] = 2000
    state = aggregate_day(order, trade, snap, prev_close_cent=1000.0)
    assert state["event_duration_hours"] == pytest.approx(2.0 / 3600.0)


def test_aggregate_day_handles_zero_denominators():
    order, trade, snap = make_day_arrays()
    snap[0]["bid_px"][0] = 0
    snap[0]["ask_px"][0] = 0
    snap[0]["total_bidvol"] = 0
    snap[0]["total_askvol"] = 0
    snap[0]["d_turnover"] = 0
    state = aggregate_day(order, trade, snap, prev_close_cent=0.0)
    assert all(np.isfinite(value) for value in state.values())


def test_aggregate_day_does_not_mutate_inputs():
    order, trade, snap = make_day_arrays()
    before = (order.copy(), trade.copy(), snap.copy())
    aggregate_day(order, trade, snap, prev_close_cent=1000.0)
    assert np.array_equal(order, before[0])
    assert np.array_equal(trade, before[1])
    assert np.array_equal(snap, before[2])
```

Extend the fixture with three snapshots, two orders, and three trades; set the third trade side to unknown only inside the relevant test. Keep tests deterministic and assert behavior rather than helper internals.

- [ ] **Step 6: Run edge-case tests to verify the remaining expected failures**

Run: `uv run pytest tests/microstructure/test_eventstream_daily.py -q`

Expected: the new tests fail only on unimplemented edge-case behavior, not on fixture construction or import errors.

- [ ] **Step 7: Complete the implementation and run the focused file**

Implement the remaining guards and path/recovery calculations, then run:

Run: `uv run pytest tests/microstructure/test_eventstream_daily.py -q`

Expected: all tests in the focused file pass.

- [ ] **Step 8: Commit the vertical slice**

```bash
git add packages/microstructure/src/ticknet/eventstream/daily.py tests/microstructure/test_eventstream_daily.py
git commit -m "feat: add daily microstructure state aggregation"
```

### Task 2: Export the API and document the public contract

**Files:**
- Modify: `packages/microstructure/src/ticknet/eventstream/__init__.py`
- Modify: `packages/microstructure/src/ticknet/eventstream/daily.py` (module docstring only if needed after review)
- Test: `tests/microstructure/test_eventstream.py`

**Interfaces:**
- Consumes: `aggregate_day` and `DAILY_STATE_KEYS` from Task 1.
- Produces: `from ticknet.eventstream import DAILY_STATE_KEYS, aggregate_day`.

- [ ] **Step 1: Write the failing export test**

```python
def test_daily_state_api_is_exported():
    from ticknet.eventstream import DAILY_STATE_KEYS, aggregate_day

    assert callable(aggregate_day)
    assert "trade_amount" in DAILY_STATE_KEYS
```

- [ ] **Step 2: Run the test and verify it fails**

Run: `uv run pytest tests/microstructure/test_eventstream.py::test_daily_state_api_is_exported -q`

Expected: FAIL with `ImportError` because the names are not exported from `ticknet.eventstream`.

- [ ] **Step 3: Add the explicit exports**

Import the two names in `packages/microstructure/src/ticknet/eventstream/__init__.py` and define `__all__` with the existing public names plus `aggregate_day` and `DAILY_STATE_KEYS`. Do not import Torch or change package initialization side effects.

- [ ] **Step 4: Run the export test and the focused daily tests**

Run: `uv run pytest tests/microstructure/test_eventstream.py::test_daily_state_api_is_exported tests/microstructure/test_eventstream_daily.py -q`

Expected: all selected tests pass.

- [ ] **Step 5: Commit the public export**

```bash
git add packages/microstructure/src/ticknet/eventstream/__init__.py tests/microstructure/test_eventstream.py
git commit -m "feat: export daily microstructure state API"
```

### Task 3: Run repository verification and perform final review

**Files:**
- No new production files; inspect Task 1 and Task 2 changes.

**Interfaces:**
- Consumes: the committed daily aggregation API and public export.
- Produces: verified branch with no unrelated changes.

- [ ] **Step 1: Run the complete microstructure suite**

Run: `uv run pytest tests/microstructure -q`

Expected: all microstructure tests pass with zero failures.

- [ ] **Step 2: Run formatting/lint checks for changed Python files**

Run: `uv run ruff check packages/microstructure/src/ticknet/eventstream/daily.py packages/microstructure/src/ticknet/eventstream/__init__.py tests/microstructure/test_eventstream_daily.py tests/microstructure/test_eventstream.py`

Expected: exit 0 with no diagnostics.

- [ ] **Step 3: Run the full repository test suite**

Run: `uv run pytest -q`

Expected: exit 0 with zero failures.

- [ ] **Step 4: Inspect the diff and verify scope**

Run: `git diff --check HEAD~2..HEAD && git status --short && git diff --stat HEAD~2..HEAD`

Expected: no whitespace errors, only the spec, daily aggregator, exports, and their tests are changed; worktree is clean.

- [ ] **Step 5: Commit any documentation-only correction if required, otherwise record final review**

Read the changed files once more against the spec. If no correction is needed, do not create a no-op commit; report the two feature commits and verification results. Do not push or merge without a separate user request.
