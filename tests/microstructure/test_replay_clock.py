"""Replay batches must not consume events before their processed clock."""

from __future__ import annotations

import importlib
import os

import pytest
from ticknet.simulator.impact import ExecutionSchedule, ImpactEstimator
from ticknet.simulator.matching import MatchingEngine
from ticknet.simulator.replay import InterventionOrder, ReplaySession


@pytest.fixture(params=["python", "rust"])
def session(request):
    if request.param == "rust":
        try:
            importlib.import_module("_microstructure_rs")
        except ImportError:
            if os.environ.get("TICKNET_REQUIRE_RUST") == "1":
                raise
            pytest.skip("optional Rust wheel is not installed")
    return ReplaySession(MatchingEngine(backend=request.param), (100, 50), (101, 50))


def test_background_before_processed_clock_rejects_without_order_effect(session):
    session.add_background(10, 1, 101, 5, "processed")
    session.run()
    ticks = list(session.ticks)
    with pytest.raises(ValueError, match="processed replay time"):
        session.add_background(9, 1, 101, 7, "rejected")
    session.run()
    assert session.ticks == ticks
    assert session.engine.lob.best_ask() == (101, 45)
    assert session.reserve_order_id("rejected") == "rejected"


def test_intervention_before_prefix_rejects_without_order_effect(session):
    with pytest.raises(ValueError, match="processed replay time"):
        session.add_intervention(InterventionOrder(-1, 1, 101, 7, "rejected"))
    session.run()
    assert len(session.ticks) == 1
    assert session.engine.lob.best_ask() == (101, 50)
    assert session.reserve_order_id("rejected") == "rejected"


def test_mutated_queued_time_is_checked_before_any_replay_effect(session):
    session.add_background(10, 1, 101, 5, "processed")
    session.run()
    order = InterventionOrder(12, 1, 101, 7, "mutated")
    session.add_background(11, 1, 101, 3)
    session.add_intervention(order)
    order.time_ms = 9
    ticks = list(session.ticks)
    with pytest.raises(ValueError, match="processed replay time"):
        session.run()
    assert session.ticks == ticks
    assert session.engine.lob.best_ask() == (101, 45)
    # The same pending orders remain recoverable after correcting the caller input.
    order.time_ms = 12
    session.run()
    assert session.engine.lob.best_ask() == (101, 35)
    assert [tick.time_ms for tick in session.ticks] == [0, 10, 11, 12]


def test_same_time_append_and_unsorted_future_batch_preserve_order(session):
    session.add_background(10, 1, 101, 5, "first")
    session.run()
    session.add_background(12, 1, 101, 3, "last")
    session.add_background(10, 1, 101, 2, "same-time")
    session.add_intervention(InterventionOrder(11, 1, 101, 4, "middle"))
    session.run()
    assert [tick.time_ms for tick in session.ticks] == [0, 10, 10, 11, 12]
    assert session.engine.lob.best_ask() == (101, 36)


@pytest.mark.parametrize("time_ms", [float("nan"), float("inf"), 1.5, True])
def test_noninteger_time_rejects_without_order_effect(session, time_ms):
    with pytest.raises(ValueError, match="integer"):
        session.add_background(time_ms, 1, 101, 7, "rejected")
    session.run()
    assert len(session.ticks) == 1
    assert session.engine.lob.best_ask() == (101, 50)


def test_impact_past_schedule_rejects_before_reserving_child_ids():
    replay = ReplaySession(MatchingEngine(), (100, 50), (101, 50))
    replay.add_background(10000, 1, 101, 5)
    replay.run()
    with pytest.raises(ValueError, match="processed replay time"):
        ImpactEstimator(replay).estimate(ExecutionSchedule(1, 10, start_time_ms=1000))
    replay.run()
    assert replay.engine.lob.best_ask() == (101, 45)
    assert replay.reserve_order_id("IMPACT0") == "IMPACT0"


def test_impact_checks_existing_mutated_queue_before_reserving_child_ids():
    replay = ReplaySession(MatchingEngine(), (100, 50), (101, 50))
    replay.add_background(10, 1, 101, 5)
    replay.run()
    order = InterventionOrder(11, 1, 101, 7, "existing")
    replay.add_intervention(order)
    order.time_ms = 9
    with pytest.raises(ValueError, match="processed replay time"):
        ImpactEstimator(replay).estimate(ExecutionSchedule(1, 10, start_time_ms=20))
    assert replay.engine.lob.best_ask() == (101, 45)
    assert replay.reserve_order_id("IMPACT0") == "IMPACT0"
