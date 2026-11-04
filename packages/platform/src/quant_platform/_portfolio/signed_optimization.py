"""Convex signed portfolio research with explicit assumed costs; never executable."""

from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Literal

import numpy as np
import pandas as pd
from scipy.optimize import Bounds, LinearConstraint, linprog, minimize


@dataclass(frozen=True)
class SignedOptimizationRequest:
    """All returns, covariance and cost rates cover exactly ``horizon_days``.

    Weights and rates are decimals per unit portfolio NAV, not percentages.
    Borrow rates charge negative holdings; holding rates charge absolute holdings.
    Timestamps must be timezone aware; the caller attests all inputs were known
    at information_time. Costs are assumptions, never evidence of borrow access.
    """

    expected_returns: pd.Series
    covariance: pd.DataFrame
    current_weights: pd.Series
    lower_bounds: pd.Series
    upper_bounds: pd.Series
    trade_costs: pd.Series
    borrow_costs: pd.Series
    holding_costs: pd.Series
    factor_loadings: pd.DataFrame
    factor_bounds: Mapping[str, tuple[float, float]]
    gross_limit: float
    net_target: float
    risk_aversion: float
    horizon_days: int
    units: Literal["horizon_decimal"]
    assumptions: str
    information_time: pd.Timestamp
    decision_time: pd.Timestamp


@dataclass(frozen=True)
class SignedOptimizationResult:
    status: Literal["optimal", "infeasible", "numerical_failure"]
    message: str
    weights: pd.Series | None = None
    gross: float | None = None
    net: float | None = None
    turnover: float | None = None
    expected_return: float | None = None
    variance: float | None = None
    trade_cost: float | None = None
    borrow_cost: float | None = None
    holding_cost: float | None = None
    factor_exposures: Mapping[str, float] = field(default_factory=dict)
    residuals: Mapping[str, float] = field(default_factory=dict)
    active: bool = False
    paper_only: Literal[True] = field(default=True, init=False)
    executable: Literal[False] = field(default=False, init=False)


def _validate(r: SignedOptimizationRequest) -> None:
    index = r.expected_returns.index
    if index.empty or not index.is_unique or index.hasnans:
        raise ValueError("Assets must be nonempty, unique and nonmissing")
    for name in (
        "expected_returns",
        "current_weights",
        "lower_bounds",
        "upper_bounds",
        "trade_costs",
        "borrow_costs",
        "holding_costs",
    ):
        value = getattr(r, name)
        if not value.index.equals(index) or not np.isfinite(value.to_numpy(dtype=float)).all():
            raise ValueError(f"{name} must have matching finite asset values")
    cov = r.covariance
    if (
        not cov.index.equals(index)
        or not cov.columns.equals(index)
        or not np.isfinite(cov.to_numpy(dtype=float)).all()
    ):
        raise ValueError("Covariance must have matching finite asset axes")
    matrix = cov.to_numpy(dtype=float)
    if not np.allclose(matrix, matrix.T, atol=1e-12, rtol=0):
        raise ValueError("Covariance must be symmetric")
    if np.linalg.eigvalsh(matrix).min() < -1e-12:
        raise ValueError("Covariance must be positive semidefinite")
    _validate_factors(r, index)
    _validate_policy(r)


def _validate_factors(r: SignedOptimizationRequest, index: pd.Index) -> None:
    factors = r.factor_loadings
    if (
        not factors.index.equals(index)
        or not factors.columns.is_unique
        or not all(isinstance(name, str) and name for name in factors.columns)
        or not np.isfinite(factors.to_numpy(dtype=float)).all()
    ):
        raise ValueError("Factor loadings must have unique names and matching finite assets")
    for name, bounds in r.factor_bounds.items():
        if (
            name not in factors.columns
            or len(bounds) != 2
            or not np.isfinite(bounds).all()
            or bounds[0] > bounds[1]
        ):
            raise ValueError("Factor bounds must be finite, ordered and named in loadings")


def _validate_policy(r: SignedOptimizationRequest) -> None:
    if (
        not np.isfinite([r.gross_limit, r.net_target, r.risk_aversion]).all()
        or r.gross_limit < 0
        or r.risk_aversion <= 0
    ):
        raise ValueError("Gross must be nonnegative and risk aversion positive; scalars finite")
    if (r.lower_bounds > r.upper_bounds).any():
        raise ValueError("Asset bounds must be ordered")
    if any(
        (getattr(r, name) < 0).any() for name in ("trade_costs", "borrow_costs", "holding_costs")
    ):
        raise ValueError("Costs must be nonnegative explicit assumptions")
    if (
        isinstance(r.horizon_days, bool)
        or not isinstance(r.horizon_days, int)
        or r.horizon_days <= 0
        or r.units != "horizon_decimal"
    ):
        raise ValueError("Positive integer horizon and horizon_decimal units required")
    if not isinstance(r.assumptions, str) or not r.assumptions.strip():
        raise ValueError("Explicit assumptions required")
    for timestamp in (r.information_time, r.decision_time):
        if (
            not isinstance(timestamp, pd.Timestamp)
            or pd.isna(timestamp)
            or timestamp.tzinfo is None
        ):
            raise ValueError(
                "Valid timezone-aware pandas Timestamp information and decision times required"
            )
    if r.information_time > r.decision_time:
        raise ValueError("Information must not follow decision time")


