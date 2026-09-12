from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from portfolio_backtester.risk_model import (
    RiskModelConfig,
    attribute_portfolio_risk,
    build_risk_model,
    estimate_factor_returns,
    validate_risk_inputs,
)


def _synthetic_panel() -> tuple[pd.DataFrame, pd.Series]:
    dates = pd.date_range("2024-01-02", periods=8, freq="B")
    symbols = ["A", "B", "C", "D"]
    index = pd.MultiIndex.from_product([dates, symbols], names=["as_of_date", "symbol"])
    rows = []
    returns = []
    for date_number, _date in enumerate(dates):
        for symbol_number, _symbol in enumerate(symbols):
            size = (symbol_number - 1.5) / 1.5
            momentum = ((symbol_number + 1) * (date_number + 1) % 5 - 2) / 2.0
            rows.append((size, momentum))
            returns.append(0.01 * size + 0.02 * momentum + 0.0001 * (symbol_number - date_number))
    return pd.DataFrame(rows, index=index, columns=["size", "momentum"]), pd.Series(
        returns, index=index, name="total_return"
    )


def test_validate_risk_inputs_accepts_canonical_panel() -> None:
    exposures, returns = _synthetic_panel()
    validate_risk_inputs(exposures, returns)


@pytest.mark.parametrize(
    ("mutate", "message"),
    [
        (
            lambda e, r: e.set_axis(pd.MultiIndex.from_tuples(e.index, names=["date", "symbol"])),
            "index names",
        ),
        (
            lambda e, r: e.set_axis(
                pd.MultiIndex.from_tuples([e.index[0]] * len(e), names=["as_of_date", "symbol"])
            ),
            "duplicate",
        ),
        (lambda e, r: (e, r.where(r.index != r.index[0], np.nan)), "non-finite"),
    ],
)
def test_validate_risk_inputs_rejects_invalid_inputs(mutate, message: str) -> None:
    exposures, returns = _synthetic_panel()
    result = mutate(exposures, returns)
    if isinstance(result, tuple):
        exposures, returns = result
    else:
        exposures = result
    with pytest.raises(ValueError, match=message):
        validate_risk_inputs(exposures, returns)


def test_validate_risk_inputs_requires_a_sufficient_cross_section() -> None:
    exposures, returns = _synthetic_panel()
    with pytest.raises(ValueError, match="min_cross_section"):
        validate_risk_inputs(
            exposures.iloc[:2],
            returns.iloc[:2],
            config=RiskModelConfig(min_cross_section=3),
        )


def test_estimate_factor_returns_recovers_synthetic_coefficients() -> None:
    exposures, _returns = _synthetic_panel()
    exact_returns = pd.Series(
        0.01 * exposures["size"] + 0.02 * exposures["momentum"],
        index=exposures.index,
        name="total_return",
    )
    result = estimate_factor_returns(exposures, exact_returns)
    assert result.factor_returns.shape == (8, 2)
    assert np.allclose(result.factor_returns["size"], 0.01, atol=2e-5)
    assert np.allclose(result.factor_returns["momentum"], 0.02, atol=2e-5)
    fitted = result.residual_returns["fitted_return"]
    residual = result.residual_returns["residual_return"]
    assert np.allclose(fitted + residual, result.residual_returns["total_return"], equal_nan=False)
    assert (result.diagnostics["status"] == "ok").all()


def test_estimate_factor_returns_reports_insufficient_date() -> None:
    exposures, returns = _synthetic_panel()
    first_date = exposures.index.get_level_values("as_of_date").unique()[0]
    first_keys = exposures.loc[first_date].index[:2]
    keep = pd.MultiIndex.from_tuples(
        [(first_date, symbol) for symbol in first_keys], names=["as_of_date", "symbol"]
    )
    reduced_exposures = pd.concat(
        [exposures.loc[keep], exposures.loc[exposures.index.get_level_values(0) != first_date]]
    )
    reduced_returns = pd.concat(
        [returns.loc[keep], returns.loc[returns.index.get_level_values(0) != first_date]]
    )
    result = estimate_factor_returns(
        reduced_exposures, reduced_returns, config=RiskModelConfig(min_cross_section=3)
    )
    assert result.diagnostics.loc[first_date, "status"] == "insufficient_cross_section"
    assert first_date not in result.factor_returns.index


