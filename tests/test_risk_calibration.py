"""Hand-derived, synthetic matched-horizon risk audit acceptance."""

from importlib import import_module, util

import numpy as np
import pandas as pd
import pytest

MODULE = "quant_platform.analytics.risk_calibration"
AS_OF = pd.Timestamp("2026-03-01", tz="UTC")


def audit(forecasts, outcomes, **kwargs):
    assert util.find_spec(MODULE) is not None, "matched-horizon risk audit API is missing"
    return import_module(MODULE).audit_risk_calibration(forecasts, outcomes, as_of=AS_OF, **kwargs)


@pytest.fixture
def sample():
    forecasts, outcomes = [], []
    for i, (variance, realized) in enumerate(
        zip([1.0, 1.0, 4.0, 4.0], [1, -3, 2, -6], strict=True)
    ):
        start = pd.Timestamp("2026-01-01", tz="UTC") + pd.Timedelta(days=i)
        common = {
            "symbol": "A",
            "target_start": start,
            "target_end": start + pd.Timedelta(days=1),
            "unit": "return_bps",
        }
        forecasts.append(
            common
            | {
                "forecast_at": start,
                "available_at": start,
                "forecast_mean": 0.0,
                "forecast_variance": variance,
                "liquidity": "liquid",
                "regime": "low" if i < 2 else "high",
            }
        )
        outcomes.append(
            common
            | {
                "realized": float(realized),
                "available_at": common["target_end"],
                "observation_start": start,
                "observation_end": common["target_end"],
            }
        )
    return pd.DataFrame(forecasts), pd.DataFrame(outcomes)


def test_known_heteroskedastic_variance_residuals_tails_and_shared_denominators(sample):
    f, o = sample
    report = audit(f, o)
    s = report.summary.iloc[0]
    # (1 + 9 + 4 + 36)/4 = 12.5; (1+1+4+4)/4 = 2.5.
    assert (s.forecasts, s.paired_observations, s.coverage) == (4, 4, 1)
    assert s.predicted_variance == 2.5
    assert s.realized_squared_residual == 12.5
    assert s.variance_ratio == 5
    assert (s.tail_observations, s.two_sigma_exceedances, s.two_sigma_rate) == (4, 2, 0.5)
    assert report.rows.squared_residual.tolist() == [1, 9, 4, 36]
    assert report.sample_status == "insufficient_target_intervals"
    assert report.real_calibration == "unavailable"
    assert report.independence_status == "unverified"
    assert report.certified is False
    assert report.prediction_intervals is None


def test_constant_variance_with_nonzero_mean_uses_zero_residual_not_squared_return(sample):
    f, o = sample
    f["forecast_variance"] = 4.0
    f["forecast_mean"] = [2.0, -2.0, 5.0, -5.0]
    o["realized"] = f.forecast_mean
    s = audit(f, o).summary.iloc[0]
    assert s.predicted_variance == 4
    assert s.realized_squared_residual == 0
    assert s.variance_ratio == 0
    assert s.two_sigma_exceedances == 0


def test_missing_illiquid_rows_and_regimes_remain_visible(sample):
    f, o = sample
    f.loc[2:, "liquidity"] = "illiquid"
    o = o.iloc[:2]
    report = audit(f, o)
    assert len(report.rows) == 4
    assert report.rows.paired.tolist() == [True, True, False, False]
    assert report.rows.iloc[2].issues == ("missing_outcome",)
    liquid = report.cohorts.query("liquidity == 'liquid'").iloc[0]
    missing = report.cohorts.query("liquidity == 'illiquid'").iloc[0]
    assert (liquid.forecasts, liquid.paired_observations, liquid.coverage) == (2, 2, 1)
    assert (missing.forecasts, missing.paired_observations, missing.coverage) == (2, 0, 0)
    assert pd.isna(missing.realized_squared_residual)
    assert pd.isna(missing.predicted_variance)
    assert pd.isna(missing.two_sigma_rate)


