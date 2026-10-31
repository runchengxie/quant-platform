"""Read-only calibration of backtest cost assumptions from realized TCA."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pandas as pd

TCA_CALIBRATION_SCHEMA = "portfolio_backtester.tca-calibration.v1"
_REQUIRED_COLUMNS = frozenset(
    {
        "trade_date",
        "requested_notional",
        "filled_notional",
        "modeled_cost_bps",
        "realized_cost_bps",
    }
)


@dataclass(frozen=True)
class TCACalibrationReceipt:
    """Evidence-backed cost recommendation; it never mutates a cost model."""

    model_version: str
    source_version: str
    status: str
    observation_count: int
    observation_start: str | None
    observation_end: str | None
    requested_notional: float
    filled_notional: float
    coverage_ratio: float
    modeled_cost_bps: float
    realized_cost_bps: float
    residual_cost_bps: float
    recommended_cost_bps: float | None

    def to_mapping(self) -> dict[str, Any]:
        return {
            "schema_version": TCA_CALIBRATION_SCHEMA,
            "model_version": self.model_version,
            "source_version": self.source_version,
            "status": self.status,
            "observation_count": self.observation_count,
            "observation_start": self.observation_start,
            "observation_end": self.observation_end,
            "requested_notional": self.requested_notional,
            "filled_notional": self.filled_notional,
            "coverage_ratio": self.coverage_ratio,
            "modeled_cost_bps": self.modeled_cost_bps,
            "realized_cost_bps": self.realized_cost_bps,
            "residual_cost_bps": self.residual_cost_bps,
            "recommended_cost_bps": self.recommended_cost_bps,
        }


def calibrate_cost_model(
    observations: pd.DataFrame,
    *,
    model_version: str,
    source_version: str,
    min_observations: int = 20,
) -> TCACalibrationReceipt:
    """Summarize realized-vs-modeled costs for a governed model update.

    Costs are weighted by requested notional so unfilled orders remain in the
    denominator. A recommendation is emitted only when the minimum sample
    threshold is met; callers must separately review and promote it.
    """

    if not model_version.strip() or not source_version.strip():
        raise ValueError("model_version and source_version are required")
    if min_observations < 1:
        raise ValueError("min_observations must be positive")
    missing = sorted(_REQUIRED_COLUMNS - set(observations.columns))
    if missing:
        raise ValueError("missing required columns: " + ", ".join(missing))

    frame = observations[list(_REQUIRED_COLUMNS)].copy()
    frame["trade_date"] = pd.to_datetime(frame["trade_date"], errors="coerce")
    numeric = [
        "requested_notional",
        "filled_notional",
        "modeled_cost_bps",
        "realized_cost_bps",
    ]
    for column in numeric:
        frame[column] = pd.to_numeric(frame[column], errors="coerce")
    frame[numeric] = frame[numeric].replace([float("inf"), float("-inf")], pd.NA)
    if frame[numeric].isna().any().any() or frame["trade_date"].isna().any():
        raise ValueError("TCA observations must contain finite dates and numeric values")
    if (frame["requested_notional"] <= 0).any():
        raise ValueError("requested_notional must be positive")
    if (frame["filled_notional"] < 0).any() or (
        frame["filled_notional"] > frame["requested_notional"]
    ).any():
        raise ValueError("filled_notional must be between zero and requested_notional")
    if (frame[["modeled_cost_bps", "realized_cost_bps"]] < 0).any().any():
        raise ValueError("cost_bps must be non-negative")

    requested = float(frame["requested_notional"].sum())
    filled = float(frame["filled_notional"].sum())
    weights = frame["requested_notional"] / requested
    modeled = float((frame["modeled_cost_bps"] * weights).sum())
    realized = float((frame["realized_cost_bps"] * weights).sum())
    status = "ready" if len(frame) >= min_observations else "insufficient_data"
    return TCACalibrationReceipt(
        model_version=model_version.strip(),
        source_version=source_version.strip(),
        status=status,
        observation_count=len(frame),
        observation_start=frame["trade_date"].min().date().isoformat(),
        observation_end=frame["trade_date"].max().date().isoformat(),
        requested_notional=requested,
        filled_notional=filled,
        coverage_ratio=filled / requested,
        modeled_cost_bps=modeled,
        realized_cost_bps=realized,
        residual_cost_bps=realized - modeled,
        recommended_cost_bps=realized if status == "ready" else None,
    )


__all__ = ["TCA_CALIBRATION_SCHEMA", "TCACalibrationReceipt", "calibrate_cost_model"]
