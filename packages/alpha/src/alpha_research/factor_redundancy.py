"""Same-date signal overlap; no inference of economic independence or trial count."""

from __future__ import annotations

from itertools import combinations
from math import ceil

import numpy as np
import pandas as pd


def _tail(values: pd.Series, fraction: float, *, upper: bool) -> set:
    count = max(1, ceil(len(values) * fraction))
    cutoff = values.nlargest(count).iloc[-1] if upper else values.nsmallest(count).iloc[-1]
    return set(values.index[values.ge(cutoff) if upper else values.le(cutoff)])


def _jaccard(left: set, right: set) -> float:
    union = left | right
    return len(left & right) / len(union) if union else np.nan


def factor_redundancy(
    scores: pd.DataFrame, *, top_fraction: float, min_cross_section: int
) -> dict[str, pd.DataFrame]:
    """Compare numeric signals on aligned date/symbol observations.

    Pair statistics use pairwise complete rows; rank uses complete rows across
    ALL columns and a Spearman PSD matrix. Ties stay together. Missing/constant
    signals are disclosed, never imputed. Neither rank nor overlap measures
    incremental portfolio returns, leave-one-out refits or statistical trials.
    """
    data = _validated_scores(scores, top_fraction, min_cross_section)
    pairs, coverage, ranks = [], [], []
    for date, cross in data.groupby(level="date", sort=True):
        cross = cross.droplevel("date")
        for factor in cross:
            count = int(cross[factor].notna().sum())
            coverage.append(
                {
                    "date": date,
                    "factor": factor,
                    "observed": count,
                    "universe_rows": len(cross),
                    "coverage": count / len(cross),
                }
            )
        for left, right in combinations(cross.columns, 2):
            pair = cross[[left, right]].dropna()
            row = {
                "date": date,
                "left": left,
                "right": right,
                "observations": len(pair),
                "spearman": np.nan,
                "top_jaccard": np.nan,
                "bottom_jaccard": np.nan,
                "top_bottom_jaccard": np.nan,
                "top_size_left": 0,
                "top_size_right": 0,
                "bottom_size_left": 0,
                "bottom_size_right": 0,
                "status": "insufficient_sample",
            }
            if len(pair) >= min_cross_section:
                if pair.nunique().min() < 2:
                    row["status"] = "constant_signal"
                else:
                    lt, rt = (_tail(pair[c], top_fraction, upper=True) for c in (left, right))
                    lb, rb = (_tail(pair[c], top_fraction, upper=False) for c in (left, right))
                    row.update(
                        spearman=pair[left].corr(pair[right], method="spearman"),
                        top_jaccard=_jaccard(lt, rt),
                        bottom_jaccard=_jaccard(lb, rb),
                        top_bottom_jaccard=_jaccard(lt, rb),
                        top_size_left=len(lt),
                        top_size_right=len(rt),
                        bottom_size_left=len(lb),
                        bottom_size_right=len(rb),
                        status="ok",
                    )
            pairs.append(row)
        common = cross.dropna()
        rank = {
            "date": date,
            "common_observations": len(common),
            "factors": len(cross.columns),
            "participation_ratio": np.nan,
            "status": "insufficient_common_sample",
        }
        if len(common) >= min_cross_section:
            if common.nunique().min() < 2:
                rank["status"] = "constant_signal"
            else:
                eigenvalues = np.linalg.eigvalsh(common.corr(method="spearman").to_numpy())
                if eigenvalues.min() < -1e-10:
                    rank["status"] = "non_psd"
                else:
                    eigenvalues = np.maximum(eigenvalues, 0)
                    rank.update(
                        participation_ratio=float(
                            eigenvalues.sum() ** 2 / np.square(eigenvalues).sum()
                        ),
                        status="ok",
                    )
        ranks.append(rank)
    return {
        "pairs": pd.DataFrame(pairs),
        "coverage": pd.DataFrame(coverage),
        "rank": pd.DataFrame(ranks),
    }


def _validated_scores(scores, top_fraction, min_cross_section):
    if (
        not isinstance(scores.index, pd.MultiIndex)
        or scores.index.nlevels != 2
        or set(scores.index.names) != {"date", "symbol"}
        or scores.index.has_duplicates
        or scores.index.to_frame(index=False).isna().any().any()
    ):
        raise ValueError("unique nonmissing date/symbol MultiIndex required")
    if not isinstance(scores.index.get_level_values("date"), pd.DatetimeIndex):
        raise ValueError("date level must contain timestamps")
    if (
        scores.empty
        or len(scores.columns) < 2
        or scores.columns.has_duplicates
        or any(not isinstance(c, str) or not c for c in scores.columns)
    ):
        raise ValueError("nonempty scores with at least two unique named factors required")
    if (
        isinstance(top_fraction, bool)
        or not np.isfinite(top_fraction)
        or not 0 < top_fraction <= 0.5
    ):
        raise ValueError("top_fraction must lie in (0, 0.5]")
    if type(min_cross_section) is not int or min_cross_section < 3:
        raise ValueError("min_cross_section must be an integer at least three")
    if any(not pd.api.types.is_numeric_dtype(scores[c]) for c in scores):
        raise ValueError("numeric scores required")
    data = scores.astype(float)
    if np.isinf(data.to_numpy()).any():
        raise ValueError("infinite scores are invalid")
    return data