def test_paired_predictions_do_not_include_missing_high_variance_forecasts(sample):
    f, o = sample
    f.loc[2:, "forecast_variance"] = 10000.0
    s = audit(f, o.iloc[:2]).summary.iloc[0]
    assert s.predicted_variance == 1
    assert s.realized_squared_residual == 5
    assert s.variance_ratio == 5


@pytest.mark.parametrize(
    "change,issue",
    [
        ("late", "outcome_unavailable"),
        ("stale", "stale_outcome"),
        ("future_target", "target_incomplete"),
        ("unit", "incompatible_outcome"),
        ("horizon", "incompatible_outcome"),
        ("missing_return", "missing_realized"),
        ("missing_risk", "missing_forecast_risk"),
        ("missing_mean", "missing_forecast_mean"),
        ("late_forecast", "forecast_unavailable_at_decision"),
    ],
)
def test_unsupported_evidence_is_retained_with_reasons(sample, change, issue):
    f, o = sample
    if change == "late":
        o.loc[0, "available_at"] = AS_OF + pd.Timedelta(days=1)
    elif change == "stale":
        o.loc[0, "observation_end"] -= pd.Timedelta(hours=1)
    elif change == "future_target":
        f.loc[0, "target_end"] = AS_OF + pd.Timedelta(days=1)
        o.loc[0, ["target_end", "observation_end", "available_at"]] = AS_OF + pd.Timedelta(days=1)
    elif change == "unit":
        o.loc[0, "unit"] = "return_fraction"
    elif change == "horizon":
        o.loc[0, "target_end"] += pd.Timedelta(hours=1)
        o.loc[0, ["observation_end", "available_at"]] = o.loc[0, "target_end"]
    elif change == "missing_return":
        o.loc[0, "realized"] = np.nan
    elif change == "missing_risk":
        f.loc[0, "forecast_variance"] = np.nan
    elif change == "missing_mean":
        f.loc[0, "forecast_mean"] = np.nan
    elif change == "late_forecast":
        f.loc[0, "available_at"] += pd.Timedelta(seconds=1)
    report = audit(f, o)
    assert len(report.rows) == 4
    assert issue in report.rows.iloc[0].issues
    assert not report.rows.iloc[0].paired
    assert pd.isna(report.rows.iloc[0].squared_residual)
    assert len(report.outcomes) == 4


def test_same_target_from_multiple_decisions_not_duplicated_as_independent(sample):
    f, o = sample
    duplicate_decision = f.iloc[:1].copy()
    duplicate_decision["forecast_at"] -= pd.Timedelta(hours=1)
    duplicate_decision["available_at"] = duplicate_decision.forecast_at
    report = audit(pd.concat([f, duplicate_decision]), o, minimum_observations=4)
    assert report.summary.iloc[0].paired_observations == 5
    assert report.summary.iloc[0].distinct_target_intervals == 4
    assert report.summary.iloc[0].nonoverlapping_target_intervals == 4
    assert report.sample_status == "descriptive_only_independence_unverified"


def test_many_correlated_assets_in_two_dates_cannot_meet_twenty_observations(sample):
    f, o = sample
    forecasts, outcomes = [], []
    for i in range(30):
        forecasts.append(f.iloc[:2].assign(symbol=f"S{i}"))
        outcomes.append(o.iloc[:2].assign(symbol=f"S{i}"))
    report = audit(pd.concat(forecasts), pd.concat(outcomes))
    s = report.summary.iloc[0]
    assert (
        s.paired_observations,
        s.distinct_target_intervals,
        s.nonoverlapping_target_intervals,
    ) == (60, 2, 2)
    assert report.sample_status == "insufficient_target_intervals"
    assert report.effective_independent_observations is None


def test_overlapping_horizons_use_interval_count_and_no_independence_claim(sample):
    f, o = sample
    f["target_end"] += pd.Timedelta(days=1)
    for col in ["target_end", "observation_end", "available_at"]:
        o[col] += pd.Timedelta(days=1)
    report = audit(f, o, minimum_observations=3)
    s = report.summary.iloc[0]
    assert (s.distinct_target_intervals, s.nonoverlapping_target_intervals) == (4, 2)
    assert report.sample_status == "insufficient_nonoverlapping_intervals"
    assert report.independence_status == "unverified"


