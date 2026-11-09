"""Legacy deterministic routes retain Engine identity and lazy learned exports."""

import importlib
import subprocess
import sys

import pytest


@pytest.mark.parametrize(
    "name", ["matching", "pack", "ordering", "replay", "correctness", "impact"]
)
def test_deterministic_modules_and_classes_are_exact_provider_aliases(name):
    old = importlib.import_module(f"ticknet.simulator.{name}")
    core = importlib.import_module(f"quant_backtest_core.microstructure.{name}")
    assert old is core
    for symbol, value in vars(core).items():
        if isinstance(value, type) or callable(value):
            assert getattr(old, symbol) is value


def test_impact_root_exports_and_old_schedule_estimate():
    import ticknet
    from quant_backtest_core.microstructure import impact
    from ticknet import simulator
    from ticknet.simulator.matching import MatchingEngine
    from ticknet.simulator.replay import ReplaySession

    for name in ("ExecutionSchedule", "ImpactResult", "ImpactEstimator"):
        assert getattr(ticknet, name) is getattr(impact, name)
        assert getattr(simulator, name) is getattr(impact, name)
    session = ReplaySession(MatchingEngine(), (1000, 500), (1001, 30))
    result = ticknet.ImpactEstimator(session).estimate(ticknet.ExecutionSchedule(1, 100, n_child=3))
    assert type(result) is impact.ImpactResult
    assert result.filled_volume == 30 and result.unfilled_volume == 70
    assert result.execution_vwap == 1001
    with pytest.raises(AttributeError):
        _ = ticknet.unknown_export
    with pytest.raises(AttributeError):
        _ = simulator.unknown_export


def test_deterministic_imports_do_not_load_training():
    code = """
import sys
import ticknet
import ticknet.simulator.matching
import ticknet.simulator.replay
import ticknet.simulator.impact
assert ticknet.ExecutionSchedule
for name in ('torch', 'ticknet.dataset', 'ticknet.model',
             'ticknet.simulator.generator', 'ticknet.simulator.sqrt_law'):
    assert name not in sys.modules, name
"""
    subprocess.run([sys.executable, "-I", "-c", code], check=True)


def test_retained_training_and_generator_consumers_use_aliases():
    import ticknet
    from quant_backtest_core.microstructure import impact, replay
    from ticknet import dataset, model
    from ticknet.simulator import generator, sqrt_law
    from ticknet.train import f1_metrics

    for name in ("NUM_CLASSES", "NUM_FEATURES", "WINDOW_SIZE", "get_dummy_batch"):
        assert getattr(ticknet, name) is getattr(dataset, name)
    for name in ("DeepLOB", "build_model"):
        assert getattr(ticknet, name) is getattr(model, name)
    assert generator.BackgroundOrder is replay.BackgroundOrder
    assert sqrt_law.ExecutionSchedule is impact.ExecutionSchedule
    assert sqrt_law.ImpactEstimator is impact.ImpactEstimator
    assert callable(f1_metrics)


@pytest.mark.parametrize("mutated_queue", [False, True])
def test_legacy_impact_rejects_stale_admission_before_reserving_ids(mutated_queue):
    from ticknet.simulator.impact import ExecutionSchedule, ImpactEstimator
    from ticknet.simulator.matching import MatchingEngine
    from ticknet.simulator.replay import InterventionOrder, ReplaySession

    session = ReplaySession(MatchingEngine(), (100, 50), (101, 50))
    session.add_background(10, 1, 101, 5)
    session.run()
    start = 1
    if mutated_queue:
        queued = InterventionOrder(11, 1, 101, 7, "existing")
        session.add_intervention(queued)
        queued.time_ms = 9
        start = 20
    with pytest.raises(ValueError, match="processed replay time"):
        ImpactEstimator(session).estimate(ExecutionSchedule(1, 10, start_time_ms=start))
    assert session.engine.lob.best_ask() == (101, 45)
    assert session.reserve_order_id("IMPACT0") == "IMPACT0"


@pytest.mark.parametrize(
    "side,bid,ask,volume,raw_slippage",
    [
        (1, (100, 0), (101, 0), 0, 0.0),
        (1, (100, 0), (101, 5), 5, -10000.0),
        (-1, (100, 5), (101, 0), 5, 10000.0),
    ],
)
def test_legacy_empty_book_sentinels_remain_distinct_from_execution_evidence(
    side, bid, ask, volume, raw_slippage
):
    from ticknet.simulator.impact import ExecutionSchedule, ImpactEstimator
    from ticknet.simulator.matching import MatchingEngine
    from ticknet.simulator.replay import ReplaySession

    result = ImpactEstimator(ReplaySession(MatchingEngine(), bid, ask)).estimate(
        ExecutionSchedule(side, volume)
    )
    assert result.mid_after == 0.0
    assert result.slippage_bps == raw_slippage  # Legacy midpoint sentinel, not calibrated impact.
    assert result.filled_volume == volume
    if volume:
        assert result.execution_vwap == result.mid_before
        assert result.execution_slippage_bps == 0.0
    else:
        assert result.execution_vwap is result.execution_slippage_bps is None
