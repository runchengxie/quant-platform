"""Conditional associations and explicitly paired model evidence."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from numbers import Integral
from typing import Any

import numpy as np
import pandas as pd

from ._signal_reliability_common import (
    BlockStatistics,
    SignalReliabilityResult,
    correlation,
    finish,
    prepare_panel,
    validate_ks,
)
from ._signal_reliability_tail import ranked, selection


def _paired_identity(
    baseline: str | None,
    augmented: str | None,
    metadata: Mapping[str, Any] | None,
) -> bool:
    if baseline is None and augmented is None:
        if metadata is not None:
            raise ValueError("paired metadata requires both prediction columns")
        return False
    if not baseline or not augmented or not isinstance(metadata, Mapping):
        raise ValueError("both prediction columns and paired provenance are required")
    keys = ("run_id", "label_id", "universe_id", "split_id", "prediction_availability")
    pairs = [metadata.get(name) for name in ("baseline", "augmented")]
    for item in pairs:
        if not isinstance(item, Mapping) or any(
            not isinstance(item.get(key), str) or not item[key].strip() for key in keys
        ):
            raise ValueError("incomplete paired research identity")
    base, aug = pairs
    if any(base[key] != aug[key] for key in keys[1:]):
        raise ValueError("incompatible paired research identities")
    if base["prediction_availability"] != "before_label_start":
        raise ValueError("paired predictions must be declared available before label start")
    description = metadata.get("feature_change")
    if (
        base["run_id"] == aug["run_id"]
        or not isinstance(description, str)
        or not description.strip()
    ):
        raise ValueError("distinct runs and a feature change description are required")
    return True


def _standardize(values: pd.Series) -> np.ndarray:
    std = float(values.std(ddof=0))
    if std <= 1e-12:
        return np.zeros(len(values))
    return ((values - values.mean()) / std).to_numpy(dtype=float)


def _design(
    sample: pd.DataFrame, controls: Sequence[str], industry: str | None, *, rank: bool
) -> np.ndarray:
    columns = [np.ones(len(sample))]
    columns.extend(_standardize(sample[col].rank() if rank else sample[col]) for col in controls)
    if industry:
        dummies = pd.get_dummies(sample[industry], drop_first=True, dtype=float)
        columns.extend(dummies[col].to_numpy() for col in dummies)
    return np.column_stack(columns)


def _controlled_value(
    sample: pd.DataFrame,
    factor: str,
    target: str,
    controls: Sequence[str],
    industry: str | None,
    *,
    rank: bool,
) -> dict[str, Any]:
    x = _design(sample, controls, industry, rank=rank)
    f = _standardize(sample[factor].rank() if rank else sample[factor])
    full = np.column_stack([x, f])
    design_rank = int(np.linalg.matrix_rank(full))
    conditioning = float(np.linalg.cond(full))
    result = {
        "value": np.nan,
        "status": "unidentified",
        "design_rank": design_rank,
        "design_columns": full.shape[1],
        "condition_number": conditioning,
    }
    if len(sample) <= full.shape[1]:
        result["status"] = "insufficient_degrees_of_freedom"
        return result
    if design_rank != full.shape[1] or not np.isfinite(conditioning) or conditioning > 1e10:
        return result
    y = (
        sample[target].rank().to_numpy(dtype=float)
        if rank
        else sample[target].to_numpy(dtype=float)
    )
    residual_f = f - x @ np.linalg.lstsq(x, f, rcond=None)[0]
    if float(np.std(residual_f)) < 1e-8:
        return result
    if rank:
        residual_y = y - x @ np.linalg.lstsq(x, y, rcond=None)[0]
        value = correlation(pd.Series(residual_f), pd.Series(residual_y))
    else:
        value = float(np.linalg.lstsq(full, y, rcond=None)[0][-1])
    result.update(value=value, status="ok" if np.isfinite(value) else "unidentified")
    return result


def _factor_rows(
    group: pd.DataFrame,
    *,
    date: str,
    factor: str,
    target: str,
    controls: Sequence[str],
    industry: str | None,
    min_obs: int,
) -> list[dict[str, Any]]:
    full = group.dropna(subset=[factor, target])
    sample = full.dropna(subset=[*controls, *([industry] if industry else [])])
    common = {
        "date": date,
        "group": f"factor:{factor}",
        "factor": factor,
        "n_universe": len(group),
        "n_obs": len(sample),
        "n_raw_obs": len(full),
    }
    rows = []
    for metric, data in (("raw_full_rank_ic", full), ("raw_rank_ic", sample)):
        value = (
            correlation(data[factor], data[target], rank=True) if len(data) >= min_obs else np.nan
        )
        rows.append(
            common
            | {
                "metric": metric,
                "n_obs": len(data),
                "value": value,
                "status": "ok"
                if np.isfinite(value)
                else "insufficient_observations"
                if len(data) < min_obs
                else "unidentified",
            }
        )
    for metric, rank in (("partial_rank_ic", True), ("conditional_coefficient", False)):
        row = common | {
            "metric": metric,
            "value": np.nan,
            "status": "not_requested",
            "design_rank": np.nan,
            "design_columns": np.nan,
            "condition_number": np.nan,
        }
        if controls or industry:
            if len(sample) < min_obs:
                row["status"] = "insufficient_observations"
            else:
                row.update(_controlled_value(sample, factor, target, controls, industry, rank=rank))
        rows.append(row)
    return rows


def _incremental_rows(
    group: pd.DataFrame,
    *,
    date: str,
    baseline: str,
    augmented: str,
    target: str,
    symbol: str,
    ks: Sequence[int],
    min_obs: int,
    ascending: bool,
) -> list[dict[str, Any]]:
    pairs = group.dropna(subset=[baseline, augmented])
    labelled = pairs.dropna(subset=[target])
    common = {
        "date": date,
        "group": "incremental",
        "n_universe": len(group),
        "n_prediction_pairs": len(pairs),
        "n_obs": len(labelled),
    }
    delta = np.nan
    if len(labelled) >= min_obs:
        delta = correlation(labelled[augmented], labelled[target], rank=True) - correlation(
            labelled[baseline], labelled[target], rank=True
        )
    rows = [
        common
        | {
            "metric": "rank_ic_delta",
            "value": delta,
            "status": "ok"
            if np.isfinite(delta)
            else "insufficient_observations"
            if len(labelled) < min_obs
            else "unidentified",
        }
    ]
    a = ranked(pairs, augmented, symbol, ascending)
    b = ranked(pairs, baseline, symbol, ascending)
    for k in ks:
        top_a, top_b = selection(a, 0, k, target), selection(b, 0, k, target)
        status = (
            "insufficient_scores"
            if len(pairs) < k
            else "missing_labels"
            if top_a["status"] != "ok" or top_b["status"] != "ok"
            else "ok"
        )
        rows.append(
            common
            | {
                "group": f"incremental:top:{k}",
                "metric": "top_return_delta",
                "k": k,
                "status": status,
                "baseline_n_labels": top_b["n_labels"],
                "augmented_n_labels": top_a["n_labels"],
                "value": top_a["value"] - top_b["value"] if status == "ok" else np.nan,
            }
        )
    return rows


def conditional_factor_profile(
    panel: pd.DataFrame,
    *,
    factor_cols: Sequence[str],
    target_col: str,
    control_cols: Sequence[str] = (),
    industry_col: str | None = None,
    statistics: BlockStatistics,
    min_obs: int,
    ks: Sequence[int],
    date_col: str = "trade_date",
    symbol_col: str = "symbol",
    baseline_col: str | None = None,
    augmented_col: str | None = None,
    paired_provenance: Mapping[str, Any] | None = None,
    provenance: Mapping[str, Any] | None = None,
    ascending: bool = False,
) -> SignalReliabilityResult:
    """Raw/partial rank IC, standardized conditional slope and optional paired OOS deltas."""
    if isinstance(factor_cols, str) or not factor_cols or isinstance(control_cols, str):
        raise ValueError("factor_cols/control_cols must be column sequences; at least one factor")
    if isinstance(min_obs, bool) or not isinstance(min_obs, Integral) or min_obs < 3:
        raise ValueError("min_obs must be an integer of at least three")
    if not isinstance(ascending, bool):
        raise ValueError("ascending must be a boolean")
    widths = validate_ks(ks)
    paired = _paired_identity(baseline_col, augmented_col, paired_provenance)
    numeric = [*factor_cols, target_col, *control_cols]
    if paired:
        numeric.extend([baseline_col, augmented_col])
    frame = prepare_panel(
        panel,
        date_col=date_col,
        symbol_col=symbol_col,
        numeric_cols=numeric,
        category_cols=[industry_col] if industry_col else [],
        statistics=statistics,
    )
    rows = []
    for date, group in frame.groupby(date_col, sort=True):
        day = date.strftime("%Y-%m-%d")
        for factor in factor_cols:
            rows.extend(
                _factor_rows(
                    group,
                    date=day,
                    factor=factor,
                    target=target_col,
                    controls=control_cols,
                    industry=industry_col,
                    min_obs=min_obs,
                )
            )
        if paired:
            rows.extend(
                _incremental_rows(
                    group,
                    date=day,
                    baseline=baseline_col,
                    augmented=augmented_col,
                    target=target_col,
                    symbol=symbol_col,
                    ks=widths,
                    min_obs=min_obs,
                    ascending=ascending,
                )
            )
    return finish(
        frame,
        rows,
        kind="conditional_factor_profile",
        date_col=date_col,
        settings=statistics,
        provenance=provenance,
        definitions={
            "factor_cols": list(factor_cols),
            "target_col": target_col,
            "control_cols": list(control_cols),
            "industry_col": industry_col,
            "date_col": date_col,
            "symbol_col": symbol_col,
            "min_obs": min_obs,
            "ks": list(widths),
            "ascending": ascending,
            "baseline_col": baseline_col,
            "augmented_col": augmented_col,
            "coefficient_units": "return_per_factor_std_ddof0",
            "partial_ic": "Pearson of residualized ranks; ranked numeric controls",
        },
        extra={
            "incremental_status": "provided_declared_oos" if paired else "not_provided",
            "paired_provenance": dict(paired_provenance or {}),
        },
    )