def test_zero_denominators_remain_unknown_and_zero_risk_breaches_visible(sample):
    f, o = sample
    f["forecast_variance"] = 0.0
    o["realized"] = [0, 1, 0, 2]
    s = audit(f, o).summary.iloc[0]
    assert pd.isna(s.variance_ratio)
    assert pd.isna(s.two_sigma_rate)
    assert pd.isna(s.two_sigma_exceedances)
    assert s.tail_observations == 0
    assert s.zero_variance_nonzero_residuals == 2


def test_empty_inputs_have_unknown_coverage_and_no_healthy_zero(sample):
    f, o = sample
    report = audit(f.iloc[:0], o.iloc[:0])
    assert len(report.rows) == 0
    s = report.summary.iloc[0]
    for column in [
        "coverage",
        "predicted_variance",
        "realized_squared_residual",
        "variance_ratio",
        "two_sigma_rate",
        "two_sigma_exceedances",
    ]:
        assert pd.isna(s[column])
    assert report.sample_status == "insufficient_target_intervals"


def test_volatility_is_squared_once_and_units_are_never_converted(sample):
    f, o = sample
    f = f.drop(columns="forecast_variance")
    f["forecast_volatility"] = [1, 1, 2, 2]
    f["unit"] = o["unit"] = "price_change:CNY"
    s = audit(f, o).summary.iloc[0]
    assert s.unit == "price_change:CNY"
    assert s.predicted_variance == 2.5


def test_different_horizons_and_units_have_separate_comparable_summaries(sample):
    f, o = sample
    f.loc[2:, "unit"] = o.loc[2:, "unit"] = "factor:synthetic_index_point"
    report = audit(f, o)
    assert len(report.summary) == 2
    assert sorted(report.summary.predicted_variance) == [1, 4]
    f.loc[1, "target_end"] += pd.Timedelta(hours=1)
    for col in ["target_end", "observation_end", "available_at"]:
        o.loc[1, col] += pd.Timedelta(hours=1)
    assert len(audit(f, o).summary) == 3


@pytest.mark.parametrize("side", ["forecast", "outcome"])
def test_duplicate_economic_keys_are_rejected(sample, side):
    f, o = sample
    if side == "forecast":
        f = pd.concat([f, f.iloc[:1]])
    else:
        o = pd.concat([o, o.iloc[:1]])
    with pytest.raises(ValueError, match="duplicate"):
        audit(f, o)


@pytest.mark.parametrize(
    "change,match",
    [
        ("naive", "aware"),
        ("negative", "nonnegative"),
        ("infinite", "finite"),
        ("two_risks", "one risk"),
        ("unit", "unit"),
        ("interval", "interval"),
        ("outcome_availability", "availability"),
        ("missing_schema", "columns"),
    ],
)
def test_invalid_contract_rejected(sample, change, match):
    f, o = sample
    if change == "naive":
        f["forecast_at"] = f.forecast_at.dt.tz_localize(None)
    elif change == "negative":
        f.loc[0, "forecast_variance"] = -1
    elif change == "infinite":
        o.loc[0, "realized"] = np.inf
    elif change == "two_risks":
        f["forecast_volatility"] = 1.0
    elif change == "unit":
        f.loc[0, "unit"] = "annualized"
    elif change == "interval":
        f.loc[0, "target_end"] = f.loc[0, "target_start"]
    elif change == "outcome_availability":
        o.loc[0, "available_at"] = o.loc[0, "target_start"]
    elif change == "missing_schema":
        f = f.drop(columns="forecast_mean")
    with pytest.raises(ValueError, match=match):
        audit(f, o)


@pytest.mark.parametrize("minimum", [True, 0, -1, 1.5])
def test_minimum_requires_positive_integer(sample, minimum):
    with pytest.raises(ValueError, match="minimum"):
        audit(*sample, minimum_observations=minimum)


