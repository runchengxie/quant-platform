import numpy as np
from alpha_research.transform import neutralize_cross_sectional_series
from quant_platform.scenarios import build_scenario, read_scenario, write_scenario
from ticknet.simulator.ordering import ordering_provenance
from ticknet.simulator.pack import SimulatorEvent

from portfolio_backtester import settle_execution_fills


def _fixture(tmp_path, name):
    return read_scenario(write_scenario(build_scenario(name, seed=7), tmp_path / name))


def test_null_signal_truth_is_not_a_random_performance_threshold(tmp_path):
    bundle = _fixture(tmp_path, "null_signal")
    frame = bundle.frames["signals"]
    assert np.cov(frame.prediction, frame["return"])[0, 1] == bundle.truth["covariance"]


def test_industry_only_prediction_has_no_residual_cross_sectional_signal(tmp_path):
    bundle = _fixture(tmp_path, "industry_confound")
    frame = bundle.frames["signals"]
    residual = neutralize_cross_sectional_series(frame, "prediction", ["industry"])
    assert np.var(residual) < 1e-20


def test_partial_fill_truth_reaches_existing_execution_accounting(tmp_path):
    bundle = _fixture(tmp_path, "partial_fill")
    result = settle_execution_fills(
        bundle.frames["fills"],
        bundle.frames["marks"],
        initial_capital=bundle.truth["initial_capital"],
        round_lot=1,
        buy_fee_bps=0.0,
        sell_fee_bps=0.0,
    )
    assert result.iloc[0].buy_shares == bundle.truth["filled_quantity"]
    assert result.iloc[0].cash_end == bundle.truth["cash_end_before_fees"]
    assert result.iloc[0].holdings_value == bundle.truth["market_value_end"]


def test_sequence_gap_remains_in_provenance(tmp_path):
    bundle = _fixture(tmp_path, "sequence_gap")
    events = [SimulatorEvent(**row) for row in bundle.frames["events"].to_dict("records")]
    provenance = ordering_provenance(events)
    assert provenance.get("sequence_gap_count") == len(bundle.truth["missing_sequences"])
    assert provenance.get("sequence_completeness") == "gaps_observed"


def test_sequence_integrity_does_not_invent_cross_channel_sequence():
    events = [
        SimulatorEvent(100, "order", channel="A", sequence=1),
        SimulatorEvent(100, "order", channel="B", sequence=1000),
    ]
    assert ordering_provenance(events).get("sequence_gap_count") == 0