def test_estimate_factor_returns_honors_observation_weights() -> None:
    exposures, returns = _synthetic_panel()
    returns = returns.copy()
    weights = pd.Series(1.0, index=returns.index)
    first_date = returns.index.get_level_values("as_of_date").unique()[0]
    returns.loc[(first_date, "A")] += 0.01
    weights.loc[(first_date, "A")] = 1_000_000.0
    weighted = estimate_factor_returns(exposures, returns, weights=weights)
    unweighted = estimate_factor_returns(exposures, returns)
    assert not np.allclose(
        weighted.factor_returns.loc[first_date], unweighted.factor_returns.loc[first_date]
    )


def test_build_risk_model_returns_psd_covariance_and_specific_risk() -> None:
    exposures, returns = _synthetic_panel()
    factor_result = estimate_factor_returns(exposures, returns)
    risk = build_risk_model(factor_result.factor_returns, factor_result.residual_returns)
    assert risk.factor_covariance.index.tolist() == ["size", "momentum"]
    assert np.allclose(risk.factor_covariance, risk.factor_covariance.T)
    assert np.linalg.eigvalsh(risk.factor_covariance.to_numpy()).min() >= -1e-12
    assert (risk.specific_variance.dropna() >= 0).all()
    assert risk.diagnostics.loc["model", "factor_observations"] == 8


def test_build_risk_model_requires_enough_factor_history() -> None:
    factor_returns = pd.DataFrame({"size": [0.01]}, index=pd.date_range("2024-01-01", periods=1))
    residual_returns = pd.DataFrame()
    with pytest.raises(ValueError, match="at least two"):
        build_risk_model(factor_returns, residual_returns)


def test_attribute_portfolio_risk_reconciles_variance() -> None:
    exposures = pd.DataFrame(
        {"size": [1.0, -1.0], "momentum": [0.5, 0.25]},
        index=pd.Index(["A", "B"], name="symbol"),
    )
    weights = pd.Series([0.6, 0.4], index=["A", "B"])
    covariance = pd.DataFrame(
        [[0.04, 0.01], [0.01, 0.09]], index=exposures.columns, columns=exposures.columns
    )
    specific = pd.Series({"A": 0.01, "B": 0.02})
    result = attribute_portfolio_risk(weights, exposures, covariance, specific)
    factor_variance = float(result.portfolio_exposure @ covariance @ result.portfolio_exposure)
    expected_specific = float((weights.pow(2) * specific).sum())
    assert np.isclose(result.factor_contribution.sum(), factor_variance)
    assert np.isclose(result.specific_variance, expected_specific)
    assert np.isclose(result.total_variance, factor_variance + expected_specific)
    assert np.isclose(result.total_volatility, np.sqrt(result.total_variance))


def test_attribute_portfolio_risk_accepts_one_date_multiindex_snapshot() -> None:
    exposures = pd.DataFrame(
        {"size": [1.0, -1.0]},
        index=pd.MultiIndex.from_tuples(
            [(pd.Timestamp("2024-01-02"), "A"), (pd.Timestamp("2024-01-02"), "B")],
            names=["as_of_date", "symbol"],
        ),
    )
    result = attribute_portfolio_risk(
        pd.Series([0.5, 0.5], index=["A", "B"]),
        exposures,
        pd.DataFrame([[0.04]], index=["size"], columns=["size"]),
        pd.Series({"A": 0.01, "B": 0.01}),
    )
    assert np.isclose(result.portfolio_exposure["size"], 0.0)


def test_attribute_portfolio_risk_rejects_missing_symbol() -> None:
    exposures = pd.DataFrame({"size": [1.0]}, index=pd.Index(["A"], name="symbol"))
    with pytest.raises(ValueError, match="missing exposures"):
        attribute_portfolio_risk(
            pd.Series([0.5, 0.5], index=["A", "B"]),
            exposures,
            pd.DataFrame([[0.04]], index=["size"], columns=["size"]),
            pd.Series({"A": 0.01, "B": 0.01}),
        )