def test_covariance_rank_requires_auditable_matrix_and_preserves_raw_rank(sample):
    f, o = sample
    f["raw_covariance"] = pd.Series([[[1, 1], [1, 1]]] * 4, dtype=object)
    f["shrunk_covariance"] = pd.Series([[[1, 0.5], [0.5, 1]]] * 4, dtype=object)
    f["covariance_labels"] = [("F1", "F2")] * 4
    f["covariance_unit"] = "return_bps^2"
    f["covariance_available_at"] = f.forecast_at
    f["covariance_source"] = "synthetic-matrix-v1"
    report = audit(f, o)
    assert report.rank_diagnostics.raw_rank.tolist() == [1] * 4
    assert report.rank_diagnostics.shrunk_rank.tolist() == [2] * 4
    assert report.rank_diagnostics.dimension.tolist() == [2] * 4
    assert report.rank_diagnostics.status.tolist() == ["raw_rank_deficient"] * 4
    assert report.certified is False
    assert report.rows.iloc[0].raw_covariance == [[1, 1], [1, 1]]


def test_rank_claim_without_matrix_evidence_is_unavailable(sample):
    f, o = sample
    f["raw_rank"] = 2
    f["shrunk_rank"] = 2
    r = audit(f, o)
    assert r.rank_diagnostics.status.tolist() == ["unavailable"] * 4
    assert r.rank_diagnostics.raw_rank.isna().all()


def test_future_covariance_evidence_cannot_support_rank(sample):
    f, o = sample
    f["raw_covariance"] = pd.Series([[[1]]] * 4, dtype=object)
    f["covariance_labels"] = [("F1",)] * 4
    f["covariance_unit"] = "return_bps^2"
    f["covariance_available_at"] = AS_OF + pd.Timedelta(days=1)
    f["covariance_source"] = "synthetic"
    assert audit(f, o).rank_diagnostics.status.tolist() == ["unavailable_at_decision"] * 4


def test_inputs_unchanged_duplicate_indices_and_unmatched_outcomes_visible(sample):
    f, o = sample
    f.index = [3, 3, 1, 0]
    extra = o.iloc[:1].assign(symbol="UNKNOWN")
    o = pd.concat([o, extra])
    before_f, before_o = f.copy(deep=True), o.copy(deep=True)
    report = audit(f, o)
    assert len(report.outcomes) == 5
    assert report.outcomes.iloc[-1].match_status == "unmatched"
    pd.testing.assert_frame_equal(f, before_f)
    pd.testing.assert_frame_equal(o, before_o)


def test_extra_input_column_names_survive_namedtuple_renaming(sample):
    f, o = sample
    f["_private_column"] = ["a", "b", "c", "d"]
    f["explanation text"] = [1, 2, 3, 4]
    report = audit(f, o)
    assert report.rows["_private_column"].tolist() == ["a", "b", "c", "d"]
    assert report.rows["explanation text"].tolist() == [1, 2, 3, 4]


def test_output_column_collision_is_rejected_instead_of_overwriting_evidence(sample):
    f, o = sample
    f["paired"] = "caller evidence"
    with pytest.raises(ValueError, match="reserved"):
        audit(f, o)


def test_covariance_evidence_later_than_audit_clock_is_not_audited(sample):
    f, o = sample
    future = AS_OF + pd.Timedelta(days=1)
    f["forecast_at"] = future
    f["available_at"] = future
    f["raw_covariance"] = pd.Series([[[1]]] * 4, dtype=object)
    f["covariance_labels"] = [("F1",)] * 4
    f["covariance_unit"] = "return_bps^2"
    f["covariance_available_at"] = future
    f["covariance_source"] = "synthetic"
    report = audit(f, o)
    assert not report.rows.paired.any()
    assert report.rank_diagnostics.status.tolist() == ["unavailable_at_decision"] * 4
    assert report.rank_diagnostics.raw_rank.isna().all()


