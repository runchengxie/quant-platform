"""Legacy portfolio mechanics preserve cash and shrinkage semantics."""

import importlib

import numpy as np
import pandas as pd


def api():
    return importlib.import_module("portfolio_backtester.legacy_rotation")


def test_equal_weights_preserve_cash_when_cap_is_tight():
    assert api().build_equal_weight_portfolio(["A", "B"], 0.2) == {"A": 0.2, "B": 0.2}


def test_covariance_shrinkage_retains_labels_and_ridge():
    cov = pd.DataFrame([[4.0, 2.0], [2.0, 6.0]], index=["A", "B"], columns=["A", "B"])
    result = api().shrink_covariance_matrix(cov, 0.5)
    np.testing.assert_allclose(result.to_numpy(), [[4.000005000001, 1.0], [1.0, 6.000005000001]])
    assert list(result.index) == ["A", "B"]


def test_optimization_without_covariance_respects_cap():
    result = api().optimize_portfolio_weights(
        pd.Series([0.1, 0.2], index=["A", "B"]), max_weight_per_asset=0.3
    )
    assert result == {"A": 0.3, "B": 0.3}


def test_zero_cap_retains_all_cash_even_with_covariance():
    cov = pd.DataFrame([[0.04, 0.01], [0.01, 0.09]], index=["A", "B"], columns=["A", "B"])
    for cap in [0.0, -0.1]:
        assert (
            api().optimize_portfolio_weights(
                pd.Series([0.1, 0.2], index=["A", "B"]), cov, max_weight_per_asset=cap
            )
            == {}
        )


def test_covariance_labels_are_aligned_before_optimization():
    mu = pd.Series([0.1, 0.2], index=["A", "B"])
    cov = pd.DataFrame([[0.01, 0.005], [0.005, 0.25]], index=["A", "B"], columns=["A", "B"])
    expected = api().optimize_portfolio_weights(mu, cov, max_weight_per_asset=0.8)
    reordered = api().optimize_portfolio_weights(
        mu, cov.loc[["B", "A"], ["B", "A"]], max_weight_per_asset=0.8
    )
    np.testing.assert_allclose(list(expected.values()), list(reordered.values()), atol=1e-8)
