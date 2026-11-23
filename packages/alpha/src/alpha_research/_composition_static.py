"""Cross-sectional transforms and deterministic composition operators."""

from __future__ import annotations

import numpy as np
import pandas as pd

from .factor_composition_spec import FactorCompositionSpec


def validate_panel(frame: pd.DataFrame, aliases: tuple[str, ...]) -> None:
    if (
        not isinstance(frame.index, pd.MultiIndex)
        or frame.index.nlevels != 2
        or set(frame.index.names) != {"date", "symbol"}
    ):
        raise ValueError("frame requires a (date, symbol) MultiIndex")
    if not frame.index.is_unique or not frame.columns.is_unique:
        raise ValueError("frame rows and columns must be unique")
    dates = frame.index.get_level_values("date")
    if not isinstance(dates, pd.DatetimeIndex) or dates.hasnans:
        raise ValueError("date index must contain valid pandas timestamps")
    if frame.index.get_level_values("symbol").isna().any():
        raise ValueError("symbol index cannot be missing")
    if not set(aliases) <= set(frame.columns):
        raise ValueError("missing required input columns")
    values = frame.loc[:, list(aliases)]
    if any(pd.api.types.is_complex_dtype(dtype) for dtype in values.dtypes):
        raise ValueError("factor values must be real")
    if any(not pd.api.types.is_numeric_dtype(dtype) for dtype in values.dtypes):
        raise ValueError("factor values must be numeric")
    if np.isinf(values.to_numpy(dtype=float, na_value=np.nan)).any():
        raise ValueError("factor values must be finite or missing")


def preprocess(frame: pd.DataFrame, spec: FactorCompositionSpec) -> pd.DataFrame:
    values = frame.loc[:, list(spec.aliases)].astype(float).copy()
    if spec.missing_policy == "error" and values.isna().any().any():
        raise ValueError("missing factor values")
    values *= [item.direction for item in spec.inputs]
    mode = "rank" if spec.method == "rank" else spec.normalization
    grouped = values.groupby(level="date", sort=False)
    if mode == "rank":
        values = grouped.rank(method="average", pct=True)
    elif mode == "zscore":
        mean = grouped.transform("mean")
        std = grouped.transform(lambda x: x.std(ddof=0))
        values = (values - mean) / std.replace(0.0, 1.0)
    return values


def static_compose(values: pd.DataFrame, spec: FactorCompositionSpec):
    aliases = list(spec.aliases)
    weights = pd.Series(dict(spec.weights) or dict.fromkeys(aliases, 1.0 / len(aliases)))
    transformed = values.copy()
    if spec.method == "hierarchical":
        weights = pd.Series(
            {
                alias: 1.0 / len(spec.groups) / len(members)
                for members in spec.groups.values()
                for alias in members
            }
        )
    if spec.method == "residualized":
        # All regressions refer to the original transformed inputs; mapping order is irrelevant.
        for _, group in values.groupby(level="date", sort=False):
            for target, exposures in spec.residualize.items():
                valid = group[[target, *exposures]].dropna()
                transformed.loc[group.index, target] = np.nan
                if valid.empty:
                    continue
                design = np.column_stack([np.ones(len(valid)), valid[list(exposures)]])
                if len(valid) <= design.shape[1] or np.linalg.matrix_rank(design) < design.shape[1]:
                    raise ValueError(
                        "residualization requires full rank and residual degrees of freedom"
                    )
                coef = np.linalg.lstsq(design, valid[target].to_numpy(), rcond=None)[0]
                transformed.loc[valid.index, target] = valid[target] - design @ coef
    row_weights = pd.DataFrame(
        np.tile(weights.reindex(aliases), (len(values), 1)), index=values.index, columns=aliases
    )
    if spec.method == "conditional":
        low = values[spec.gate] <= spec.threshold
        row_weights.loc[low, :] = pd.Series(dict(spec.low_weights)).reindex(aliases).to_numpy()
    scores = (transformed * row_weights).sum(axis=1, skipna=False)
    if spec.method == "interaction":
        for left, right, coefficient in spec.interactions:
            scores += coefficient * transformed[left] * transformed[right]
    return scores, transformed, row_weights
