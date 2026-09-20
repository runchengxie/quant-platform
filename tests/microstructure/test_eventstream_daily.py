import numpy as np
import pytest
from ticknet.eventstream.config import ORDER_DTYPE, SNAP_DTYPE, TRADE_DTYPE
from ticknet.eventstream.daily import DAILY_STATE_KEYS, aggregate_day


def make_day_arrays():
    order = np.zeros(2, dtype=ORDER_DTYPE)
    order["time_ms"] = [1000, 3000]
    order["price"] = [1000, 1000]
    order["volume"] = [10, 20]

    trade = np.zeros(3, dtype=TRADE_DTYPE)
    trade["time_ms"] = [1100, 2200, 2500]
    trade["price"] = [1000, 1010, 1000]
    trade["volume"] = [100, 200, 150]
    trade["side"] = [1, -1, 1]

    snap = np.zeros(3, dtype=SNAP_DTYPE)
    snap["time_ms"] = [1200, 2000, 3000]
    snap["last"] = [1000, 1010, 1000]
    snap["d_turnover"] = [1000, 2000, 1000]
    snap["total_bidvol"] = [1000, 1100, 1000]
    snap["total_askvol"] = [900, 1000, 1000]
    snap["bid_px"][:, 0] = [999, 1009, 999]
    snap["ask_px"][:, 0] = [1001, 1011, 1001]

    return order, trade, snap


def test_aggregate_day_reports_core_state():
    order, trade, snap = make_day_arrays()
    state = aggregate_day(order, trade, snap, prev_close_cent=1000.0)

    assert state["order_count"] == 2.0
    assert state["trade_count"] == 3.0
    assert state["snapshot_count"] == 3.0
    assert state["trade_amount"] == 452000.0
    assert state["signed_trade_amount"] == 48000.0
    up = 1010.0 / 1000.0 - 1.0
    down = 1000.0 / 1010.0 - 1.0
    assert state["realized_variance"] == pytest.approx(up**2 + down**2)
    assert state["upside_semivariance"] == pytest.approx(up**2)
    assert state["downside_semivariance"] == pytest.approx(down**2)
    assert set(state) == set(DAILY_STATE_KEYS)
    assert all(np.isfinite(value) for value in state.values())


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
    order, trade, snap = make_day_arrays()
    trade[2]["side"] = 0
    state = aggregate_day(order, trade, snap, prev_close_cent=1000.0)
    assert state["trade_amount"] == 452000.0
    assert state["signed_trade_amount"] == -102000.0


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
