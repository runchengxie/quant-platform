"""Chronological fitting with explicit label maturity and auditable warmup."""

from __future__ import annotations

import numpy as np
import pandas as pd

from ._composition_models import fit_predict
from ._composition_provenance import composition_frame_sha256
from .factor_composition_spec import FactorCompositionSpec


def _labels(values, labels, available):
    if labels is None or available is None:
        raise ValueError("supervised composition requires labels and label_available_at")
    if not labels.index.equals(values.index) or not available.index.equals(values.index):
        raise ValueError("labels and availability must have exactly the factor index and order")
    if pd.api.types.is_complex_dtype(labels.dtype):
        raise ValueError("labels must be real")
    if not pd.api.types.is_numeric_dtype(labels.dtype):
        raise ValueError("labels must be numeric")
    if np.isinf(labels.to_numpy(dtype=float, na_value=np.nan)).any():
        raise ValueError("labels must be finite or missing")
    try:
        available = pd.to_datetime(available, errors="raise")
        feature_dates = values.index.get_level_values("date")
        if available.isna().any() or (available.to_numpy() < feature_dates.to_numpy()).any():
            raise ValueError("label availability cannot be missing or before its feature date")
        # Force compatible timezone awareness before comparisons in the fitting loop.
        _ = available < feature_dates.max() if len(feature_dates) else available
    except (TypeError, OverflowError) as exc:
        raise ValueError("label availability dates must use compatible timezones") from exc
    return labels.astype(float), available


def _strength_weights(train, target, spec):
    ic_rows = []
    for _, cross_section in train.groupby(level="date", sort=True):
        aligned = cross_section.join(target.rename("__target__")).dropna()
        if len(aligned) < spec.min_cross_section:
            continue
        ranks = aligned.rank()
        ic = ranks[list(spec.aliases)].corrwith(ranks["__target__"])
        if ic.notna().all():
            ic_rows.append(ic)
    if len(ic_rows) < spec.min_periods:
        return None
    history = pd.DataFrame(ic_rows)
    strength = history.mean()
    if spec.method == "icir":
        strength = strength / history.std(ddof=1).clip(lower=1e-8)
    elif spec.method == "covariance":
        corr = train.corr().to_numpy()
        corr = (1 - spec.shrinkage) * corr + spec.shrinkage * np.eye(len(strength))
        strength = pd.Series(np.linalg.solve(corr, strength.to_numpy()), index=strength.index)
    strength = strength.clip(lower=0.0)
    return strength / strength.sum() if strength.sum() > 0 else pd.Series(dtype=float)


def temporal_compose(values, spec: FactorCompositionSpec, labels, available):
    supervised = spec.method != "pca"
    if supervised:
        labels, available = _labels(values, labels, available)
    dates = values.index.get_level_values("date")
    ordered_dates = dates.unique().sort_values()
    scores = pd.Series(np.nan, index=values.index, dtype=float)
    weights = pd.DataFrame(np.nan, index=values.index, columns=values.columns)
    audit = []
    previous = None
    for date in ordered_dates:
        train, target = _training_sample(values, spec, labels, available, date, ordered_dates)
        record = {
            "date": date,
            "status": "insufficient_history",
            "train_rows": len(train),
            "train_dates": train.index.get_level_values("date").nunique(),
        }
        if record["train_dates"] < spec.min_periods or len(train) < spec.min_cross_section:
            audit.append(record)
            continue
        record.update(
            train_start=train.index.get_level_values("date").min(),
            train_end=train.index.get_level_values("date").max(),
            max_label_available_at=available.loc[train.index].max() if supervised else pd.NaT,
        )
        fit_data = train.join(target.rename("__target__")) if target is not None else train
        if supervised:
            fit_data = fit_data.join(available.loc[train.index].rename("__available_at__"))
        record["training_sha256"] = composition_frame_sha256(fit_data)
        prediction = values.loc[dates == date].dropna()
        if prediction.empty:
            record["status"] = "missing_prediction_inputs"
            audit.append(record)
            continue
        if spec.method in {"ic", "icir", "covariance"}:
            coef = _strength_weights(train, target, spec)
            if coef is None or coef.empty:
                record["status"] = (
                    "insufficient_ic_history" if coef is None else "no_positive_strength"
                )
                audit.append(record)
                continue
            coef, turnover = _limit_turnover(coef, previous, spec.max_weight_turnover)
            record["weight_turnover"] = turnover
            previous = coef.copy()
            predictions = prediction @ coef
            coefficients = coef.reindex(values.columns).to_numpy()
        else:
            if spec.n_components > min(len(train), np.linalg.matrix_rank(train.to_numpy())):
                record["status"] = "insufficient_rank"
                audit.append(record)
                continue
            predictions, coefficients, digest = fit_predict(train, target, prediction, spec)
            record["model_state_sha256"] = digest
        scores.loc[prediction.index] = np.asarray(predictions)
        weights.loc[prediction.index, :] = coefficients
        record["status"] = "fitted"
        audit.append(record)
    return scores, weights, pd.DataFrame(audit)


def _training_sample(values, spec, labels, available, date, ordered_dates):
    supervised = spec.method != "pca"
    dates = values.index.get_level_values("date")
    prior_dates = ordered_dates[ordered_dates < date][-spec.window :]
    mask = dates.isin(prior_dates)
    if supervised:
        mask &= (available < date).to_numpy()
        if spec.method in {"ic", "icir", "covariance"}:
            # IC is a cross-sectional estimate: do not train on a partially matured date.
            complete = (available < date).groupby(level="date").all()
            mask &= dates.isin(complete.index[complete])
    train = values.loc[mask].dropna()
    target = labels.reindex(train.index) if supervised else None
    if target is not None:
        train = train.loc[target.notna()]
        target = target.loc[train.index]
    return train, target


def _limit_turnover(coef, previous, limit):
    if previous is None:
        return coef, 0.0
    turnover = float((coef - previous).abs().sum())
    if turnover > limit:
        coef = previous + (coef - previous) * (limit / turnover)
    return coef, float((coef - previous).abs().sum())
