"""Descriptive interaction evidence; double sorts do not establish causal effects."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from ._composition_static import validate_panel


@dataclass(frozen=True)
class DoubleSortResult:
    cells: pd.DataFrame
    by_date: pd.DataFrame


def double_sort_profile(
    frame: pd.DataFrame,
    labels: pd.Series,
    *,
    quality: str,
    value: str,
    bins: int = 5,
    min_cell: int = 5,
) -> DoubleSortResult:
    """Independent rank buckets and extreme-cell difference in differences.

    Average ranks keep ties together. Empty or undersized extreme cells yield
    a missing spread. The caller must restrict outcomes to its evaluation window
    and availability cutoff; these are forward-return diagnostics, not signals.
    """
    validate_panel(frame, (quality, value))
    if quality == value or not labels.index.equals(frame.index):
        raise ValueError("distinct factors and exactly aligned labels are required")
    if isinstance(bins, bool) or not isinstance(bins, int) or bins < 2:
        raise ValueError("bins must be an integer >= 2")
    if isinstance(min_cell, bool) or not isinstance(min_cell, int) or min_cell < 1:
        raise ValueError("min_cell must be a positive integer")
    if (
        not pd.api.types.is_numeric_dtype(labels.dtype)
        or np.isinf(labels.to_numpy(dtype=float)).any()
    ):
        raise ValueError("labels must be numeric and finite or missing")
    cells, dates = [], []
    for date, cross in frame.groupby(level="date", sort=True):
        ranks = cross[[quality, value]].rank(method="average", pct=True)
        buckets = (np.ceil(ranks * bins) - 1).clip(0, bins - 1)
        work = pd.DataFrame(
            {
                "quality_bucket": buckets[quality],
                "value_bucket": buckets[value],
                "future_return": labels.reindex(cross.index),
            }
        ).dropna()
        grouped = work.groupby(["quality_bucket", "value_bucket"]).future_return.agg(
            ["mean", "count"]
        )
        cells.extend(
            {
                "date": date,
                "quality_bucket": int(q),
                "value_bucket": int(v),
                "mean_return": row["mean"],
                "observations": int(row["count"]),
            }
            for (q, v), row in grouped.iterrows()
        )
        extremes = [(bins - 1, bins - 1), (bins - 1, 0), (0, bins - 1), (0, 0)]
        usable = all(
            key in grouped.index and grouped.loc[key, "count"] >= min_cell for key in extremes
        )
        means = [grouped.loc[key, "mean"] for key in extremes] if usable else [np.nan] * 4
        dates.append(
            {
                "date": date,
                "interaction_spread": means[0] - means[1] - means[2] + means[3],
                "complete_extremes": usable,
            }
        )
    return DoubleSortResult(
        pd.DataFrame(
            cells, columns=["date", "quality_bucket", "value_bucket", "mean_return", "observations"]
        ),
        pd.DataFrame(dates, columns=["date", "interaction_spread", "complete_extremes"]),
    )
