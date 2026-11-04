"""Sparse factor QP behavior against independent dense and analytic references."""

from dataclasses import fields, replace

import numpy as np
import pandas as pd
import pytest
from test_signed_optimization import request

from quant_platform.portfolio import sparse_signed_optimization as sparse
from quant_platform.portfolio.signed_optimization import optimize_signed_paper


def factor_request(**changes):
    dense = request()
    values = {f.name: getattr(dense, f.name) for f in fields(dense) if f.name != "covariance"}
    values.update(
        risk_loadings=dense.factor_loadings.copy(),
        factor_covariance=pd.DataFrame([[0.02]], index=["beta"], columns=["beta"]),
        specific_variance=pd.Series(0.1, index=dense.expected_returns.index),
    )
    values.update(changes)
    return sparse.SparseSignedOptimizationRequest(**values)


def dense_request(r):
    values = {f.name: getattr(r, f.name) for f in fields(request()) if f.name != "covariance"}
    b = r.risk_loadings.to_numpy()
    values["covariance"] = pd.DataFrame(
        b @ r.factor_covariance.to_numpy() @ b.T + np.diag(r.specific_variance),
        index=r.expected_returns.index,
        columns=r.expected_returns.index,
    )
    return replace(request(), **values)


def score(r, result):
    return (
        r.risk_aversion * result.variance / 2
        - result.expected_return
        + result.trade_cost
        + result.borrow_cost
        + result.holding_cost
    )


@pytest.mark.parametrize("bounds", [{}, {"beta": (0, 0)}])
def test_dense_objective_and_all_constraints(bounds):
    r = factor_request(factor_bounds=bounds)
    r = replace(
        r,
        trade_costs=r.trade_costs + 0.002,
        borrow_costs=r.borrow_costs + 0.003,
        holding_costs=r.holding_costs + 0.001,
    )
    got = sparse.SparseSignedOptimizer(backend="osqp").solve(r)
    reference = optimize_signed_paper(dense_request(r))
    assert got.status == reference.status == "optimal"
    assert score(r, got) == pytest.approx(score(r, reference), abs=1e-7)
    assert max(got.residuals.values()) <= 1e-7
    assert got.paper_only and not got.executable
    assert got.trade_cost == pytest.approx(0.002 * got.turnover)
    assert got.borrow_cost == pytest.approx(0.003 * np.maximum(-got.weights, 0).sum())


def test_warm_updates_and_pattern_invalidation_match_cold_objective():
    solver = sparse.SparseSignedOptimizer(backend="osqp")
    r = factor_request()
    assert solver.solve(r).status == "optimal"
    updated = replace(
        r,
        expected_returns=r.expected_returns * 0.2,
        current_weights=pd.Series([0.1, -0.1, 0], index=r.expected_returns.index),
        specific_variance=r.specific_variance * 2,
        risk_loadings=r.risk_loadings * 2,
        factor_covariance=r.factor_covariance * 2,
        trade_costs=r.trade_costs + 0.01,
        borrow_costs=r.borrow_costs + 0.002,
        holding_costs=r.holding_costs + 0.001,
        lower_bounds=r.lower_bounds * 0.8,
        upper_bounds=r.upper_bounds * 0.8,
        gross_limit=0.8,
        net_target=0.01,
    )
    warm = solver.solve(updated)
    cold = sparse.SparseSignedOptimizer(backend="osqp").solve(updated)
    assert warm.status == cold.status == "optimal"
    assert score(updated, warm) == pytest.approx(score(updated, cold), abs=1e-7)
    assert solver.structure_stats["setups"] == 1
    assert solver.structure_stats["updates"] == 1
    changed = replace(updated, factor_bounds={"beta": (-0.1, 0.1)})
    assert solver.solve(changed).status == "optimal"
    assert solver.structure_stats["setups"] == 2