def _constraints(r: SignedOptimizationRequest):
    n = len(r.expected_returns)
    current = r.current_weights.to_numpy(dtype=float)
    # x = [signed weights, absolute turnover, absolute holdings, short holdings].
    size = 4 * n
    rows, limits = [], []
    for i in range(n):
        for sign in (1, -1):
            row = np.zeros(size)
            row[i], row[n + i] = sign, -1
            rows.append(row)
            limits.append(sign * current[i])
            row = np.zeros(size)
            row[i], row[2 * n + i] = sign, -1
            rows.append(row)
            limits.append(0.0)
        row = np.zeros(size)
        row[i], row[3 * n + i] = -1, -1
        rows.append(row)
        limits.append(0.0)
    row = np.zeros(size)
    row[2 * n : 3 * n] = 1
    rows.append(row)
    limits.append(r.gross_limit)
    for name, (lower, upper) in r.factor_bounds.items():
        row = np.zeros(size)
        row[:n] = r.factor_loadings[name].to_numpy(dtype=float)
        rows.extend([row, -row])
        limits.extend([upper, -lower])
    a, b = np.asarray(rows), np.asarray(limits)
    eq = np.zeros((1, size))
    eq[0, :n] = 1
    lower = np.r_[r.lower_bounds.to_numpy(dtype=float), np.zeros(3 * n)]
    upper = np.r_[r.upper_bounds.to_numpy(dtype=float), np.full(3 * n, np.inf)]
    return a, b, eq, lower, upper


def optimize_signed_paper(r: SignedOptimizationRequest) -> SignedOptimizationResult:
    """Minimize risk/2 - alpha + linear trade, borrow and holding costs.

    Gross is an upper bound, never a mandatory investment level. Failure returns
    no weights or score. LP infeasibility is distinct from numerical failure.
    """
    _validate(r)
    n = len(r.expected_returns)
    alpha = r.expected_returns.to_numpy(dtype=float)
    covariance = r.covariance.to_numpy(dtype=float)
    current = r.current_weights.to_numpy(dtype=float)
    size = 4 * n
    a, b, eq, lower, upper = _constraints(r)
    linear = np.r_[-alpha, r.trade_costs, r.holding_costs, r.borrow_costs]
    feasible = linprog(
        np.zeros(size),
        A_ub=a,
        b_ub=b,
        A_eq=eq,
        b_eq=[r.net_target],
        bounds=list(zip(lower, upper, strict=True)),
        method="highs",
    )
    if not feasible.success:
        return SignedOptimizationResult(
            "infeasible" if feasible.status == 2 else "numerical_failure", feasible.message
        )

    def objective(x):
        return 0.5 * r.risk_aversion * x[:n] @ covariance @ x[:n] + linear @ x

    def gradient(x):
        grad = linear.copy()
        grad[:n] += r.risk_aversion * covariance @ x[:n]
        return grad

    solution = minimize(
        objective,
        feasible.x,
        jac=gradient,
        method="SLSQP",
        bounds=Bounds(lower, upper),
        constraints=[
            LinearConstraint(a, -np.inf, b),
            LinearConstraint(eq, r.net_target, r.net_target),
        ],
        options={"ftol": 1e-12, "maxiter": 1000},
    )
    if not solution.success or not np.isfinite(solution.x).all():
        return SignedOptimizationResult("numerical_failure", str(solution.message))
    w = solution.x[:n]
    gross, net = float(np.abs(w).sum()), float(w.sum())
    exposures = r.factor_loadings.T @ w
    residuals = {
        "gross": max(0.0, gross - r.gross_limit),
        "net": abs(net - r.net_target),
        "asset_lower": max(0.0, float((lower[:n] - w).max())),
        "asset_upper": max(0.0, float((w - upper[:n]).max())),
        "auxiliary": max(0.0, float((a @ solution.x - b).max())),
    }
    for name, (lo, hi) in r.factor_bounds.items():
        residuals[f"factor:{name}"] = max(0.0, lo - exposures[name], exposures[name] - hi)
    if max(residuals.values()) > 1e-7:
        return SignedOptimizationResult("numerical_failure", "Constraint residual exceeds 1e-7")
    return SignedOptimizationResult(
        status="optimal",
        message=str(solution.message),
        weights=pd.Series(w, index=r.expected_returns.index, name="weight"),
        gross=gross,
        net=net,
        turnover=float(np.abs(w - current).sum()),
        expected_return=float(alpha @ w),
        variance=float(w @ covariance @ w),
        trade_cost=float(r.trade_costs @ np.abs(w - current)),
        borrow_cost=float(r.borrow_costs @ np.maximum(-w, 0)),
        holding_cost=float(r.holding_costs @ np.abs(w)),
        factor_exposures=exposures.to_dict(),
        residuals=residuals,
        active=gross > 1e-7,
    )
