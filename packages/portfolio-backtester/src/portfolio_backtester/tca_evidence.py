"""Grouped signed shortfall evidence, not an automatic cost-model update."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Sequence
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

TCA_EVIDENCE_SCHEMA = "portfolio_backtester.tca-evidence.v2"
_NUMERIC = (
    "requested_notional",
    "filled_notional",
    "execution_cash",
    "opportunity_cash",
    "fee_cash",
    "total_cash",
    "total_bps",
)


def _checksum(payload: dict[str, Any]) -> str:
    body = {key: value for key, value in payload.items() if key != "payload_sha256"}
    return hashlib.sha256(
        json.dumps(body, sort_keys=True, allow_nan=False, separators=(",", ":")).encode()
    ).hexdigest()


def _mean_interval(frame: pd.DataFrame, samples: int, seed: int) -> list[float] | None:
    blocks = [group for _, group in frame.groupby("trade_date", sort=True)]
    if len(blocks) < 2:
        return None
    # Aggregate complete date blocks, preserving every order and its notional.
    numerators = np.array([(block.total_bps * block.requested_notional).sum() for block in blocks])
    denominators = np.array([block.requested_notional.sum() for block in blocks])
    rng = np.random.default_rng(seed)
    values = []
    for _ in range(samples):
        chosen = rng.integers(0, len(blocks), size=len(blocks))
        values.append(float(numerators[chosen].sum() / denominators[chosen].sum()))
    return np.quantile(values, [0.025, 0.975]).tolist()


def _summarize_group(
    frame: pd.DataFrame,
    identity: dict[str, object],
    *,
    minimum: int,
    coverage_minimum: float,
    samples: int,
    seed: int,
) -> dict[str, object]:
    requested = float(frame.requested_notional.sum())
    filled = float(frame.filled_notional.sum())
    coverage = filled / requested
    mean = float((frame.total_bps * frame.requested_notional).sum() / requested)
    dates = sorted(frame.trade_date.unique().tolist())
    reasons = []
    if len(frame) < minimum:
        reasons.append("insufficient_observations")
    if len(dates) < 2:
        reasons.append("insufficient_dates")
    if filled <= 0:
        reasons.append("no_execution_evidence")
    if coverage < coverage_minimum:
        reasons.append("insufficient_fill_coverage")
    return {
        "group": identity,
        "status": "insufficient_evidence" if reasons else "ready",
        "reasons": reasons,
        "observation_count": len(frame),
        "date_count": len(dates),
        "observation_start": dates[0],
        "observation_end": dates[-1],
        "requested_notional": requested,
        "filled_notional": filled,
        "coverage_ratio": coverage,
        "mean_shortfall_bps": mean,
        "median_shortfall_bps": float(frame.total_bps.median()),
        "p95_shortfall_bps": float(frame.total_bps.quantile(0.95)),
        "mean_ci_bps": _mean_interval(frame, samples, seed),
        "recommended_shortfall_bps": None if reasons else mean,
    }


def _validated_observations(observations: pd.DataFrame, groups: list[str]) -> pd.DataFrame:
    required = {"order_id", "trade_date", *_NUMERIC, *groups}
    if required - set(observations.columns) or observations.empty:
        raise ValueError("non-empty observations with required columns needed")
    frame = observations.copy(deep=True)
    if (
        frame.order_id.isna().any()
        or frame.order_id.astype(str).str.strip().eq("").any()
        or frame.order_id.astype(str).duplicated().any()
    ):
        raise ValueError("unique non-empty order IDs required")
    dates = pd.to_datetime(frame.trade_date, format="%Y-%m-%d", errors="coerce")
    if dates.isna().any():
        raise ValueError("valid market dates required")
    frame["trade_date"] = dates.dt.strftime("%Y-%m-%d")
    for col in _NUMERIC:
        frame[col] = pd.to_numeric(frame[col], errors="coerce")
    if not np.isfinite(frame[list(_NUMERIC)].to_numpy(dtype=float)).all():
        raise ValueError("finite cost observations required")
    if (
        frame.requested_notional.le(0).any()
        or frame.filled_notional.lt(0).any()
        or frame.filled_notional.gt(frame.requested_notional).any()
        or frame.fee_cash.lt(0).any()
    ):
        raise ValueError("invalid requested/filled notional or fee")
    if not np.allclose(
        frame.total_cash, frame.execution_cash + frame.opportunity_cash + frame.fee_cash
    ):
        raise ValueError("shortfall components do not reconcile")
    if not np.allclose(frame.total_bps, frame.total_cash / frame.requested_notional * 10_000):
        raise ValueError("shortfall units do not reconcile")
    return frame


def summarize_tca(
    observations: pd.DataFrame,
    *,
    group_cols: Sequence[str],
    min_observations: int,
    min_coverage: float,
    bootstrap_samples: int = 500,
    seed: int = 0,
) -> dict[str, Any]:
    """Means use requested-notional weights; median/P95 are empirical order quantiles."""
    if (
        type(min_observations) is not int
        or min_observations < 1
        or not np.isfinite(min_coverage)
        or not 0 <= min_coverage <= 1
        or type(bootstrap_samples) is not int
        or bootstrap_samples < 1
        or type(seed) is not int
        or seed < 0
    ):
        raise ValueError("invalid evidence controls")
    groups = list(group_cols)
    if len(set(groups)) != len(groups):
        raise ValueError("duplicate group columns")
    frame = _validated_observations(observations, groups)
    partitions = frame.groupby(groups, dropna=False, sort=True) if groups else [((), frame)]
    summaries = []
    for key, group in partitions:
        values = key if isinstance(key, tuple) else (key,)
        identity = {
            col: None
            if pd.isna(value)
            else value.item()
            if isinstance(value, np.generic)
            else value
            for col, value in zip(groups, values, strict=True)
        }
        summaries.append(
            _summarize_group(
                group,
                identity,
                minimum=min_observations,
                coverage_minimum=min_coverage,
                samples=bootstrap_samples,
                seed=seed,
            )
        )
    payload = {
        "schema_version": TCA_EVIDENCE_SCHEMA,
        "groups": summaries,
        "controls": {
            "min_observations": min_observations,
            "min_coverage": min_coverage,
            "bootstrap_samples": bootstrap_samples,
            "seed": seed,
        },
        "mean_weighting": "requested_decision_notional",
        "quantile_weighting": "unweighted_orders",
        "uncertainty": "date_block_bootstrap_95_percent",
        "automatic_promotion": False,
    }
    payload["payload_sha256"] = _checksum(payload)
    return payload


def validate_tca_evidence(payload: dict[str, Any]) -> dict[str, Any]:
    """Check internal integrity, not authenticity or suitability for a strategy."""
    if (
        not isinstance(payload, dict)
        or payload.get("schema_version") != TCA_EVIDENCE_SCHEMA
        or not isinstance(payload.get("groups"), list)
        or not payload["groups"]
        or payload.get("automatic_promotion") is not False
        or payload.get("payload_sha256") != _checksum(payload)
    ):
        raise ValueError("invalid TCA evidence schema or checksum")
    return json.loads(json.dumps(payload, allow_nan=False))


def read_tca_evidence(path: Path, *, expected_sha256: str | None = None) -> dict[str, Any]:
    data = Path(path).read_bytes()
    if expected_sha256 is not None and hashlib.sha256(data).hexdigest() != expected_sha256:
        raise ValueError("TCA evidence artifact hash mismatch")
    return validate_tca_evidence(json.loads(data))