def test_degenerate_multiple_optima_and_infeasible_have_honest_status():
    r = factor_request()
    zero = replace(
        r,
        expected_returns=r.expected_returns * 0,
        specific_variance=r.specific_variance * 0,
        factor_covariance=r.factor_covariance * 0,
    )
    solver = sparse.SparseSignedOptimizer(backend="osqp")
    assert score(zero, solver.solve(zero)) == pytest.approx(0, abs=1e-7)
    failed = solver.solve(replace(r, net_target=2))
    assert failed.status == "infeasible"
    assert failed.weights is None and failed.variance is None
    limited = sparse.SparseSignedOptimizer(backend="osqp", max_iter=1).solve(r)
    assert limited.status == "numerical_failure"
    assert limited.weights is None


@pytest.mark.parametrize("kind", ["negative", "indefinite", "labels", "future", "naive", "many"])
def test_invalid_factor_and_clock_contracts(kind):
    r = factor_request()
    if kind == "negative":
        r = replace(r, specific_variance=r.specific_variance - 1)
    elif kind == "indefinite":
        r = replace(r, factor_covariance=r.factor_covariance - 1)
    elif kind == "labels":
        r = replace(r, specific_variance=r.specific_variance.iloc[::-1])
    elif kind == "future":
        r = replace(r, information_time=r.decision_time + pd.Timedelta(days=1))
    elif kind == "naive":
        r = replace(r, information_time=pd.Timestamp("2026-01-01"))
    else:
        r = replace(r, risk_loadings=pd.DataFrame(np.eye(3), index=r.expected_returns.index))
    with pytest.raises(ValueError):
        sparse.SparseSignedOptimizer(backend="osqp").solve(r)


def test_backend_is_explicit_and_sparse_problem_storage_scales_linearly():
    with pytest.raises(ValueError):
        sparse.SparseSignedOptimizer(backend="automatic")
    r = factor_request()
    solver = sparse.SparseSignedOptimizer(backend="osqp")
    solver.solve(r)
    assert solver.structure_stats["p_nnz"] < 10
    assert solver.structure_stats["a_nnz"] < 100


def test_timeout_releases_no_weights():
    result = sparse.SparseSignedOptimizer(backend="osqp", time_limit=1e-9).solve(factor_request())
    assert result.status == "numerical_failure"
    assert result.weights is None and result.trade_cost is None


def test_independent_residual_check_rejects_corrupted_solver_solution(monkeypatch):
    import osqp

    real_solve = osqp.OSQP.solve

    def corrupt(self, **kwargs):
        result = real_solve(self, **kwargs)
        result.x[0] = 10
        return result

    monkeypatch.setattr(osqp.OSQP, "solve", corrupt)
    result = sparse.SparseSignedOptimizer(backend="osqp").solve(factor_request())
    assert result.status == "numerical_failure"
    assert result.weights is None and result.expected_return is None


def test_optional_dependency_failure_is_explicit(monkeypatch):
    import builtins

    original = builtins.__import__

    def missing(name, *args, **kwargs):
        if name == "osqp":
            raise ImportError("synthetic missing optional backend")
        return original(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", missing)
    with pytest.raises(ImportError, match=r"quant-platform\[sparse\]"):
        sparse.SparseSignedOptimizer(backend="osqp")


def test_zero_pattern_change_rebuilds_and_produces_feasible_updated_solution():
    solver = sparse.SparseSignedOptimizer(backend="osqp")
    r = factor_request()
    assert solver.solve(r).status == "optimal"
    result = solver.solve(replace(r, risk_loadings=r.risk_loadings * 0))
    assert result.status == "optimal"
    assert max(result.residuals.values()) <= 1e-7
    assert solver.structure_stats["setups"] == 2


def test_finite_inputs_that_overflow_qp_are_numerical_failure():
    r = factor_request(risk_aversion=1e308)
    r = replace(r, specific_variance=r.specific_variance * 1e100)
    result = sparse.SparseSignedOptimizer(backend="osqp").solve(r)
    assert result.status == "numerical_failure"
    assert result.weights is None
