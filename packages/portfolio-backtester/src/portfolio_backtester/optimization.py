"""Framework-neutral portfolio optimization boundary with native baselines."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from math import isfinite
from typing import Any, Protocol, runtime_checkable

import numpy as np
import pandas as pd

from .hrp import HrpConfig, hierarchical_risk_parity

PORTFOLIO_OPTIMIZATION_RESULT_SCHEMA = "portfolio_optimization_result.v1"


@dataclass(frozen=True)
class LinearExposureConstraint:
    """Bounds on a generic linear portfolio exposure."""

    name: str
    values: pd.Series
    lower: float | None = None
    upper: float | None = None

    def __post_init__(self) -> None:
        if not str(self.name).strip():
            raise ValueError("linear exposure constraint name must be non-empty")
        if self.lower is None and self.upper is None:
            raise ValueError("linear exposure constraint needs a lower or upper bound")
        for label, value in (("lower", self.lower), ("upper", self.upper)):
            if value is not None and (not np.isfinite(value)):
                raise ValueError(f"linear exposure constraint {label} must be finite")
        if self.lower is not None and self.upper is not None and self.lower > self.upper:
            raise ValueError("linear exposure constraint lower must be <= upper")
        if not isinstance(self.values, pd.Series):
            raise TypeError("linear exposure constraint values must be a pandas Series")


def _numeric_series_for_assets(
    value: pd.Series | None,
    assets: tuple[str, ...],
    *,
    label: str,
) -> pd.Series | None:
    if value is None:
        return None
    if not isinstance(value, pd.Series):
        raise TypeError(f"{label} must be a pandas Series")
    normalized = pd.to_numeric(value, errors="coerce")
    if set(map(str, normalized.index)) != set(assets):
        raise ValueError(f"{label} assets must match returns columns")
    normalized.index = normalized.index.map(str)
    normalized = normalized.reindex(assets)
    if normalized.isna().any() or not np.isfinite(normalized.to_numpy(dtype=float)).all():
        raise ValueError(f"{label} must contain finite values for every asset")
    return normalized.astype(float)


def _project_weights_to_bounds(
    weights: pd.Series,
    *,
    min_weight: float,
    max_weight: float | None,
) -> pd.Series:
    """Project positive preference weights into a feasible long-only box simplex.

    Lower bounds are assigned first and the remaining mass is distributed in
    proportion to the original preferences, repeatedly saturating upper bounds.
    This avoids the common `clip -> normalize` bug where normalization can push a
    previously clipped lower-bound weight below the promised minimum again.
    """

    numeric = pd.to_numeric(weights, errors="coerce").astype(float)
    if numeric.isna().any() or not np.isfinite(numeric.to_numpy()).all():
        raise ValueError("optimizer preference weights must be finite")
    if (numeric < 0).any():
        raise ValueError("optimizer preference weights must be non-negative")
    total = float(numeric.sum())
    if total <= 0:
        numeric[:] = 1.0
        total = float(numeric.sum())
    preference = numeric / total

    count = len(preference)
    upper = 1.0 if max_weight is None else max_weight
    result = np.full(count, min_weight, dtype=float)
    capacity = np.full(count, upper - min_weight, dtype=float)
    remaining = 1.0 - min_weight * count
    preference_values = preference.to_numpy(dtype=float)
    tolerance = 1e-12

    for _ in range(count + 2):
        if remaining <= tolerance:
            break
        eligible = capacity > tolerance
        if not eligible.any():
            break
        allocation_preference = np.where(eligible, preference_values, 0.0)
        preference_sum = float(allocation_preference.sum())
        if preference_sum <= tolerance:
            allocation_preference = eligible.astype(float)
            preference_sum = float(allocation_preference.sum())
        proposed = remaining * allocation_preference / preference_sum
        allocation = np.minimum(proposed, capacity)
        used = float(allocation.sum())
        result += allocation
        capacity -= allocation
        remaining -= used
        if used <= tolerance:
            break

    if abs(remaining) > 1e-9:
        raise ValueError("failed to project optimizer weights into requested bounds")
    return pd.Series(result, index=preference.index, dtype=float)


@dataclass(frozen=True)
class PortfolioOptimizationRequest:
    """Stable optimizer input independent of any third-party solver object."""

    returns: pd.DataFrame
    expected_returns: pd.Series | None = None
    previous_weights: pd.Series | None = None
    benchmark_weights: pd.Series | None = None
    anchor_weights: pd.Series | None = None
    covariance: pd.DataFrame | None = None
    linear_constraints: tuple[LinearExposureConstraint, ...] = ()
    min_weight: float = 0.0
    max_weight: float | None = None
    covariance_shrinkage: float = 0.0
    long_only: bool = True

    def __post_init__(self) -> None:  # noqa: C901
        if not isinstance(self.returns, pd.DataFrame):
            raise TypeError("returns must be a pandas DataFrame")
        if self.returns.empty or self.returns.shape[1] == 0:
            raise ValueError("returns must contain at least one asset")
        assets = tuple(map(str, self.returns.columns))
        if len(set(assets)) != len(assets):
            raise ValueError("returns columns must be unique")
        numeric = self.returns.apply(pd.to_numeric, errors="coerce")
        if numeric.dropna(how="all").empty:
            raise ValueError("returns must contain numeric observations")
        object.__setattr__(self, "returns", numeric.set_axis(assets, axis=1))
        object.__setattr__(
            self,
            "expected_returns",
            _numeric_series_for_assets(self.expected_returns, assets, label="expected_returns"),
        )
        object.__setattr__(
            self,
            "previous_weights",
            _numeric_series_for_assets(self.previous_weights, assets, label="previous_weights"),
        )
        object.__setattr__(
            self,
            "benchmark_weights",
            _numeric_series_for_assets(self.benchmark_weights, assets, label="benchmark_weights"),
        )
        object.__setattr__(
            self,
            "anchor_weights",
            _numeric_series_for_assets(self.anchor_weights, assets, label="anchor_weights"),
        )
        if self.covariance is not None:
            if not isinstance(self.covariance, pd.DataFrame):
                raise TypeError("covariance must be a pandas DataFrame")
            covariance = self.covariance.copy()
            covariance.index = covariance.index.map(str)
            covariance.columns = covariance.columns.map(str)
            if covariance.index.tolist() != list(assets) or covariance.columns.tolist() != list(
                assets
            ):
                raise ValueError("covariance assets must match returns columns in order")
            numeric_covariance = covariance.apply(pd.to_numeric, errors="coerce")
            if not np.isfinite(numeric_covariance.to_numpy(dtype=float)).all():
                raise ValueError("covariance must contain finite values")
            if not np.allclose(numeric_covariance, numeric_covariance.T):
                raise ValueError("covariance must be symmetric")
            object.__setattr__(self, "covariance", numeric_covariance.astype(float))
        normalized_constraints: list[LinearExposureConstraint] = []
        names: set[str] = set()
        for constraint in self.linear_constraints:
            if not isinstance(constraint, LinearExposureConstraint):
                raise TypeError("linear_constraints must contain LinearExposureConstraint values")
            values = _numeric_series_for_assets(constraint.values, assets, label=constraint.name)
            assert values is not None
            if constraint.name in names:
                raise ValueError(f"duplicate linear exposure constraint: {constraint.name}")
            names.add(constraint.name)
            normalized_constraints.append(
                LinearExposureConstraint(
                    name=constraint.name,
                    values=values,
                    lower=constraint.lower,
                    upper=constraint.upper,
                )
            )
        object.__setattr__(self, "linear_constraints", tuple(normalized_constraints))
        if self.min_weight < 0:
            raise ValueError("min_weight must be >= 0")
        if self.max_weight is not None and self.max_weight <= 0:
            raise ValueError("max_weight must be > 0")
        if self.max_weight is not None and self.min_weight > self.max_weight:
            raise ValueError("min_weight must be <= max_weight")
        if not 0.0 <= self.covariance_shrinkage <= 1.0:
            raise ValueError("covariance_shrinkage must be in [0, 1]")
        if not self.long_only:
            raise ValueError("native optimizer baselines currently require long_only=True")
        count = len(assets)
        if self.min_weight * count > 1.0 + 1e-12:
            raise ValueError("min_weight is infeasible for the number of assets")
        if self.max_weight is not None and self.max_weight * count < 1.0 - 1e-12:
            raise ValueError("max_weight is infeasible for the number of assets")

    @property
    def assets(self) -> tuple[str, ...]:
        return tuple(map(str, self.returns.columns))


@dataclass(frozen=True)
class PortfolioOptimizationResult:
    backend_name: str
    weights: pd.Series
    diagnostics: Mapping[str, Any] = field(default_factory=dict)
    schema_version: str = PORTFOLIO_OPTIMIZATION_RESULT_SCHEMA

    def validate(self, request: PortfolioOptimizationRequest) -> None:
        if not self.backend_name.strip():
            raise ValueError("backend_name must be non-empty")
        if self.schema_version != PORTFOLIO_OPTIMIZATION_RESULT_SCHEMA:
            raise ValueError(f"unsupported optimization result schema {self.schema_version!r}")
        if not isinstance(self.weights, pd.Series):
            raise TypeError("weights must be a pandas Series")
        weights = pd.to_numeric(self.weights, errors="coerce")
        weights.index = weights.index.map(str)
        if set(weights.index) != set(request.assets):
            raise ValueError("weights assets must match optimization request")
        weights = weights.reindex(request.assets)
        values = weights.to_numpy(dtype=float)
        if np.isnan(values).any() or not np.isfinite(values).all():
            raise ValueError("weights must be finite")
        if abs(float(weights.sum()) - 1.0) > 1e-8:
            raise ValueError("weights must sum to 1")
        if request.long_only and (weights < -1e-12).any():
            raise ValueError("long-only weights must be non-negative")
        if (weights < request.min_weight - 1e-12).any():
            raise ValueError("weights violate min_weight")
        if request.max_weight is not None and (weights > request.max_weight + 1e-12).any():
            raise ValueError("weights violate max_weight")
        _validate_json_scalars(self.diagnostics)


@runtime_checkable
class PortfolioOptimizerBackend(Protocol):
    name: str

    def run(self, request: PortfolioOptimizationRequest) -> PortfolioOptimizationResult: ...


@dataclass(frozen=True)
class InverseVolConfig:
    """Configuration for inverse-volatility preference weighting."""

    lookback: int = 252
    exponent: float = 0.5
    min_periods: int | None = None

    def __post_init__(self) -> None:
        if (
            isinstance(self.lookback, bool)
            or not isinstance(self.lookback, int)
            or self.lookback <= 0
        ):
            raise ValueError("lookback must be a positive integer")
        if not np.isfinite(self.exponent) or self.exponent <= 0:
            raise ValueError("exponent must be finite and positive")
        min_periods = self.lookback if self.min_periods is None else self.min_periods
        if (
            isinstance(min_periods, bool)
            or not isinstance(min_periods, int)
            or not 1 <= min_periods <= self.lookback
        ):
            raise ValueError("min_periods must be an integer in [1, lookback]")
        object.__setattr__(self, "min_periods", min_periods)


@dataclass(frozen=True)
class PortfolioQpConfig:
    """Objective controls for the native convex quadratic risk optimizer."""

    anchor_penalty: float = 0.0
    previous_penalty: float = 0.0
    max_iterations: int = 1_000
    tolerance: float = 1e-9

    def __post_init__(self) -> None:
        for name in ("anchor_penalty", "previous_penalty"):
            value = getattr(self, name)
            if not np.isfinite(value) or value < 0:
                raise ValueError(f"{name} must be finite and non-negative")
        if isinstance(self.max_iterations, bool) or self.max_iterations < 0:
            raise ValueError("max_iterations must be a non-negative integer")
        if not np.isfinite(self.tolerance) or self.tolerance <= 0:
            raise ValueError("tolerance must be finite and positive")


class OptimizerRegistry:
    """Explicit registry; external optimizer adapters never leak their native objects."""

    def __init__(self) -> None:
        self._backends: dict[str, PortfolioOptimizerBackend] = {}

    def register(self, backend: PortfolioOptimizerBackend) -> None:
        name = str(backend.name).strip()
        if not name:
            raise ValueError("optimizer backend name must be non-empty")
        if name in self._backends:
            raise ValueError(f"optimizer backend already registered: {name}")
        self._backends[name] = backend

    def get(self, name: str) -> PortfolioOptimizerBackend:
        try:
            return self._backends[name]
        except KeyError as exc:
            known = ", ".join(sorted(self._backends)) or "<none>"
            raise KeyError(f"Unknown optimizer backend {name!r}; registered: {known}") from exc

    def names(self) -> tuple[str, ...]:
        return tuple(sorted(self._backends))

    def run(self, name: str, request: PortfolioOptimizationRequest) -> PortfolioOptimizationResult:
        result = self.get(name).run(request)
        result.validate(request)
        return result


class EqualWeightOptimizerBackend:
    name = "native.equal_weight"

    def run(self, request: PortfolioOptimizationRequest) -> PortfolioOptimizationResult:
        weight = 1.0 / len(request.assets)
        result = PortfolioOptimizationResult(
            backend_name=self.name,
            weights=pd.Series(weight, index=request.assets, dtype=float),
            diagnostics={"method": "equal_weight", "asset_count": len(request.assets)},
        )
        result.validate(request)
        return result


class HrpOptimizerBackend:
    name = "native.hrp"

    def run(self, request: PortfolioOptimizationRequest) -> PortfolioOptimizationResult:
        if len(request.assets) < 2:
            result = PortfolioOptimizationResult(
                backend_name=self.name,
                weights=pd.Series(1.0, index=request.assets, dtype=float),
                diagnostics={"method": "hrp", "fallback": "single_asset"},
            )
            result.validate(request)
            return result
        hrp = hierarchical_risk_parity(
            request.returns,
            config=HrpConfig(
                shrinkage=request.covariance_shrinkage,
                min_weight=0.0,
                max_weight=None,
            ),
        )
        projected = _project_weights_to_bounds(
            hrp.weights.reindex(request.assets).fillna(0.0),
            min_weight=request.min_weight,
            max_weight=request.max_weight,
        )
        result = PortfolioOptimizationResult(
            backend_name=self.name,
            weights=projected,
            diagnostics={
                "method": "hrp",
                "ordered_assets": list(hrp.ordered_assets),
                "covariance_shrinkage": request.covariance_shrinkage,
                "bounds_projected": request.min_weight > 0 or request.max_weight is not None,
            },
        )
        result.validate(request)
        return result


class InverseVolOptimizerBackend:
    """Allocate by inverse recent volatility, then project into requested bounds."""

    name = "native.inverse_vol"

    def __init__(self, config: InverseVolConfig | None = None) -> None:
        self.config = config or InverseVolConfig()

    def run(self, request: PortfolioOptimizationRequest) -> PortfolioOptimizationResult:
        if len(request.assets) == 1:
            result = PortfolioOptimizationResult(
                backend_name=self.name,
                weights=pd.Series(1.0, index=request.assets, dtype=float),
                diagnostics={
                    "method": "inverse_volatility",
                    "lookback": self.config.lookback,
                    "exponent": self.config.exponent,
                    "min_periods": self.config.min_periods,
                    "bounds_projected": request.min_weight > 0 or request.max_weight is not None,
                    "fallback": "single_asset",
                },
            )
            result.validate(request)
            return result

        window = request.returns.tail(self.config.lookback)
        observations = window.notna().sum()
        insufficient = observations[observations < self.config.min_periods]
        if not insufficient.empty:
            assets = ", ".join(map(str, insufficient.index))
            raise ValueError(f"insufficient observations for inverse volatility: {assets}")

        volatility = window.std(ddof=1)
        invalid = volatility[~np.isfinite(volatility) | (volatility <= 0)]
        if not invalid.empty:
            assets = ", ".join(map(str, invalid.index))
            raise ValueError(f"assets must have positive finite volatility: {assets}")

        preference = volatility.pow(-self.config.exponent)
        weights = _project_weights_to_bounds(
            preference,
            min_weight=request.min_weight,
            max_weight=request.max_weight,
        )
        result = PortfolioOptimizationResult(
            backend_name=self.name,
            weights=weights,
            diagnostics={
                "method": "inverse_volatility",
                "lookback": self.config.lookback,
                "exponent": self.config.exponent,
                "min_periods": self.config.min_periods,
                "bounds_projected": request.min_weight > 0 or request.max_weight is not None,
            },
        )
        result.validate(request)
        return result


def _qp_covariance(request: PortfolioOptimizationRequest) -> tuple[np.ndarray, str]:
    if request.covariance is not None:
        covariance = request.covariance.to_numpy(dtype=float)
        source = "request"
    else:
        observations = request.returns.dropna(how="any")
        if len(observations) < 2:
            raise ValueError("at least two complete return observations are required for QP")
        covariance = observations.cov(ddof=1).to_numpy(dtype=float)
        source = "sample"
    covariance = (covariance + covariance.T) / 2.0
    if request.covariance_shrinkage:
        diagonal = np.diag(np.diag(covariance))
        covariance = (
            1.0 - request.covariance_shrinkage
        ) * covariance + request.covariance_shrinkage * diagonal
    minimum_eigenvalue = float(np.linalg.eigvalsh(covariance).min())
    if minimum_eigenvalue < -1e-10:
        raise ValueError("covariance must be positive semidefinite")
    return covariance, source


def _qp_constraint_residuals(
    weights: np.ndarray,
    constraints: tuple[LinearExposureConstraint, ...],
) -> dict[str, float]:
    residuals: dict[str, float] = {}
    for constraint in constraints:
        exposure = float(weights @ constraint.values.to_numpy(dtype=float))
        if constraint.lower is not None:
            residuals[constraint.name] = exposure - constraint.lower
        if constraint.upper is not None:
            residuals[f"{constraint.name}.upper"] = constraint.upper - exposure
    return residuals


class QpMinVarianceOptimizerBackend:
    """Minimize covariance risk while preserving optional portfolio structure.

    The backend deliberately treats scores, sectors, styles, and other model
    outputs as anonymous linear exposures. Strategy-specific meaning stays in
    the caller; the platform only solves and validates the QP.
    """

    name = "native.qp_min_variance"

    def __init__(self, config: PortfolioQpConfig | None = None) -> None:
        self.config = config or PortfolioQpConfig()

    def run(self, request: PortfolioOptimizationRequest) -> PortfolioOptimizationResult:  # noqa: C901
        try:
            from scipy.optimize import minimize
        except ImportError as exc:  # pragma: no cover - depends on environment packaging
            raise ImportError("native.qp_min_variance requires scipy") from exc

        covariance, covariance_source = _qp_covariance(request)
        assets = request.assets
        count = len(assets)
        equal = np.full(count, 1.0 / count, dtype=float)
        anchor = (
            request.anchor_weights.to_numpy(dtype=float)
            if request.anchor_weights is not None
            else equal
        )
        previous = (
            request.previous_weights.to_numpy(dtype=float)
            if request.previous_weights is not None
            else None
        )
        q = covariance.copy()
        if self.config.anchor_penalty:
            q += 2.0 * self.config.anchor_penalty * np.eye(count)
        if self.config.previous_penalty:
            q += 2.0 * self.config.previous_penalty * np.eye(count)
        linear_term = np.zeros(count, dtype=float)
        if self.config.anchor_penalty:
            linear_term -= 2.0 * self.config.anchor_penalty * anchor
        if previous is not None and self.config.previous_penalty:
            linear_term -= 2.0 * self.config.previous_penalty * previous

        def objective(weights: np.ndarray) -> float:
            return float(
                0.5 * weights @ q @ weights
                + linear_term @ weights
                + self.config.anchor_penalty * anchor @ anchor
                + (
                    self.config.previous_penalty * previous @ previous
                    if previous is not None
                    else 0.0
                )
            )

        def gradient(weights: np.ndarray) -> np.ndarray:
            return q @ weights + linear_term

        constraints: list[dict[str, Any]] = [{"type": "eq", "fun": lambda w: float(w.sum() - 1.0)}]
        for constraint in request.linear_constraints:
            values = constraint.values.to_numpy(dtype=float)
            if constraint.lower is not None:
                constraints.append(
                    {
                        "type": "ineq",
                        "fun": lambda w, v=values, lower=constraint.lower: float(w @ v - lower),
                    }
                )
            if constraint.upper is not None:
                constraints.append(
                    {
                        "type": "ineq",
                        "fun": lambda w, v=values, upper=constraint.upper: float(upper - w @ v),
                    }
                )
        bounds = [(request.min_weight, request.max_weight or 1.0)] * count
        solution = minimize(
            objective,
            equal,
            jac=gradient,
            method="SLSQP",
            bounds=bounds,
            constraints=constraints,
            options={
                "maxiter": self.config.max_iterations,
                "ftol": self.config.tolerance,
                "disp": False,
            },
        )
        feasible = bool(
            solution.success
            and np.isfinite(solution.x).all()
            and abs(float(solution.x.sum()) - 1.0) <= 1e-7
            and min(
                _qp_constraint_residuals(solution.x, request.linear_constraints).values(),
                default=0.0,
            )
            >= -1e-7
        )
        fallback = None
        weights = solution.x if feasible else equal
        if not feasible:
            residuals = _qp_constraint_residuals(equal, request.linear_constraints)
            fallback_violations = {
                name: residual for name, residual in residuals.items() if residual < -1e-7
            }
            if equal.min() < request.min_weight - 1e-12:
                fallback_violations["min_weight"] = float(equal.min() - request.min_weight)
            upper_bound = request.max_weight or 1.0
            if equal.max() > upper_bound + 1e-12:
                fallback_violations["max_weight"] = float(upper_bound - equal.max())
            equal_feasible = (
                min(residuals.values(), default=0.0) >= -1e-7
                and equal.min() >= request.min_weight - 1e-12
                and equal.max() <= upper_bound + 1e-12
            )
            if not equal_feasible:
                raise ValueError(
                    "QP solver failed and equal-weight fallback is infeasible: "
                    f"{solution.message}; violated constraints: {fallback_violations}"
                )
            fallback = "equal_weight"

        result = PortfolioOptimizationResult(
            backend_name=self.name,
            weights=pd.Series(weights, index=assets, dtype=float),
            diagnostics={
                "method": "minimum_variance_qp",
                "solver": "scipy_slsqp",
                "solver_status": "optimal" if feasible else "failed",
                "solver_message": str(solution.message),
                "covariance_source": covariance_source,
                "risk_variance": float(weights @ covariance @ weights),
                "anchor_distance_squared": float(np.sum((weights - anchor) ** 2)),
                "previous_distance_squared": float(
                    np.sum((weights - previous) ** 2) if previous is not None else 0.0
                ),
                "constraint_residuals": _qp_constraint_residuals(
                    weights, request.linear_constraints
                ),
                **({"fallback": fallback} if fallback else {}),
            },
        )
        result.validate(request)
        return result


def _validate_json_scalars(value: Any) -> None:
    if value is None or isinstance(value, (str, bool, int)):
        return
    if isinstance(value, (float, np.floating)):
        if not isfinite(float(value)):
            raise ValueError("diagnostics must not contain non-finite numbers")
        return
    if isinstance(value, np.integer):
        return
    if isinstance(value, Mapping):
        for key, item in value.items():
            if not isinstance(key, str):
                raise TypeError("diagnostics mapping keys must be strings")
            _validate_json_scalars(item)
        return
    if isinstance(value, (list, tuple)):
        for item in value:
            _validate_json_scalars(item)
        return
    raise TypeError(f"unsupported optimizer diagnostics value: {type(value).__name__}")


__all__ = [
    "PORTFOLIO_OPTIMIZATION_RESULT_SCHEMA",
    "EqualWeightOptimizerBackend",
    "HrpOptimizerBackend",
    "InverseVolConfig",
    "InverseVolOptimizerBackend",
    "LinearExposureConstraint",
    "OptimizerRegistry",
    "PortfolioOptimizationRequest",
    "PortfolioOptimizationResult",
    "PortfolioOptimizerBackend",
    "PortfolioQpConfig",
    "QpMinVarianceOptimizerBackend",
]
