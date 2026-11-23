"""Fitted scores must be invariant to future data and unavailable outcomes."""

from dataclasses import replace

import numpy as np
import pandas as pd
import pytest
from alpha_research.factor_composition import FactorCompositionSpec, FactorInput, compose_factors


def fixture(method):
    index = pd.MultiIndex.from_product(
        [pd.date_range("2026-01-01", periods=8), list("ABCDEF")], names=["date", "symbol"]
    )
    frame = pd.DataFrame(
        {"Q": [1.0, 2.0, 3.0, 4.0, 5.0, 6.0] * 8, "V": [3.0, 1.0, 5.0, 2.0, 6.0, 4.0] * 8},
        index=index,
    )
    labels = (frame.Q * 0.01).rename("future_return")
    available = pd.Series(index.get_level_values("date") + pd.Timedelta(days=1), index=index)
    config = FactorCompositionSpec(
        "fitted",
        "v1",
        (FactorInput("Q", "q", "v1"), FactorInput("V", "v", "v1")),
        method=method,
        normalization="zscore",
        window=4,
        min_periods=2,
        min_cross_section=5,
    )
    return frame, labels, available, config


@pytest.mark.parametrize("method", ["ic", "icir", "covariance", "pca", "ridge", "pls"])
def test_fitted_methods_have_warmup_and_chronological_prefix_invariance(method):
    frame, labels, available, config = fixture(method)
    result = compose_factors(frame, config, labels=labels, label_available_at=available)
    assert (
        result.scores.loc[:"2026-01-03"].isna().all()
        if method != "pca"
        else (result.scores.loc[:"2026-01-02"].isna().all())
    )
    assert result.scores.loc["2026-01-06"].notna().all()
    prefix = frame.loc[:"2026-01-06"]
    earlier = compose_factors(
        prefix,
        config,
        labels=labels.loc[prefix.index],
        label_available_at=available.loc[prefix.index],
    )
    pd.testing.assert_series_equal(result.scores.loc[prefix.index], earlier.scores)
    fitted = result.fit_audit.query("status == 'fitted'")
    assert (fitted.train_end < fitted.date).all()
    if method != "pca":
        assert (fitted.max_label_available_at < fitted.date).all()


def test_ic_uses_only_complete_matured_cross_sections_and_ignores_future_targets():
    frame, labels, available, config = fixture("ic")
    available.loc[pd.IndexSlice[pd.Timestamp("2026-01-01"), "A"]] = pd.Timestamp("2027-01-01")
    result = compose_factors(frame, config, labels=labels, label_available_at=available)
    assert result.scores.loc["2026-01-04"].isna().all()  # Jan 1 is not fully available.
    expected = compose_factors(frame, config, labels=labels, label_available_at=available)
    changed = labels.copy()
    changed.loc["2026-01-05":] *= -1000
    actual = compose_factors(frame, config, labels=changed, label_available_at=available)
    pd.testing.assert_series_equal(
        expected.scores.loc[:"2026-01-06"], actual.scores.loc[:"2026-01-06"]
    )


def test_ic_weights_are_positive_normalized_and_turnover_capped():
    frame, labels, available, config = fixture("ic")
    labels.loc["2026-01-04":] = frame.loc["2026-01-04":, "V"] * 0.1
    result = compose_factors(
        frame,
        replace(config, max_weight_turnover=0.05),
        labels=labels,
        label_available_at=available,
    )
    w = result.weights.groupby(level="date").first().dropna()
    np.testing.assert_allclose(w.sum(axis=1), 1.0)
    assert (w >= 0).all().all()
    assert (w.diff().abs().sum(axis=1) <= 0.05 + 1e-12).all()


def test_negative_ic_does_not_reverse_declared_factor_direction():
    frame, labels, available, config = fixture("ic")
    result = compose_factors(frame, config, labels=-labels, label_available_at=available)
    assert result.scores.isna().all()
    assert "no_positive_strength" in result.fit_audit.status.values


@pytest.mark.parametrize("bad", ["absent", "index", "nat", "before_feature"])
def test_supervised_fit_requires_aligned_valid_label_availability(bad):
    frame, labels, available, config = fixture("ridge")
    if bad == "absent":
        available = None
    elif bad == "index":
        labels = labels.iloc[:-1]
    elif bad == "nat":
        available.iloc[0] = pd.NaT
    else:
        available.iloc[0] = pd.Timestamp("2025-01-01")
    with pytest.raises(ValueError):
        compose_factors(frame, config, labels=labels, label_available_at=available)


def test_ridge_learns_linear_target_and_pca_sign_is_deterministic():
    frame, labels, available, config = fixture("ridge")
    result = compose_factors(
        frame, replace(config, regularization=0.000001), labels=labels, label_available_at=available
    )
    np.testing.assert_allclose(
        result.scores.loc["2026-01-08"], [0.01, 0.02, 0.03, 0.04, 0.05, 0.06], atol=1e-7
    )
    pca = compose_factors(frame, replace(config, method="pca"))
    w = pca.weights.dropna().iloc[0]
    assert w.loc[w.abs().idxmax()] > 0


def test_missing_prediction_inputs_remain_missing_and_no_labels_needed_for_pca():
    frame, labels, available, config = fixture("ridge")
    frame.iloc[-1, 0] = np.nan
    result = compose_factors(frame, config, labels=labels, label_available_at=available)
    assert np.isnan(result.scores.iloc[-1])
    assert compose_factors(frame, replace(config, method="pca")).scores.notna().any()


def test_lightgbm_is_chronological_and_exposes_no_fake_linear_coefficients():
    pytest.importorskip("lightgbm")
    frame, labels, available, config = fixture("lightgbm")
    result = compose_factors(frame, config, labels=labels, label_available_at=available)
    assert result.scores.loc["2026-01-08"].notna().all()
    assert result.weights.isna().all().all()
    assert result.fit_audit.query("status == 'fitted'").model_state_sha256.str.len().eq(64).all()
    changed = labels.copy()
    changed.loc["2026-01-07":] *= -100
    other = compose_factors(frame, config, labels=changed, label_available_at=available)
    pd.testing.assert_series_equal(result.scores, other.scores)


def test_complex_labels_are_rejected_instead_of_discarded():
    frame, labels, available, config = fixture("ridge")
    with pytest.raises(ValueError, match="real"):
        compose_factors(
            frame, config, labels=labels.astype(complex) + 1j, label_available_at=available
        )
