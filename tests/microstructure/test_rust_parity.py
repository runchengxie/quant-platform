"""Rust simulation kernel must agree with the public Python reference."""

from __future__ import annotations

import importlib
import os
import random

import pytest

from ticknet.simulator.matching import LimitOrderBook
from ticknet.simulator.replay import InterventionOrder, ReplaySession
from ticknet.simulator.matching import MatchingEngine
from ticknet.simulator.ordering import sort_simulator_events
from ticknet.simulator.pack import SimulatorEvent


def _native():
    try:
        return importlib.import_module("_microstructure_rs")
    except ImportError:
        if os.environ.get("TICKNET_REQUIRE_RUST") == "1":
            raise
        pytest.skip("optional Rust wheel is not installed")


def test_order_book_matches_python_reference_for_seeded_events():
    native = _native()
    for seed in range(20):
        rng = random.Random(seed)
        python_book = LimitOrderBook()
        rust_book = native.OrderBook()
        ids: list[str] = []
        for index in range(300):
            if ids and rng.random() < 0.25:
                order_id = rng.choice(ids)
                quantity = rng.choice([None, 1, 10, 1000])
                assert rust_book.cancel_order(order_id, quantity) == python_book.cancel_order(
                    order_id, quantity
                )
            else:
                order_id = f"{seed}-{index}"
                ids.append(order_id)
                side = rng.choice([-1, 1])
                price = rng.randint(97, 103)
                volume = rng.randint(1, 100)
                actual = rust_book.apply_order(order_id, side, price, volume)
                expected = python_book.apply_order(order_id, side, price, volume)
                assert actual == (
                    None
                    if expected is None
                    else (expected.buy_id, expected.sell_id, expected.price, expected.volume)
                )
            assert rust_book.best_bid() == python_book.best_bid()
            assert rust_book.best_ask() == python_book.best_ask()


def test_batch_replay_matches_python_and_keeps_book_state():
    native = _native()
    python_engine = MatchingEngine()
    session = ReplaySession(python_engine, (100, 50), (101, 40), init_time_ms=7)
    background = [(12, -1, 100, 20, ""), (14, 1, 101, 10, "B"), (14, -1, 99, 5, "S")]
    interventions = [(12, 1, 101, 30, "I"), (15, -1, 100, 10, "J")]
    for row in background:
        session.add_background(*row)
    for row in interventions:
        session.add_intervention(InterventionOrder(*row))
    expected = session.run()

    book = native.OrderBook()
    book.apply_order("INIT_BID", 1, 100, 50)
    book.apply_order("INIT_ASK", -1, 101, 40)
    actual = book.replay(background, interventions)
    assert actual == [
        (tick.time_ms, tick.best_bid, tick.best_ask, tick.source) for tick in expected[1:]
    ]
    assert book.best_bid() == python_engine.lob.best_bid()
    assert book.best_ask() == python_engine.lob.best_ask()


def test_timestamp_ordering_preserves_cross_channel_source_order():
    native = _native()
    rows = [
        (10, "order", "A", 2, 2),
        (10, "snapshot", "", None, 0),
        (10, "cancel", "B", 1, 1),
        (9, "order", "", None, 3),
    ]
    assert native.sort_event_indices(rows) == [3, 2, 0, 1]


def test_public_engine_and_replay_use_rust_backend():
    _native()
    engine = MatchingEngine(backend="rust")
    session = ReplaySession(engine, (100, 50), (101, 40))
    session.add_intervention(InterventionOrder(1, 1, 101, 45, "I"))
    ticks = session.run()
    assert [tick.best_bid for tick in ticks] == [(100, 50), (101, 5)]
    assert engine.lob.best_ask() is None


def test_public_ordering_backend_matches_python():
    _native()
    events = [
        SimulatorEvent(10, "order", order_id="a", channel="A", sequence=3, source_index=0),
        SimulatorEvent(10, "cancel", order_id="b", channel="A", sequence=1, source_index=1),
        SimulatorEvent(10, "snapshot", source_index=2),
        SimulatorEvent(9, "order", order_id="c", source_index=3),
    ]
    assert sort_simulator_events(events, backend="rust") == sort_simulator_events(events)


def test_seed_and_anonymous_reduction_match_python():
    native = _native()
    python_book = LimitOrderBook()
    rust_book = native.OrderBook()
    for book in (python_book, rust_book):
        book.seed_level(1, 100, 20, "a")
        book.seed_level(1, 100, 30, "b")
        assert book.reduce_level(1, 100, 25)
        assert book.best_bid() == (100, 25)
        assert not book.has_order("a")
        assert book.has_order("b")
        assert not book.reduce_level(-1, 100, 3)
        assert book.cancel_order("b", 50) is False
        assert book.best_bid() == (100, 25)


def test_ordering_randomized_differential():
    _native()
    for seed in range(30):
        rng = random.Random(seed)
        events = [
            SimulatorEvent(
                rng.randrange(5),
                rng.choice(["order", "cancel", "trade", "snapshot"]),
                order_id=str(i),
                channel=rng.choice(["", "A", "B"]),
                sequence=rng.choice([None, 1, 2, 3]),
                source_index=i,
            )
            for i in range(100)
        ]
        assert sort_simulator_events(events, backend="rust") == sort_simulator_events(events)


def test_unknown_side_matches_python_reference():
    native = _native()
    python_book = LimitOrderBook()
    rust_book = native.OrderBook()
    for book in (python_book, rust_book):
        book.apply_order("low", 1, 98, 10)
        book.apply_order("high", 1, 101, 10)
    expected = python_book.apply_order("unknown", 0, 100, 5)
    actual = rust_book.apply_order("unknown", 0, 100, 5)
    assert actual == (expected.buy_id, expected.sell_id, expected.price, expected.volume)
    assert rust_book.best_bid() == python_book.best_bid()


def test_replay_generated_ids_follow_sorted_background_position():
    native = _native()
    background = [(20, 1, 99, 1, ""), (10, 1, 100, 1, "")]
    python_engine = MatchingEngine()
    session = ReplaySession(python_engine, (95, 1), (105, 1))
    for row in background:
        session.add_background(*row)
    session.run()

    rust_book = native.OrderBook()
    rust_book.apply_order("INIT_BID", 1, 95, 1)
    rust_book.apply_order("INIT_ASK", -1, 105, 1)
    rust_book.replay(background, [])
    for order_id in ("BG0", "BG1"):
        assert rust_book.cancel_order(order_id) == python_engine.cancel_order(order_id)
        assert rust_book.best_bid() == python_engine.lob.best_bid()