@pytest.mark.parametrize("matrix", [[[1, 1], [0, 1]], [[1, 0], [0, -1]], [[1e-20, 0], [0, -1e-20]]])
def test_invalid_covariance_evidence_is_not_silently_psd(matrix, sample):
    f, o = sample
    f["raw_covariance"] = pd.Series([matrix] * 4, dtype=object)
    f["covariance_labels"] = [("F1", "F2")] * 4
    f["covariance_unit"] = "return_bps^2"
    f["covariance_available_at"] = f.forecast_at
    f["covariance_source"] = "synthetic"
    with pytest.raises(ValueError, match="covariance"):
        audit(f, o)


def test_future_forecast_is_retained_without_pairing(sample):
    f, o = sample
    f.loc[0, ["forecast_at", "available_at"]] = AS_OF + pd.Timedelta(days=1)
    r = audit(f, o)
    assert not r.rows.iloc[0].paired
    assert "forecast_after_as_of" in r.rows.iloc[0].issues


def supplied_exposures(f, o):
    f["target_exposure"] = [0.5, -0.5, 1.0, 0.0]
    f["exposure_unit"] = "factor:SYNTHETIC"
    f["exposure_source"] = "synthetic-target-v1"
    f["exposure_available_at"] = f.forecast_at
    o["actual_exposure"] = [0.4, -0.2, 0.5, 0.1]
    o["exposure_unit"] = "factor:SYNTHETIC"
    o["exposure_source"] = "synthetic-observed-v1"
    o["exposure_observed_at"] = o.target_end
    o["exposure_available_at"] = o.available_at


def test_supplied_exposure_gaps_and_counts_are_descriptive_and_independent_of_risk(sample):
    f, o = sample
    supplied_exposures(f, o)
    f["forecast_variance"] = np.nan
    report = audit(f, o)
    assert report.summary.iloc[0].paired_observations == 0
    assert report.summary.iloc[0].exposure_observations == 4
    e = report.exposure_comparison
    assert e.status.tolist() == ["descriptive"] * 4
    assert e.signed_gap.tolist() == pytest.approx([-0.1, 0.3, -0.5, 0.1])
    assert e.absolute_gap.tolist() == pytest.approx([0.1, 0.3, 0.5, 0.1])
    assert e.exposure_unit.tolist() == ["factor:SYNTHETIC"] * 4
    assert report.certified is False


@pytest.mark.parametrize(
    "change,status",
    [
        ("unit", "unit_mismatch"),
        ("late_target", "target_exposure_unavailable"),
        ("late_actual", "actual_exposure_unavailable"),
        ("early_observation", "exposure_outside_horizon"),
        ("late_observation", "exposure_outside_horizon"),
        ("missing_actual", "missing_exposure"),
        ("missing_target", "missing_exposure"),
        ("missing_source", "missing_exposure_evidence"),
        ("missing_clock", "missing_exposure_evidence"),
    ],
)
def test_incompatible_optional_exposure_keeps_variance_pairs(sample, change, status):
    f, o = sample
    supplied_exposures(f, o)
    changes = {
        "unit": (o, "exposure_unit", "factor:OTHER"),
        "late_target": (f, "exposure_available_at", AS_OF),
        "late_actual": (o, "exposure_available_at", AS_OF + pd.Timedelta(days=2)),
        "early_observation": (
            o,
            "exposure_observed_at",
            o.target_start.iloc[0] - pd.Timedelta(seconds=1),
        ),
        "late_observation": (
            o,
            "exposure_observed_at",
            o.target_end.iloc[0] + pd.Timedelta(seconds=1),
        ),
        "missing_actual": (o, "actual_exposure", np.nan),
        "missing_target": (f, "target_exposure", np.nan),
        "missing_source": (o, "exposure_source", ""),
        "missing_clock": (o, "exposure_available_at", pd.NaT),
    }
    frame, column, value = changes[change]
    frame.loc[0, column] = value
    report = audit(f, o)
    assert report.summary.iloc[0].paired_observations == 4
    assert report.summary.iloc[0].exposure_observations == 3
    assert report.exposure_comparison.iloc[0].status == status
    assert pd.isna(report.exposure_comparison.iloc[0].signed_gap)


