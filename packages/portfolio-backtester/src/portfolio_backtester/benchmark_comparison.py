"""Metrics and receipts for benchmark-relative portfolio comparisons."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from typing import Any

import numpy as np
import pandas as pd


def _validated_returns(portfolio_returns: pd.Series, benchmark_returns: pd.Series) -> pd.DataFrame:
    if not portfolio_returns.index.equals(benchmark_returns.index):
        raise ValueError("portfolio and benchmark returns must have matching dates")
    frame = pd.concat(
        [portfolio_returns.rename("portfolio"), benchmark_returns.rename("benchmark")], axis=1
    )
    if frame.empty or not np.isfinite(frame.to_numpy(dtype=float)).all():
        raise ValueError("returns must be non-empty and finite")
    return frame


def _validated_weights(weights: pd.Series, benchmark_weights: pd.Series) -> pd.DataFrame:
    frame = pd.concat(
        [weights.rename("portfolio"), benchmark_weights.rename("benchmark")], axis=1
    ).fillna(0.0)
    if frame.empty or not np.isfinite(frame.to_numpy(dtype=float)).all():
        raise ValueError("weights must be non-empty and finite")
    if (frame < 0).any().any():
        raise ValueError("weights must be non-negative")
    if not np.isclose(frame.sum(axis=0).to_numpy(), 1.0).all():
        raise ValueError("weights must sum to one")
    return frame


def _input_hash(returns: pd.DataFrame, weights: pd.DataFrame) -> str:
    payload: Mapping[str, Any] = {
        "returns": returns.reset_index().astype(str).to_dict(orient="records"),
        "weights": weights.reset_index().astype(str).to_dict(orient="records"),
    }
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def compare_portfolio_returns(
    portfolio_returns: pd.Series,
    benchmark_returns: pd.Series,
    weights: pd.Series,
    benchmark_weights: pd.Series,
    previous_weights: pd.Series | None = None,
) -> dict[str, float | str]:
    """Return comparable absolute and active portfolio metrics."""

    returns = _validated_returns(portfolio_returns, benchmark_returns)
    weight_frame = _validated_weights(weights, benchmark_weights)
    excess = returns["portfolio"] - returns["benchmark"]
    tracking_error = float(excess.std(ddof=1) * np.sqrt(252)) if len(excess) > 1 else 0.0
    information_ratio = (
        float(excess.mean() * np.sqrt(252) / tracking_error)
        if tracking_error > 0
        else float("nan")
    )
    if previous_weights is None:
        turnover = 0.0
    else:
        previous = previous_weights.reindex(weight_frame.index).fillna(0.0)
        if (previous < 0).any() or not np.isclose(previous.sum(), 1.0):
            raise ValueError("previous_weights must be non-negative and sum to one")
        turnover = float(0.5 * (weight_frame["portfolio"] - previous).abs().sum())
    return {
        "portfolio_total_return": float((1.0 + returns["portfolio"]).prod() - 1.0),
        "benchmark_total_return": float((1.0 + returns["benchmark"]).prod() - 1.0),
        "excess_total_return": float(
            (1.0 + returns["portfolio"]).prod() / (1.0 + returns["benchmark"]).prod() - 1.0
        ),
        "tracking_error": tracking_error,
        "information_ratio": information_ratio,
        "turnover": turnover,
        "active_share": float(
            0.5 * (weight_frame["portfolio"] - weight_frame["benchmark"]).abs().sum()
        ),
        "input_sha256": _input_hash(returns, weight_frame),
    }


def build_comparison_receipt(
    metrics: Mapping[str, float | str],
    *,
    variant: str,
    rebalance_policy: str,
) -> dict[str, Any]:
    """Wrap metrics in the public research-only comparison receipt."""

    return {
        "schema_version": "portfolio_backtester.benchmark_enhancement_comparison.v1",
        "variant": variant,
        "rebalance_policy": rebalance_policy,
        "input_sha256": metrics["input_sha256"],
        "research_only": True,
        **dict(metrics),
    }


__all__ = ["build_comparison_receipt", "compare_portfolio_returns"]
