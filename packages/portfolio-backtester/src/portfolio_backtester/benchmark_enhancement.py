"""Generic benchmark-relative portfolio construction helpers."""

from __future__ import annotations

from enum import StrEnum

import numpy as np
import pandas as pd


class PortfolioConstructionVariant(StrEnum):
    TOPK_EQUAL_WEIGHT = "topk_equal_weight"
    TOPK_BENCHMARK_WEIGHT = "topk_benchmark_weight"
    BENCHMARK_ML_TILT = "benchmark_ml_tilt"


_REQUIRED_COLUMNS = {"symbol", "selection_rank", "ml_score", "benchmark_weight"}


def _validated_frame(frame: pd.DataFrame) -> pd.DataFrame:
    missing = sorted(_REQUIRED_COLUMNS - set(frame.columns))
    if missing:
        raise ValueError("missing required columns: " + ", ".join(missing))
    result = frame.copy()
    result["symbol"] = result["symbol"].astype(str).str.strip()
    if result["symbol"].eq("").any() or result["symbol"].duplicated().any():
        raise ValueError("symbol must be non-empty and unique")
    for column in ("selection_rank", "ml_score", "benchmark_weight"):
        result[column] = pd.to_numeric(result[column], errors="coerce")
        if not np.isfinite(result[column]).all():
            raise ValueError(f"{column} must contain finite values")
    if (result["benchmark_weight"] < 0).any() or result["benchmark_weight"].sum() <= 0:
        raise ValueError("benchmark_weight must be non-negative and have a positive sum")
    return result.sort_values(["selection_rank", "symbol"], kind="mergesort").reset_index(drop=True)


def _topk(frame: pd.DataFrame, top_k: int) -> pd.DataFrame:
    if isinstance(top_k, bool) or top_k < 1:
        raise ValueError("top_k must be a positive integer")
    return frame.head(int(top_k)).copy()


def build_target_weights(
    frame: pd.DataFrame,
    variant: PortfolioConstructionVariant | str,
    *,
    top_k: int = 20,
    tilt_strength: float = 0.0,
) -> pd.Series:
    """Build long-only target weights for a public comparison variant."""

    try:
        normalized_variant = PortfolioConstructionVariant(variant)
    except ValueError as exc:
        raise ValueError(f"unknown portfolio construction variant: {variant}") from exc
    validated = _validated_frame(frame)
    if not np.isfinite(tilt_strength) or tilt_strength < 0:
        raise ValueError("tilt_strength must be finite and non-negative")

    if normalized_variant is PortfolioConstructionVariant.TOPK_EQUAL_WEIGHT:
        selected = _topk(validated, top_k)
        values = pd.Series(1.0 / len(selected), index=selected["symbol"], dtype=float)
    elif normalized_variant is PortfolioConstructionVariant.TOPK_BENCHMARK_WEIGHT:
        selected = _topk(validated, top_k)
        raw = selected.set_index("symbol")["benchmark_weight"]
        values = raw / raw.sum()
    else:
        selected = validated.set_index("symbol")
        scores = selected["ml_score"]
        deviation = scores - scores.mean()
        standard_deviation = float(scores.std(ddof=0))
        zscore = deviation / standard_deviation if standard_deviation > 0 else deviation * 0.0
        raw = selected["benchmark_weight"] * np.exp(float(tilt_strength) * zscore)
        values = raw / raw.sum()

    values.name = "target_weight"
    return values.sort_index()


__all__ = ["PortfolioConstructionVariant", "build_target_weights"]