def supplied_intervals(f):
    f["prediction_lower"] = [-1.0, -2.0, 0.0, -7.0]
    f["prediction_upper"] = [1.0, 2.0, 3.0, -5.0]
    f["prediction_unit"] = f.unit
    f["prediction_source"] = "synthetic-bounds-v1"
    f["prediction_available_at"] = f.forecast_at
    f["prediction_nominal_level"] = 0.8


def test_supplied_bounds_coverage_is_literal_and_never_inferred_from_sigma(sample):
    f, o = sample
    supplied_intervals(f)
    f["forecast_variance"] = np.nan
    r = audit(f, o)
    assert r.prediction_intervals.covered.tolist() == [True, False, True, True]
    assert r.prediction_intervals.nominal_level.tolist() == [0.8] * 4
    s = r.summary.iloc[0]
    assert (s.interval_observations, s.interval_covered, s.interval_coverage) == (4, 3, 0.75)
    assert s.paired_observations == 0
    assert r.certified is False


@pytest.mark.parametrize(
    "change,status",
    [
        ("unit", "unit_mismatch"),
        ("late", "bounds_unavailable"),
        ("missing", "missing_bounds"),
        ("clock", "missing_bound_evidence"),
        ("source", "missing_bound_evidence"),
        ("outcome", "outcome_unavailable"),
    ],
)
def test_invalid_optional_bounds_do_not_change_variance_eligibility(sample, change, status):
    f, o = sample
    supplied_intervals(f)
    changes = {
        "unit": (f, "prediction_unit", "return_fraction"),
        "late": (f, "prediction_available_at", AS_OF),
        "missing": (f, "prediction_lower", np.nan),
        "clock": (f, "prediction_available_at", pd.NaT),
        "source": (f, "prediction_source", ""),
        "outcome": (o, "available_at", AS_OF + pd.Timedelta(days=1)),
    }
    frame, column, value = changes[change]
    frame.loc[0, column] = value
    r = audit(f, o)
    assert r.prediction_intervals.iloc[0].status == status
    assert pd.isna(r.prediction_intervals.iloc[0].covered)
    assert r.summary.iloc[0].interval_observations == 3
    assert r.summary.iloc[0].paired_observations == (3 if change == "outcome" else 4)


@pytest.mark.parametrize(
    "column,value",
    [("prediction_lower", 100.0), ("prediction_upper", np.inf), ("prediction_nominal_level", 1.1)],
)
def test_supplied_bounds_must_be_finite_ordered_and_level_valid(sample, column, value):
    f, o = sample
    supplied_intervals(f)
    f.loc[0, column] = value
    with pytest.raises(ValueError, match=r"bound|nominal|finite"):
        audit(f, o)


def test_small_unit_covariance_asymmetry_is_not_hidden_by_absolute_tolerance(sample):
    f, o = sample
    f["raw_covariance"] = pd.Series([[[1e-20, 1e-20], [0.0, 1e-20]]] * 4, dtype=object)
    f["covariance_labels"] = [("F1", "F2")] * 4
    f["covariance_unit"] = "return_bps^2"
    f["covariance_available_at"] = f.forecast_at
    f["covariance_source"] = "synthetic"
    with pytest.raises(ValueError, match="symmetric"):
        audit(f, o)


def test_large_finite_variances_do_not_overflow_into_healthy_zero_ratio(sample):
    f, o = sample
    f["forecast_variance"] = 1e308
    o["realized"] = 1.0
    s = audit(f, o).summary.iloc[0]
    assert np.isfinite(s.predicted_variance)
    assert s.predicted_variance == pytest.approx(1e308)
    assert s.variance_ratio == 1e-308


@pytest.mark.parametrize("measure", ["volatility", "squared_residual", "ratio"])
def test_nonfinite_calculations_fail_explicitly(sample, measure):
    f, o = sample
    if measure == "volatility":
        f = f.drop(columns="forecast_variance")
        f["forecast_volatility"] = 1e308
    elif measure == "squared_residual":
        o["realized"] = 1e308
    else:
        f["forecast_variance"] = 1e-320
        o["realized"] = 1e150
    with pytest.raises(ValueError, match="finite"):
        audit(f, o)


