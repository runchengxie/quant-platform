"""Deterministic economic rebalancing primitives."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from math import isfinite
from typing import Any

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class EconomicRebalanceResult:
    """Target weights after applying a portfolio-level no-trade threshold."""

    weights: pd.Series
    diagnostics: Mapping[str, Any] = field(default_factory=dict)


def _validate_weights(weights: pd.Series, *, label: str) -> pd.Series:
    if not isinstance(weights, pd.Series):
        raise TypeError(f"{label} must be a pandas Series")
    normalized = pd.to_numeric(weights, errors="coerce").astype(float)
    if normalized.isna().any() or not np.isfinite(normalized.to_numpy(dtype=float)).all():
        raise ValueError(f"{label} must contain finite values")
    if (normalized < 0).any():
        raise ValueError(f"{label} must be non-negative")
    if abs(float(normalized.sum()) - 1.0) > 1e-8:
        raise ValueError(f"{label} must sum to 1")
    return normalized


def apply_no_trade_band(
    target_weights: pd.Series,
    previous_weights: pd.Series | None,
    *,
    min_turnover: float = 0.0,
) -> EconomicRebalanceResult:
    """Keep the previous portfolio when target turnover is not economical.

    ``min_turnover`` is a portfolio-level half-L1 threshold.  The function
    either adopts the complete target or keeps the complete previous portfolio;
    it never silently renormalizes only part of a trade.
    """

    if isinstance(min_turnover, bool) or not isfinite(float(min_turnover)) or min_turnover < 0:
        raise ValueError("min_turnover must be finite and non-negative")
    target = _validate_weights(target_weights, label="target_weights")
    if previous_weights is None:
        return EconomicRebalanceResult(
            weights=target.copy(),
            diagnostics={
                "method": "no_trade_band",
                "min_turnover": float(min_turnover),
                "turnover_before": None,
                "turnover_after": 0.0,
                "traded": True,
                "previous_weights_missing": True,
            },
        )

    previous = _validate_weights(previous_weights, label="previous_weights")
    if set(map(str, target.index)) != set(map(str, previous.index)):
        raise ValueError("target_weights and previous_weights must contain the same assets")
    target.index = target.index.map(str)
    previous.index = previous.index.map(str)
    previous = previous.reindex(target.index)
    turnover_before = 0.5 * float((target - previous).abs().sum())
    traded = turnover_before > float(min_turnover) + 1e-12
    weights = target.copy() if traded else previous.copy()
    turnover_after = turnover_before if traded else 0.0
    return EconomicRebalanceResult(
        weights=weights,
        diagnostics={
            "method": "no_trade_band",
            "min_turnover": float(min_turnover),
            "turnover_before": turnover_before,
            "turnover_after": turnover_after,
            "traded": traded,
            "previous_weights_missing": False,
        },
    )


__all__ = ["EconomicRebalanceResult", "apply_no_trade_band"]
