"""Strategy-agnostic Barra-like risk model primitives.

The functions in this module operate on already-built, point-in-time exposure
and return panels.  They intentionally do not know how an exposure was built
or where market data came from; those responsibilities belong to callers in
the appropriate research/data layer.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final

import numpy as np
import pandas as pd

_EXPOSURE_INDEX_NAMES: Final[tuple[str, str]] = ("as_of_date", "symbol")
_RETURN_COLUMN: Final[str] = "total_return"


@dataclass(frozen=True)
class RiskModelConfig:
    """Numerical and minimum-data settings for the risk model."""

    periods_per_year: float = 252.0
    min_cross_section: int = 3
    ridge: float = 1e-10
    covariance_window: int = 252
    ewma_halflife: float = 60.0
    covariance_shrinkage: float = 0.10

    def __post_init__(self) -> None:
        if self.periods_per_year <= 0:
            raise ValueError("periods_per_year must be positive")
        if self.min_cross_section < 1:
            raise ValueError("min_cross_section must be at least one")
        if self.ridge < 0:
            raise ValueError("ridge must be nonnegative")
        if self.covariance_window < 2:
            raise ValueError("covariance_window must be at least two")
        if self.ewma_halflife <= 0:
            raise ValueError("ewma_halflife must be positive")
        if not 0 <= self.covariance_shrinkage <= 1:
            raise ValueError("covariance_shrinkage must be between zero and one")


@dataclass(frozen=True)
class FactorReturnResult:
    """Daily factor returns, fitted asset returns, and regression diagnostics."""

    factor_returns: pd.DataFrame
    residual_returns: pd.DataFrame
    diagnostics: pd.DataFrame


@dataclass(frozen=True)
class RiskModelResult:
    """Estimated factor covariance and asset-specific risk."""

    factor_returns: pd.DataFrame
    factor_covariance: pd.DataFrame
    specific_variance: pd.Series
    diagnostics: pd.DataFrame


@dataclass(frozen=True)
class PortfolioRiskAttribution:
    """Factor and specific variance attribution for one portfolio snapshot."""

    portfolio_exposure: pd.Series
    factor_contribution: pd.Series
    specific_variance: float
    total_variance: float
    total_volatility: float


def _validate_exposure_frame(exposures: pd.DataFrame) -> None:
    if not isinstance(exposures, pd.DataFrame):
        raise TypeError("exposures must be a pandas DataFrame")
    if not isinstance(exposures.index, pd.MultiIndex):
        raise ValueError("exposures must use a MultiIndex")
    if tuple(exposures.index.names) != _EXPOSURE_INDEX_NAMES:
        raise ValueError(
            "exposures index names must be ('as_of_date', 'symbol'), "
            f"got {exposures.index.names!r}"
        )
    if exposures.index.has_duplicates:
        raise ValueError("exposures contains duplicate (as_of_date, symbol) keys")
    if exposures.shape[1] == 0:
        raise ValueError("exposures must contain at least one factor column")
    for column in exposures.columns:
        if not pd.api.types.is_numeric_dtype(exposures[column]):
            raise ValueError(f"exposure column {column!r} must be numeric")


def _as_return_series(returns: pd.Series | pd.DataFrame) -> pd.Series:
    if isinstance(returns, pd.DataFrame):
        if list(returns.columns) != [_RETURN_COLUMN]:
            raise ValueError("returns DataFrame must contain exactly 'total_return'")
        returns = returns[_RETURN_COLUMN]
    if not isinstance(returns, pd.Series):
        raise TypeError("returns must be a Series or one-column DataFrame")
    if not isinstance(returns.index, pd.MultiIndex):
        raise ValueError("returns must use a MultiIndex")
    if tuple(returns.index.names) != _EXPOSURE_INDEX_NAMES:
        raise ValueError(
            "returns index names must be ('as_of_date', 'symbol'), "
            f"got {returns.index.names!r}"
        )
    if returns.index.has_duplicates:
        raise ValueError("returns contains duplicate (as_of_date, symbol) keys")
    if not pd.api.types.is_numeric_dtype(returns):
        raise ValueError("returns must be numeric")
    return returns.rename(_RETURN_COLUMN)


def validate_risk_inputs(
    exposures: pd.DataFrame,
    returns: pd.Series | pd.DataFrame,
    *,
    config: RiskModelConfig | None = None,
) -> None:
    """Validate canonical point-in-time exposure and return panels.

    Exposure values may be missing because a factor is unavailable for an
    asset/date. Returns are different: a non-finite return is an invalid input
    and must be fixed or excluded by the data owner before estimation.
    """

    config = config or RiskModelConfig()
    _validate_exposure_frame(exposures)
    return_series = _as_return_series(returns)
    if not np.isfinite(return_series.to_numpy(dtype=float)).all():
        raise ValueError("returns contains non-finite values")
    common = exposures.index.intersection(return_series.index)
    if common.empty:
        raise ValueError("exposures and returns have no common asset/date keys")
    counts = common.to_frame(index=False).groupby("as_of_date").size()
    if counts.max() < config.min_cross_section:
        raise ValueError(
            "no date meets min_cross_section="
            f"{config.min_cross_section}; maximum is {int(counts.max())}"
        )


def _validate_estimation_weights(weights: pd.Series | None, index: pd.Index) -> pd.Series:
    if weights is None:
        return pd.Series(1.0, index=index, dtype=float)
    if not isinstance(weights, pd.Series):
        raise TypeError("weights must be a pandas Series")
    if weights.index.has_duplicates:
        raise ValueError("weights contains duplicate keys")
    aligned = weights.reindex(index)
    if aligned.isna().any() or not np.isfinite(aligned.to_numpy(dtype=float)).all():
        raise ValueError("weights must cover all return keys with finite values")
    if (aligned < 0).any() or float(aligned.sum()) <= 0:
        raise ValueError("weights must be nonnegative with a positive total")
    return aligned.astype(float)


def _weighted_regression(
    design: np.ndarray,
    target: np.ndarray,
    weights: np.ndarray,
    ridge: float,
) -> tuple[np.ndarray, int, float]:
    root_weights = np.sqrt(weights)
    weighted_design = design * root_weights[:, None]
    weighted_target = target * root_weights
    gram = weighted_design.T @ weighted_design
    if ridge:
        gram = gram + ridge * np.eye(design.shape[1])
    rhs = weighted_design.T @ weighted_target
    try:
        coefficients = np.linalg.solve(gram, rhs)
    except np.linalg.LinAlgError:
        coefficients = np.linalg.lstsq(weighted_design, weighted_target, rcond=None)[0]
    rank = int(np.linalg.matrix_rank(weighted_design))
    condition_number = float(np.linalg.cond(weighted_design))
    return coefficients, rank, condition_number


def estimate_factor_returns(
    exposures: pd.DataFrame,
    returns: pd.Series | pd.DataFrame,
    *,
    weights: pd.Series | None = None,
    config: RiskModelConfig | None = None,
) -> FactorReturnResult:
    """Estimate daily factor returns by weighted cross-sectional regression.

    The caller controls the model specification through the exposure columns.
    If an intercept is desired, provide an ``intercept`` exposure column; no
    intercept is implicitly added.
    """

    config = config or RiskModelConfig()
    validate_risk_inputs(exposures, returns, config=config)
    return_series = _as_return_series(returns)
    estimation_weights = _validate_estimation_weights(weights, return_series.index)
    factors = list(exposures.columns)
    dates = pd.Index(sorted(set(exposures.index.get_level_values("as_of_date"))))
    factor_rows: list[pd.Series] = []
    diagnostic_rows: list[dict[str, object]] = []
    total_return_values = return_series.to_numpy(dtype=float)
    fitted_values = np.full(len(return_series), np.nan, dtype=float)
    residual_values = np.full(len(return_series), np.nan, dtype=float)

    for date in dates:
        exposure_day = exposures.xs(date, level="as_of_date")
        return_day = return_series.xs(date, level="as_of_date")
        weight_day = estimation_weights.xs(date, level="as_of_date")
        joined = exposure_day.join(return_day.rename(_RETURN_COLUMN), how="inner").join(
            weight_day.rename("regression_weight"), how="inner"
        )
        joined = joined.dropna(subset=[*factors, _RETURN_COLUMN, "regression_weight"])
        n_observations = len(joined)
        diagnostic: dict[str, object] = {
            "as_of_date": date,
            "n_observations": n_observations,
            "rank": 0,
            "condition_number": np.nan,
            "weighted_r2": np.nan,
            "status": "ok",
        }
        if n_observations < config.min_cross_section:
            diagnostic["status"] = "insufficient_cross_section"
            diagnostic_rows.append(diagnostic)
            continue

        design = joined[factors].to_numpy(dtype=float)
        target = joined[_RETURN_COLUMN].to_numpy(dtype=float)
        observation_weights = joined["regression_weight"].to_numpy(dtype=float)
        coefficients, rank, condition_number = _weighted_regression(
            design, target, observation_weights, config.ridge
        )
        fitted = design @ coefficients
        joined_index = pd.MultiIndex.from_arrays(
            [np.repeat(date, len(joined)), joined.index],
            names=_EXPOSURE_INDEX_NAMES,
        )
        positions = return_series.index.get_indexer(joined_index)
        if (positions < 0).any():
            raise RuntimeError("factor regression produced an unknown return index")
        fitted_values[positions] = fitted
        residual_values[positions] = target - fitted
        weighted_mean = float(np.average(target, weights=observation_weights))
        weighted_sst = float(np.sum(observation_weights * (target - weighted_mean) ** 2))
        weighted_sse = float(np.sum(observation_weights * (target - fitted) ** 2))
        diagnostic.update(
            rank=rank,
            condition_number=condition_number,
            weighted_r2=(1.0 - weighted_sse / weighted_sst) if weighted_sst > 0 else np.nan,
        )
        factor_rows.append(pd.Series(coefficients, index=factors, name=date))
        diagnostic_rows.append(diagnostic)

    residual = pd.DataFrame(
        {
            "total_return": total_return_values,
            "fitted_return": fitted_values,
            "residual_return": residual_values,
        },
        index=return_series.index,
    )
    factor_returns = pd.DataFrame(factor_rows, columns=factors)
    factor_returns.index.name = "as_of_date"
    diagnostics = pd.DataFrame(diagnostic_rows).set_index("as_of_date")
    diagnostics.index.name = "as_of_date"
    residual.index.names = list(_EXPOSURE_INDEX_NAMES)
    return FactorReturnResult(factor_returns, residual, diagnostics)


def _ewma_weights(length: int, halflife: float) -> np.ndarray:
    ages = np.arange(length - 1, -1, -1, dtype=float)
    weights = np.exp(-np.log(2.0) * ages / halflife)
    return weights / weights.sum()


def _weighted_covariance(values: np.ndarray, weights: np.ndarray) -> np.ndarray:
    mean = np.average(values, axis=0, weights=weights)
    centered = values - mean
    denominator = 1.0 - float(np.square(weights).sum())
    if denominator <= 0:
        denominator = 1.0
    return (centered * weights[:, None]).T @ centered / denominator


def _nearest_psd(matrix: np.ndarray) -> tuple[np.ndarray, float, float]:
    symmetric = (matrix + matrix.T) / 2.0
    eigenvalues, eigenvectors = np.linalg.eigh(symmetric)
    minimum_before = float(eigenvalues.min())
    clipped = np.clip(eigenvalues, 0.0, None)
    stabilized = (eigenvectors * clipped) @ eigenvectors.T
    stabilized = (stabilized + stabilized.T) / 2.0
    return stabilized, minimum_before, float(np.linalg.eigvalsh(stabilized).min())


def build_risk_model(
    factor_returns: pd.DataFrame,
    residual_returns: pd.DataFrame,
    *,
    config: RiskModelConfig | None = None,
) -> RiskModelResult:
    """Build EWMA factor covariance and specific variances."""

    config = config or RiskModelConfig()
    if not isinstance(factor_returns, pd.DataFrame) or factor_returns.empty:
        raise ValueError("factor_returns must be a non-empty DataFrame")
    if factor_returns.columns.empty or not all(
        pd.api.types.is_numeric_dtype(factor_returns[column]) for column in factor_returns.columns
    ):
        raise ValueError("factor_returns columns must be numeric")
    factor_frame = factor_returns.loc[:, list(factor_returns.columns)].dropna(how="any")
    factor_frame = factor_frame.tail(config.covariance_window)
    if len(factor_frame) < 2:
        raise ValueError("at least two complete factor-return observations are required")
    factor_weights = _ewma_weights(len(factor_frame), config.ewma_halflife)
    covariance = _weighted_covariance(factor_frame.to_numpy(dtype=float), factor_weights)
    average_variance = float(np.trace(covariance) / covariance.shape[0])
    target = np.eye(covariance.shape[0]) * average_variance
    covariance = (1.0 - config.covariance_shrinkage) * covariance + (
        config.covariance_shrinkage * target
    )
    covariance, minimum_before, minimum_after = _nearest_psd(covariance)
    factor_covariance = pd.DataFrame(
        covariance, index=factor_frame.columns, columns=factor_frame.columns
    )

    if not isinstance(residual_returns, pd.DataFrame) or "residual_return" not in residual_returns:
        raise ValueError("residual_returns must contain a 'residual_return' column")
    residual_frame = residual_returns[["residual_return"]].copy()
    if (
        not isinstance(residual_frame.index, pd.MultiIndex)
        or tuple(residual_frame.index.names) != _EXPOSURE_INDEX_NAMES
    ):
        raise ValueError("residual_returns must use a ('as_of_date', 'symbol') MultiIndex")
    specific_values: dict[object, float] = {}
    observation_counts: dict[object, int] = {}
    for symbol, symbol_frame in residual_frame.groupby(level="symbol", sort=True):
        values = symbol_frame["residual_return"].dropna().tail(config.covariance_window)
        observation_counts[symbol] = len(values)
        if len(values) < 2:
            specific_values[symbol] = np.nan
            continue
        weights_for_symbol = _ewma_weights(len(values), config.ewma_halflife)
        specific_values[symbol] = float(
            _weighted_covariance(
                values.to_numpy(dtype=float).reshape(-1, 1), weights_for_symbol
            )[0, 0]
        )
    specific_variance = pd.Series(specific_values, dtype=float, name="specific_variance")
    diagnostics = pd.DataFrame(
        {
            "factor_observations": len(factor_frame),
            "effective_factor_observations": 1.0 / float(np.square(factor_weights).sum()),
            "covariance_shrinkage": config.covariance_shrinkage,
            "minimum_eigenvalue_before_psd": minimum_before,
            "minimum_eigenvalue_after_psd": minimum_after,
        },
        index=["model"],
    )
    diagnostics["specific_observations"] = pd.Series(observation_counts).sum()
    return RiskModelResult(factor_frame, factor_covariance, specific_variance, diagnostics)


def _snapshot_exposures(exposures: pd.DataFrame) -> pd.DataFrame:
    if isinstance(exposures.index, pd.MultiIndex):
        _validate_exposure_frame(exposures)
        dates = exposures.index.get_level_values("as_of_date").unique()
        if len(dates) != 1:
            raise ValueError("portfolio attribution requires exposures for exactly one date")
        return exposures.droplevel("as_of_date")
    if exposures.index.name != "symbol":
        raise ValueError("snapshot exposures must be indexed by 'symbol'")
    if exposures.index.has_duplicates:
        raise ValueError("snapshot exposures contains duplicate symbols")
    if exposures.empty:
        raise ValueError("snapshot exposures cannot be empty")
    for column in exposures.columns:
        if not pd.api.types.is_numeric_dtype(exposures[column]):
            raise ValueError(f"exposure column {column!r} must be numeric")
    return exposures


def _prepare_attribution_inputs(  # noqa: C901
    weights: pd.Series,
    exposures: pd.DataFrame,
    factor_covariance: pd.DataFrame,
    specific_variance: pd.Series,
) -> tuple[pd.Series, pd.DataFrame, pd.DataFrame, pd.Series]:
    if not isinstance(weights, pd.Series) or weights.index.has_duplicates:
        raise ValueError("weights must be a Series with unique symbol index")
    if not np.isfinite(weights.to_numpy(dtype=float)).all():
        raise ValueError("weights must be finite")
    snapshot = _snapshot_exposures(exposures)
    if not isinstance(factor_covariance, pd.DataFrame) or (
        factor_covariance.index.tolist() != factor_covariance.columns.tolist()
    ):
        raise ValueError("factor_covariance must be a square DataFrame with matching labels")
    if not np.isfinite(factor_covariance.to_numpy(dtype=float)).all():
        raise ValueError("factor_covariance must be finite")
    if not np.allclose(factor_covariance, factor_covariance.T):
        raise ValueError("factor_covariance must be symmetric")
    factors = list(factor_covariance.index)
    if list(snapshot.columns) != factors:
        raise ValueError("exposure factor columns must exactly match covariance labels")
    missing = weights.index.difference(snapshot.index)
    if not missing.empty:
        raise ValueError(f"missing exposures for symbols: {missing.tolist()}")
    missing_specific = weights.index.difference(specific_variance.index)
    if not missing_specific.empty:
        raise ValueError(f"missing specific variance for symbols: {missing_specific.tolist()}")
    specific = specific_variance.reindex(weights.index).astype(float)
    if specific.isna().any() or (specific < 0).any() or not np.isfinite(specific).all():
        raise ValueError("specific variances must be finite and nonnegative")
    exposure_matrix = snapshot.reindex(weights.index).to_numpy(dtype=float)
    if not np.isfinite(exposure_matrix).all():
        raise ValueError("portfolio exposures must be finite")
    return weights, snapshot, factor_covariance, specific


def attribute_portfolio_risk(
    weights: pd.Series,
    exposures: pd.DataFrame,
    factor_covariance: pd.DataFrame,
    specific_variance: pd.Series,
) -> PortfolioRiskAttribution:
    """Calculate factor exposure, variance contributions, and total volatility."""

    weights, snapshot, factor_covariance, specific = _prepare_attribution_inputs(
        weights, exposures, factor_covariance, specific_variance
    )
    factors = list(factor_covariance.index)
    exposure_matrix = snapshot.reindex(weights.index).to_numpy(dtype=float)
    weight_values = weights.to_numpy(dtype=float)
    portfolio_exposure = pd.Series(
        exposure_matrix.T @ weight_values, index=factors, name="portfolio_exposure"
    )
    covariance_values = factor_covariance.to_numpy(dtype=float)
    portfolio_factor_exposure = portfolio_exposure.to_numpy()
    factor_variance = float(
        portfolio_factor_exposure @ covariance_values @ portfolio_factor_exposure
    )
    factor_contribution = pd.Series(
        portfolio_factor_exposure * (covariance_values @ portfolio_factor_exposure),
        index=factors,
        name="factor_contribution",
    )
    specific_value = float(np.sum(np.square(weight_values) * specific.to_numpy()))
    total_variance = max(0.0, factor_variance + specific_value)
    return PortfolioRiskAttribution(
        portfolio_exposure,
        factor_contribution,
        specific_value,
        total_variance,
        float(np.sqrt(total_variance)),
    )


__all__ = [
    "FactorReturnResult",
    "PortfolioRiskAttribution",
    "RiskModelConfig",
    "RiskModelResult",
    "attribute_portfolio_risk",
    "build_risk_model",
    "estimate_factor_returns",
    "validate_risk_inputs",
]
