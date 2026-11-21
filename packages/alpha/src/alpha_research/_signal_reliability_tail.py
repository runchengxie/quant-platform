"""Ranked selections never use labels to decide membership."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any, cast

import numpy as np
import pandas as pd

from ._signal_reliability_common import (
    BlockStatistics,
    SignalReliabilityResult,
    finish,
    prepare_panel,
    validate_ks,
)


def selection(group: pd.DataFrame, start: int, end: int, target: str) -> dict[str, Any]:
    selected = group.iloc[start:end]
    n_labels = int(selected[target].notna().sum())
    status = (
        "insufficient_scores"
        if len(selected) != end - start
        else "missing_labels"
        if n_labels != len(selected)
        else "ok"
    )
    return {
        "requested_count": end - start,
        "actual_count": len(selected),
        "n_labels": n_labels,
        "status": status,
        "value": float(selected[target].mean()) if status == "ok" else np.nan,
    }


def ranked(group: pd.DataFrame, score: str, symbol: str, ascending: bool) -> pd.DataFrame:
    return group.loc[group[score].notna()].sort_values([score, symbol], ascending=[ascending, True])


def compute_tail(
    panel: pd.DataFrame,
    *,
    score_col: str,
    target_col: str,
    ks: Sequence[int],
    statistics: BlockStatistics,
    date_col: str = "trade_date",
    symbol_col: str = "symbol",
    ascending: bool = False,
    provenance: Mapping[str, Any] | None = None,
    marginal: bool = False,
) -> SignalReliabilityResult:
    widths = validate_ks(ks)
    if not isinstance(ascending, bool):
        raise ValueError("ascending must be a boolean")
    frame = prepare_panel(
        panel,
        date_col=date_col,
        symbol_col=symbol_col,
        numeric_cols=[score_col, target_col],
        statistics=statistics,
    )
    rows, tied = [], 0
    for date, original in frame.groupby(date_col, sort=True):
        group = ranked(original, score_col, symbol_col, ascending)
        tied += int(group[score_col].duplicated(keep=False).sum())
        start = 0
        for k in widths:
            common = {
                "date": cast(pd.Timestamp, date).strftime("%Y-%m-%d"),
                "k": k,
                "n_universe": len(original),
                "n_scores": len(group),
            }
            top = selection(group, 0, k, target_col)
            if marginal:
                nxt = selection(group, k, 2 * k, target_col)
                status = (
                    "insufficient_scores"
                    if len(group) < 2 * k
                    else "missing_labels"
                    if top["status"] != "ok" or nxt["status"] != "ok"
                    else "ok"
                )
                spread = top["value"] - nxt["value"] if status == "ok" else np.nan
                for label, value in (("top_minus_next", spread), ("top_minus_2k", spread / 2)):
                    rows.append(
                        common
                        | {
                            "group": f"{label}:{k}",
                            "metric": "return_spread",
                            "status": status,
                            "value": value,
                            "requested_count": 2 * k,
                            "actual_count": min(len(group), 2 * k),
                            "n_labels": top["n_labels"] + nxt["n_labels"],
                        }
                    )
            else:
                rows.append(
                    common
                    | {"group": f"band:{start + 1}:{k}", "metric": "label_return"}
                    | selection(group, start, k, target_col)
                )
                rows.append(common | {"group": f"top:{k}", "metric": "label_return"} | top)
            start = k
    return finish(
        frame,
        rows,
        kind="marginal_alpha_profile" if marginal else "tail_return_profile",
        date_col=date_col,
        settings=statistics,
        provenance=provenance,
        definitions={
            "score_col": score_col,
            "target_col": target_col,
            "date_col": date_col,
            "symbol_col": symbol_col,
            "ks": list(widths),
            "ascending": ascending,
            "label_units": "decimal_returns",
            "weighting": "equal_stock_then_equal_date",
        },
        extra={"tied_score_rows": tied},
    )
