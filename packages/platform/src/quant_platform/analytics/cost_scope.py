"""Past-only signed fill-shortfall calibration with explicit applicability.

Shortfall is signed basis points against the decision mid, including fees once.
Participation is filled shares / contemporaneous market shares over the same
execution interval. Unfilled opportunity cost is not a fill-cost observation.
Coefficients do not identify permanent impact or authorize automatic promotion.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from scipy.optimize import nnls


@dataclass(frozen=True)
class ScopedCostModel:
    intercept_bps: float
    impact_bps: float
    cutoff_ns: int
    side: str
    liquidity_bucket: str
    execution_minutes: int
    min_participation: float
    max_participation: float
    observations: int
    source_binding: str
    evidence_kind: str
    cost_basis: str = "signed_decision_mid_fill_shortfall_including_fees"

    def predict(self, participation, *, side, liquidity_bucket, execution_minutes):
        if (side, liquidity_bucket, execution_minutes) != (
            self.side,
            self.liquidity_bucket,
            self.execution_minutes,
        ):
            raise ValueError("cost scope mismatch")
        if (
            not np.isfinite(participation)
            or not self.min_participation <= participation <= self.max_participation
        ):
            raise ValueError("participation outside cost scope")
        return float(self.intercept_bps + self.impact_bps * np.sqrt(participation))


def _frame(observations):
    required = {
        "available_ns",
        "completed_ns",
        "participation",
        "filled_notional",
        "shortfall_bps",
        "side",
        "liquidity_bucket",
        "execution_minutes",
    }
    if not required <= set(observations):
        raise ValueError("missing cost observation columns")
    if any(type(v) is not int for v in observations.available_ns):
        raise ValueError("observation completion clocks must be integer UTC nanoseconds")
    if "completed_ns" not in observations or any(
        type(v) is not int for v in observations.completed_ns
    ):
        raise ValueError("integer execution completion clocks required")
    if (observations.completed_ns > observations.available_ns).any():
        raise ValueError("execution completion follows observation availability")
    return observations.copy()


def _numeric(frame):
    numbers = frame[["participation", "filled_notional", "shortfall_bps", "execution_minutes"]]
    if not np.isfinite(numbers.to_numpy(dtype=float)).all():
        raise ValueError("finite cost observations required")
    if (frame.participation <= 0).any() or (frame.filled_notional <= 0).any():
        raise ValueError("positive filled participation/notional required")
    if (frame.execution_minutes <= 0).any() or not frame.execution_minutes.map(
        lambda v: float(v).is_integer()
    ).all():
        raise ValueError("positive integer execution minutes required")
    if (
        not frame.side.isin(["buy", "sell"]).all()
        or not frame.liquidity_bucket.map(lambda v: isinstance(v, str) and bool(v.strip())).all()
    ):
        raise ValueError("explicit cost scope required")


def fit_cost_scope(
    observations: pd.DataFrame,
    *,
    cutoff_ns: int,
    source_binding: str,
    evidence_kind: str,
    min_observations: int = 3,
) -> ScopedCostModel:
    if type(cutoff_ns) is not int or not source_binding.strip() or min_observations < 3:
        raise ValueError("cutoff, source and minimum sample >=3 required")
    if evidence_kind not in {"synthetic", "broker_fills"}:
        raise ValueError("cost evidence kind must be explicit")
    frame = _frame(observations)
    frame = frame.loc[frame.available_ns <= cutoff_ns]
    if len(frame) < min_observations:
        raise ValueError("insufficient completed calibration observations")
    _numeric(frame)
    groups = frame[["side", "liquidity_bucket", "execution_minutes"]].drop_duplicates()
    if len(groups) != 1:
        raise ValueError("fit each cost scope separately")
    if frame.participation.nunique() < 2:
        raise ValueError("insufficient participation variation")
    weights = np.sqrt(frame.filled_notional.to_numpy(dtype=float) / frame.filled_notional.sum())
    design = np.column_stack(
        (np.ones(len(frame)), np.sqrt(frame.participation.to_numpy(dtype=float)))
    )
    coefficients, _ = nnls(
        design * weights[:, None], frame.shortfall_bps.to_numpy(dtype=float) * weights
    )
    group = groups.iloc[0]
    return ScopedCostModel(
        float(coefficients[0]),
        float(coefficients[1]),
        cutoff_ns,
        group.side,
        group.liquidity_bucket,
        int(group.execution_minutes),
        float(frame.participation.min()),
        float(frame.participation.max()),
        len(frame),
        source_binding,
        evidence_kind,
    )


def validate_cost_scope(
    model: ScopedCostModel, observations: pd.DataFrame, *, source_binding: str
) -> dict:
    if source_binding != model.source_binding:
        raise ValueError("validation source binding mismatch")
    frame = _frame(observations)
    frame = frame.loc[frame.available_ns > model.cutoff_ns]
    _numeric(frame)
    errors, weights = [], []
    unsupported = 0
    for row in frame.itertuples():
        try:
            predicted = model.predict(
                row.participation,
                side=row.side,
                liquidity_bucket=row.liquidity_bucket,
                execution_minutes=row.execution_minutes,
            )
        except ValueError:
            unsupported += 1
            continue
        errors.append(row.shortfall_bps - predicted)
        weights.append(row.filled_notional)
    return {
        "schema": "scoped-cost-validation.v1",
        "source_binding": source_binding,
        "observations": len(errors),
        "unsupported": unsupported,
        "cutoff_ns": model.cutoff_ns,
        "status": "evaluated" if errors else "insufficient_supported_holdout",
        "bias_bps": float(np.average(errors, weights=weights)) if errors else None,
        "rmse_bps": float(np.sqrt(np.average(np.square(errors), weights=weights)))
        if errors
        else None,
        "evidence_kind": model.evidence_kind,
        "promoted": False,
    }
