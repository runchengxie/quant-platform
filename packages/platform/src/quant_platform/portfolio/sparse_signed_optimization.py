"""Explicit optional OSQP factor-risk signed paper optimization.

Risk is B F B' + diag(D); only the small F is dense. No asset covariance is
constructed. Solver objects are mutable, sequential-use research resources.
"""

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Literal

import numpy as np
import pandas as pd
from scipy import sparse

from quant_platform._portfolio.signed_optimization import (
    SignedOptimizationResult,
    _validate_factors,
    _validate_policy,
)


@dataclass(frozen=True)
class SparseSignedOptimizationRequest:
    """Signed request semantics, with horizon factor risk replacing covariance.

    ``risk_loadings`` B has fewer columns than assets; F axes match its columns
    exactly. D is nonnegative asset-specific variance. Constraint factors are
    independent of risk factors. All inputs must be known at information_time.
    """

    expected_returns: pd.Series
    risk_loadings: pd.DataFrame
    factor_covariance: pd.DataFrame
    specific_variance: pd.Series
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


def _validate(r):
    index = r.expected_returns.index
    if index.empty or not index.is_unique or index.hasnans:
        raise ValueError("Assets must be nonempty, unique and nonmissing")
    for name in (
        "expected_returns",
        "specific_variance",
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
    b, f = r.risk_loadings, r.factor_covariance
    if (
        not b.index.equals(index)
        or not b.columns.is_unique
        or b.columns.hasnans
        or not 0 < len(b.columns) < len(index)
        or not all(isinstance(name, str) and name for name in b.columns)
        or not np.isfinite(b.to_numpy(dtype=float)).all()
    ):
        raise ValueError("Risk loadings require matching assets and fewer unique named factors")
    if (
        not f.index.equals(b.columns)
        or not f.columns.equals(b.columns)
        or not np.isfinite(f.to_numpy(dtype=float)).all()
    ):
        raise ValueError("Factor covariance must have matching finite factor axes")
    matrix = f.to_numpy(dtype=float)
    if not np.array_equal(matrix, matrix.T):
        raise ValueError("Factor covariance must be symmetric")
    if np.linalg.eigvalsh(matrix).min() < 0 or (r.specific_variance < 0).any():
        raise ValueError("Factor covariance must be PSD and specific variance nonnegative")
    _validate_factors(r, index)
    _validate_policy(r)


def _problem(r):
    n, k = r.risk_loadings.shape
    eye, zero = sparse.eye(n, format="csc"), sparse.csc_matrix((n, n))
    zfactor = sparse.csc_matrix((n, k))
    # x = [weights, abs trades, abs holdings, short holdings, risk exposures].
    rows = [sparse.eye(4 * n + k, format="csc")]
    lower = [np.r_[r.lower_bounds, np.zeros(3 * n), np.full(k, -np.inf)]]
    upper = [np.r_[r.upper_bounds, np.full(3 * n + k, np.inf)]]
    current = r.current_weights.to_numpy(dtype=float)
    for blocks, limit in (
        ([eye, -eye, zero, zero, zfactor], current),
        ([-eye, -eye, zero, zero, zfactor], -current),
        ([eye, zero, -eye, zero, zfactor], np.zeros(n)),
        ([-eye, zero, -eye, zero, zfactor], np.zeros(n)),
        ([-eye, zero, zero, -eye, zfactor], np.zeros(n)),
    ):
        rows.append(sparse.hstack(blocks, format="csc"))
        lower.append(np.full(n, -np.inf))
        upper.append(limit)
    rows.append(sparse.csc_matrix(np.r_[np.ones(n), np.zeros(3 * n + k)][None, :]))
    lower.append([r.net_target])
    upper.append([r.net_target])
    rows.append(sparse.csc_matrix(np.r_[np.zeros(2 * n), np.ones(n), np.zeros(n + k)][None, :]))
    lower.append([-np.inf])
    upper.append([r.gross_limit])
    rows.append(
        sparse.hstack(
            [
                sparse.csc_matrix(r.risk_loadings.to_numpy().T),
                sparse.csc_matrix((k, 3 * n)),
                -sparse.eye(k),
            ],
            format="csc",
        )
    )
    lower.append(np.zeros(k))
    upper.append(np.zeros(k))
    for name, (lo, hi) in r.factor_bounds.items():
        rows.append(sparse.csc_matrix(np.r_[r.factor_loadings[name], np.zeros(3 * n + k)][None, :]))
        lower.append([lo])
        upper.append([hi])
    p = sparse.block_diag(
        [
            sparse.diags(r.specific_variance.to_numpy()),
            sparse.csc_matrix((3 * n, 3 * n)),
            sparse.csc_matrix(r.factor_covariance),
        ],
        format="csc",
    )
    p = sparse.triu(p * r.risk_aversion, format="csc")
    a = sparse.vstack(rows, format="csc")
    p.sort_indices()
    a.sort_indices()
    q = np.r_[-r.expected_returns, r.trade_costs, r.holding_costs, r.borrow_costs, np.zeros(k)]
    return p, q, a, np.concatenate(lower), np.concatenate(upper)


def _pattern(matrix):
    return matrix.shape, matrix.indptr.tobytes(), matrix.indices.tobytes()


class SparseSignedOptimizer:
    """OSQP must be selected explicitly and installed with ``[sparse]``.

    Repeated solves update values and warm-start only when labels and actual CSC
    patterns match. Any structural change rebuilds; no dense solver fallback.
    Only OSQP's solved status plus independent residual checks release weights.
    """

    def __init__(self, *, backend, max_iter=100_000, time_limit=10.0, tolerance=1e-9):
        if backend != "osqp":
            raise ValueError("Explicit backend='osqp' is required")
        if (
            isinstance(max_iter, bool)
            or not isinstance(max_iter, int)
            or max_iter < 1
            or not np.isfinite([time_limit, tolerance]).all()
            or time_limit <= 0
            or not 0 < tolerance <= 1e-7
        ):
            raise ValueError("Positive iteration/time limits and tolerance <= 1e-7 required")
        try:
            import osqp
        except ImportError as exc:
            raise ImportError("Install quant-platform[sparse] to select OSQP") from exc
        self._factory = osqp.OSQP
        self._settings = {
            "max_iter": max_iter,
            "time_limit": time_limit,
            "eps_abs": tolerance,
            "eps_rel": tolerance,
            "polishing": True,
            "verbose": False,
        }
        self._solver = None
        self._signature = None
        self.structure_stats = {"setups": 0, "updates": 0}

    def solve(self, r: SparseSignedOptimizationRequest) -> SignedOptimizationResult:
        """Return existing signed scalar/cost semantics, never executable weights."""
        _validate(r)
        try:
            with np.errstate(over="raise", invalid="raise"):
                p, q, a, lo, hi = _problem(r)
        except FloatingPointError as exc:
            return SignedOptimizationResult("numerical_failure", str(exc))
        signature = (
            _pattern(p),
            _pattern(a),
            tuple(r.expected_returns.index),
            tuple(r.risk_loadings.columns),
            tuple(r.factor_loadings.columns),
            tuple(r.factor_bounds),
        )
        try:
            if self._solver is None or signature != self._signature:
                self._solver = self._factory()
                self._solver.setup(P=p, q=q, A=a, l=lo, u=hi, **self._settings)
                self._signature = signature
                self.structure_stats["setups"] += 1
            else:
                self._solver.update(Px=p.data, Ax=a.data, q=q, l=lo, u=hi)
                self.structure_stats["updates"] += 1
            self.structure_stats.update(
                p_nnz=p.nnz, a_nnz=a.nnz, variables=p.shape[0], constraints=a.shape[0]
            )
            solved = self._solver.solve(raise_error=False)
        except Exception as exc:
            self._solver, self._signature = None, None
            return SignedOptimizationResult("numerical_failure", str(exc))
        if solved.info.status_val != 1:
            status = "infeasible" if solved.info.status_val == 3 else "numerical_failure"
            return SignedOptimizationResult(status, str(solved.info.status))
        return _receipt(r, solved.x, a, lo, hi, str(solved.info.status))


def _receipt(r, x, a, lo, hi, message):
    try:
        with np.errstate(over="raise", invalid="raise", divide="raise"):
            return _checked_receipt(r, x, a, lo, hi, message)
    except FloatingPointError:
        return SignedOptimizationResult("numerical_failure", "Nonfinite derived receipt")


def _checked_receipt(r, x, a, lo, hi, message):
    if x is None or not np.isfinite(x).all():
        return SignedOptimizationResult("numerical_failure", "Nonfinite solution")
    n = len(r.expected_returns)
    w = x[:n]
    gross, net = float(np.abs(w).sum()), float(w.sum())
    exposures = r.factor_loadings.T @ w
    values = a @ x
    if not np.isfinite(values).all() or not np.isfinite(exposures.to_numpy()).all():
        return SignedOptimizationResult("numerical_failure", "Nonfinite derived receipt")
    residuals = {
        "gross": max(0.0, gross - r.gross_limit),
        "net": abs(net - r.net_target),
        "asset_lower": max(0.0, float((r.lower_bounds - w).max())),
        "asset_upper": max(0.0, float((w - r.upper_bounds).max())),
        "auxiliary": max(0.0, float(np.max(lo - values)), float(np.max(values - hi))),
    }
    for name, (lower, upper) in r.factor_bounds.items():
        residuals[f"factor:{name}"] = max(0.0, lower - exposures[name], exposures[name] - upper)
    risk = r.risk_loadings.to_numpy().T @ w
    variance = float(
        risk @ r.factor_covariance.to_numpy() @ risk + r.specific_variance.to_numpy() @ (w * w)
    )
    if max(residuals.values()) > 1e-7 or not np.isfinite(variance):
        return SignedOptimizationResult("numerical_failure", "Constraint residual exceeds 1e-7")
    trades = np.abs(w - r.current_weights.to_numpy())
    economics = {
        "gross": gross,
        "net": net,
        "turnover": float(trades.sum()),
        "expected_return": float(r.expected_returns @ w),
        "variance": variance,
        "trade_cost": float(r.trade_costs @ trades),
        "borrow_cost": float(r.borrow_costs @ np.maximum(-w, 0)),
        "holding_cost": float(r.holding_costs @ np.abs(w)),
    }
    if not np.isfinite([*economics.values(), *residuals.values()]).all():
        return SignedOptimizationResult("numerical_failure", "Nonfinite derived receipt")
    return SignedOptimizationResult(
        status="optimal",
        message=message,
        weights=pd.Series(w, index=r.expected_returns.index, name="weight"),
        **economics,
        factor_exposures=exposures.to_dict(),
        residuals=residuals,
        active=gross > 1e-7,
    )
