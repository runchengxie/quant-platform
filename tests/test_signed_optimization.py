from dataclasses import replace

import numpy as np
import pandas as pd
import pytest

from quant_platform.portfolio.signed_optimization import (
    SignedOptimizationRequest,
    optimize_signed_paper,
)


def request(**kwargs):
    assets = pd.Index(["a", "b", "c"])

    def series(values):
        return pd.Series(values, index=assets, dtype=float)

    base = SignedOptimizationRequest(
        expected_returns=series([0.1, -0.1, 0]),
        covariance=pd.DataFrame(np.eye(3) * 0.1, index=assets, columns=assets),
        current_weights=series([0, 0, 0]),
        lower_bounds=series([-0.5] * 3),
        upper_bounds=series([0.5] * 3),
        trade_costs=series([0] * 3),
        borrow_costs=series([0] * 3),
        holding_costs=series([0] * 3),
        factor_loadings=pd.DataFrame({"beta": [2.0, 1.0, 0.0]}, index=assets),
        factor_bounds={},
        gross_limit=1.0,
        net_target=0.0,
        risk_aversion=1.0,
        horizon_days=5,
        units="horizon_decimal",
        assumptions="Synthetic assumed costs only",
        information_time=pd.Timestamp("2026-01-01", tz="UTC"),
        decision_time=pd.Timestamp("2026-01-02", tz="UTC"),
    )
    return replace(base, **kwargs)


def test_net_neutral_is_not_beta_neutral_and_factor_bound_is_enforced():
    unconstrained = optimize_signed_paper(request())
    assert unconstrained.status == "optimal"
    assert unconstrained.net == pytest.approx(0, abs=1e-7)
    assert unconstrained.factor_exposures["beta"] > 0.4
    constrained = optimize_signed_paper(request(factor_bounds={"beta": (0.0, 0.0)}))
    assert constrained.status == "optimal"
    assert abs(constrained.factor_exposures["beta"]) < 1e-7
    assert constrained.gross <= 1 + 1e-7
    assert constrained.weights.abs().max() <= 0.5 + 1e-7
    assert max(constrained.residuals.values()) < 1e-7
    assert constrained.paper_only and not constrained.executable


def test_costs_can_make_zero_exposure_optimal_and_visible():
    req = request()
    costly = optimize_signed_paper(
        replace(req, trade_costs=req.trade_costs + 0.2, borrow_costs=req.borrow_costs + 0.2)
    )
    assert costly.status == "optimal"
    assert costly.gross == pytest.approx(0, abs=1e-7)
    assert not costly.active
    assert costly.turnover == pytest.approx(0, abs=1e-7)


def test_infeasible_constraints_have_no_scored_fallback():
    result = optimize_signed_paper(request(factor_bounds={"beta": (4.0, 5.0)}))
    assert result.status == "infeasible"
    assert result.weights is None
    assert result.expected_return is None
    assert optimize_signed_paper(request(net_target=2)).status == "infeasible"


@pytest.mark.parametrize(
    "kind",
    [
        "duplicate",
        "missing",
        "nan",
        "indefinite",
        "future",
        "asymmetric",
        "horizon",
        "units",
        "assumptions",
    ],
)
def test_invalid_inputs_are_rejected(kind):
    req = request()
    if kind == "duplicate":
        req.expected_returns.index = ["a", "a", "c"]
    elif kind == "missing":
        req = replace(req, trade_costs=req.trade_costs.iloc[:2])
    elif kind == "nan":
        req.expected_returns.iloc[0] = np.nan
    elif kind == "indefinite":
        req.covariance.iloc[0, 0] = -1
    elif kind == "asymmetric":
        req.covariance.iloc[0, 1] = 0.1
    elif kind == "future":
        req = replace(req, information_time=req.decision_time + pd.Timedelta(days=1))
    elif kind == "horizon":
        req = replace(req, horizon_days=0)
    elif kind == "units":
        req = replace(req, units="annual_percent")
    else:
        req = replace(req, assumptions="")
    with pytest.raises(ValueError):
        optimize_signed_paper(req)


def test_active_gross_and_asset_caps_and_actual_cost_receipt():
    req = request(gross_limit=0.4)
    result = optimize_signed_paper(req)
    assert result.gross == pytest.approx(0.4, abs=1e-7)
    assert result.active
    tight = optimize_signed_paper(replace(req, upper_bounds=req.upper_bounds * 0 + 0.05))
    assert tight.weights["a"] == pytest.approx(0.05, abs=1e-7)
    assert tight.gross < result.gross
    costly = optimize_signed_paper(replace(request(), borrow_costs=req.borrow_costs + 0.12))
    assert 0 < costly.gross < 1
    assert costly.borrow_cost == pytest.approx(0.12 * costly.gross / 2, abs=1e-7)
    assert costly.turnover == pytest.approx(costly.gross, abs=1e-7)


def test_holding_cost_and_nonzero_current_weights_affect_optimum():
    req = request()
    current = req.current_weights.copy()
    current.iloc[:] = [0.2, -0.2, 0]
    result = optimize_signed_paper(
        replace(req, current_weights=current, trade_costs=req.trade_costs + 0.2)
    )
    assert result.turnover == pytest.approx(0, abs=1e-7)
    assert result.gross == pytest.approx(0.4, abs=1e-7)
    holding = optimize_signed_paper(replace(req, holding_costs=req.holding_costs + 0.2))
    assert not holding.active


@pytest.mark.parametrize(
    "kind",
    ["negative_cost", "factor_missing", "factor_nan", "duplicate_cov", "naive_time", "bad_bounds"],
)
def test_additional_invalid_contracts(kind):
    req = request()
    if kind == "negative_cost":
        req.borrow_costs.iloc[0] = -0.1
    elif kind == "factor_missing":
        req = replace(req, factor_bounds={"unknown": (0.0, 0.0)})
    elif kind == "factor_nan":
        req.factor_loadings.iloc[0, 0] = np.nan
    elif kind == "duplicate_cov":
        req.covariance.columns = ["a", "a", "c"]
    elif kind == "naive_time":
        req = replace(req, information_time=pd.Timestamp("2026-01-01"))
    else:
        req = replace(req, lower_bounds=req.lower_bounds + 2)
    with pytest.raises(ValueError):
        optimize_signed_paper(req)


def test_alpha_risk_tradeoff_has_hand_computed_interior_solution():
    req = request()
    result = optimize_signed_paper(replace(req, expected_returns=req.expected_returns * .2))
    assert result.weights.to_list() == pytest.approx([.2, -.2, 0], abs=1e-6)
    assert result.expected_return == pytest.approx(.008, abs=1e-7)
    assert result.variance == pytest.approx(.008, abs=1e-7)