@pytest.mark.parametrize("measure", ["volatility", "squared_residual", "ratio"])
def test_positive_values_cannot_underflow_into_exact_zero_diagnostics(sample, measure):
    f, o = sample
    if measure == "volatility":
        f = f.drop(columns="forecast_variance")
        f["forecast_volatility"] = 1e-200
    elif measure == "squared_residual":
        o["realized"] = 1e-200
    else:
        f["forecast_variance"] = 1e300
        o["realized"] = 1e-150
    with pytest.raises(ValueError, match="representable"):
        audit(f, o)


def test_smallest_representable_positive_variance_mean_stays_positive(sample):
    f, o = sample
    f["forecast_variance"] = np.nextafter(0.0, 1.0)
    o["realized"] = 0.0
    s = audit(f, o).summary.iloc[0]
    assert s.predicted_variance == np.nextafter(0.0, 1.0)
    assert s.variance_ratio == 0


@pytest.mark.parametrize(
    "side,column,initial,changed",
    [
        ("forecast", "forecast_variance", 1.0, 1.00000000001),
        ("forecast", "forecast_variance", 1.0, np.nextafter(1.0, 2.0)),
        ("forecast", "forecast_variance", 1e-200, np.nextafter(1e-200, 1.0)),
        ("outcome", "realized", 1.0, 1.00000000001),
        ("outcome", "realized", 1.0, np.nextafter(1.0, 2.0)),
        ("outcome", "realized", 1e-150, np.nextafter(1e-150, 1.0)),
    ],
)
def test_input_digest_distinguishes_lossless_accepted_numeric_values(
    sample, side, column, initial, changed
):
    f, o = sample
    frame = f if side == "forecast" else o
    frame.loc[0, column] = initial
    before = audit(f, o)
    frame.loc[0, column] = changed
    after = audit(f, o)
    if side == "forecast":
        assert before.rows.iloc[0].predicted_variance != after.rows.iloc[0].predicted_variance
    else:
        assert before.rows.iloc[0].matched_realized != after.rows.iloc[0].matched_realized
    assert before.input_digest != after.input_digest


@pytest.mark.parametrize("container", [list, np.array])
def test_input_digest_preserves_nested_covariance_float_differences(sample, container):
    f, o = sample
    f["raw_covariance"] = pd.Series([container([[1.0]])] * 4, dtype=object)
    f["covariance_labels"] = [("F1",)] * 4
    f["covariance_unit"] = "return_bps^2"
    f["covariance_available_at"] = f.forecast_at
    f["covariance_source"] = "synthetic"
    before = audit(f, o)
    f.at[0, "raw_covariance"] = container([[np.nextafter(1.0, 2.0)]])
    after = audit(f, o)
    assert before.rows.iloc[0].raw_covariance[0][0] != after.rows.iloc[0].raw_covariance[0][0]
    assert before.input_digest != after.input_digest


def test_input_digest_is_canonical_for_mapping_order_indices_and_matrix_containers(sample):
    f, o = sample
    f["raw_covariance"] = pd.Series([[[1.0]]] * 4, dtype=object)
    f["covariance_labels"] = [("F1",)] * 4
    f["covariance_unit"] = "return_bps^2"
    f["covariance_available_at"] = f.forecast_at
    f["covariance_source"] = "synthetic"
    f["annotation"] = [{"a": 1.0, "b": 2.0}] * 4
    before = audit(f, o)
    f["raw_covariance"] = [np.array([[1.0]])] * 4
    f["covariance_labels"] = [["F1"]] * 4
    f["annotation"] = [{"b": 2.0, "a": 1.0}] * 4
    f.index = [3, 3, 0, 1]
    o.index = [3, 3, 0, 1]
    after = audit(f[f.columns[::-1]], o[o.columns[::-1]])
    assert before.input_digest == after.input_digest
