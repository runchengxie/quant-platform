"""Shared input identity and date-block inference for research diagnostics."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping, Sequence
from dataclasses import asdict, dataclass
from numbers import Integral, Number
from typing import Any

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class BlockStatistics:
    """Explicit time-grid settings; block length is measured in supplied dates."""

    block_length: int
    repetitions: int
    min_dates: int
    seed: int = 0
    confidence: float = 0.95

    def __post_init__(self) -> None:
        for name in ("block_length", "repetitions", "min_dates", "seed"):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, Integral):
                raise ValueError(f"{name} must be an integer")
        if self.block_length < 1 or self.repetitions < 1 or self.min_dates < 2 or self.seed < 0:
            raise ValueError("invalid block statistics settings")
        if not np.isfinite(self.confidence) or not 0 < self.confidence < 1:
            raise ValueError("confidence must be between zero and one")


@dataclass(frozen=True)
class SignalReliabilityResult:
    summary: dict[str, Any]
    by_date: pd.DataFrame
    profile: pd.DataFrame


def validate_ks(ks: Sequence[int]) -> tuple[int, ...]:
    values = tuple(ks)
    if not values or any(
        isinstance(k, bool) or not isinstance(k, Integral) or k < 1 for k in values
    ):
        raise ValueError("ks must contain positive integers")
    if tuple(sorted(set(values))) != values:
        raise ValueError("ks must be unique and increasing")
    return values


def prepare_panel(
    panel: pd.DataFrame,
    *,
    date_col: str,
    symbol_col: str,
    numeric_cols: Sequence[str],
    category_cols: Sequence[str] = (),
    statistics: BlockStatistics,
) -> pd.DataFrame:
    columns = [date_col, symbol_col, *numeric_cols, *category_cols]
    if len(columns) != len(set(columns)):
        raise ValueError("column roles must be distinct")
    if not isinstance(panel, pd.DataFrame) or panel.empty:
        raise ValueError("panel must be a nonempty DataFrame")
    if not panel.columns.is_unique or any(col not in panel for col in columns):
        raise ValueError("panel columns must be unique and include every requested column")
    frame = panel.loc[:, columns].copy()
    _normalize_keys(frame, date_col, symbol_col)
    for col in numeric_cols:
        frame[col] = pd.to_numeric(frame[col], errors="coerce").astype(float)
        frame[col] = frame[col].where(np.isfinite(frame[col]))
    for col in category_cols:
        frame[col] = frame[col].astype("string")
        frame[col] = frame[col].where(frame[col].str.strip().ne(""))
    frame = frame.sort_values([date_col, symbol_col]).reset_index(drop=True)
    if statistics.block_length > frame[date_col].nunique():
        raise ValueError("block length exceeds supplied date grid")
    return frame


def _normalize_keys(frame: pd.DataFrame, date_col: str, symbol_col: str) -> None:
    if frame[[date_col, symbol_col]].isna().any().any():
        raise ValueError("date/symbol keys must not be missing")
    if frame[date_col].map(lambda value: isinstance(value, Number)).any():
        raise ValueError("numeric date keys require explicit conversion to trading dates")
    try:
        frame[date_col] = pd.to_datetime(frame[date_col], format="mixed", utc=True).dt.normalize()
    except (ValueError, TypeError) as exc:
        raise ValueError("invalid date keys") from exc
    frame[symbol_col] = frame[symbol_col].astype(str)
    if frame[date_col].isna().any() or frame[symbol_col].str.strip().eq("").any():
        raise ValueError("invalid date/symbol keys")
    if frame.duplicated([date_col, symbol_col]).any():
        raise ValueError("duplicate normalized date/symbol keys")


def correlation(x: pd.Series, y: pd.Series, *, rank: bool = False) -> float:
    if len(x) < 2:
        return float("nan")
    a, b = (x.rank(), y.rank()) if rank else (x, y)
    if a.std(ddof=0) <= 1e-12 or b.std(ddof=0) <= 1e-12:
        return float("nan")
    return float(np.corrcoef(a.to_numpy(dtype=float), b.to_numpy(dtype=float))[0, 1])


def interval(values: np.ndarray, settings: BlockStatistics) -> dict[str, Any]:
    valid = np.isfinite(values)
    result = {
        "n_dates": len(values),
        "n_eligible_dates": int(valid.sum()),
        "mean": float(values[valid].mean()) if valid.any() else np.nan,
        "ci_low": np.nan,
        "ci_high": np.nan,
        "invalid_resamples": 0,
        "interval_status": "insufficient_dates",
    }
    if valid.sum() < settings.min_dates:
        return result
    rng = np.random.default_rng(settings.seed)
    length = settings.block_length
    means = []
    for _ in range(settings.repetitions):
        starts = rng.integers(
            0, len(values) - length + 1, size=(len(values) + length - 1) // length
        )
        indices = (starts[:, None] + np.arange(length)).ravel()[: len(values)]
        sample = values[indices]
        usable = sample[np.isfinite(sample)]
        if len(usable) < settings.min_dates:
            result["invalid_resamples"] += 1
        else:
            means.append(float(usable.mean()))
    # A heavily missing resample distribution cannot support its advertised interval.
    if len(means) < max(2, int(np.ceil(settings.repetitions * 0.9))):
        result["interval_status"] = "insufficient_resamples"
        return result
    q = (1 - settings.confidence) / 2
    result.update(
        ci_low=float(np.quantile(means, q)),
        ci_high=float(np.quantile(means, 1 - q)),
        interval_status="ok",
    )
    return result


def finish(
    frame: pd.DataFrame,
    rows: list[dict[str, Any]],
    *,
    kind: str,
    date_col: str,
    settings: BlockStatistics,
    definitions: Mapping[str, Any],
    provenance: Mapping[str, Any] | None,
    extra: Mapping[str, Any] | None = None,
) -> SignalReliabilityResult:
    # Reject unserializable caller metadata instead of stringifying unknown objects.
    declared = json.loads(json.dumps(dict(provenance or {}), allow_nan=False))
    details = pd.DataFrame(rows)
    dates = pd.Index(frame[date_col].drop_duplicates().dt.strftime("%Y-%m-%d"))
    profiles = []
    for (group, metric), part in details.groupby(["group", "metric"], sort=False):
        series = part.set_index("date")["value"].reindex(dates)
        profiles.append(
            dict(group=group, metric=metric, **interval(series.to_numpy(dtype=float), settings))
        )
    digest = hashlib.sha256()
    digest.update(json.dumps(list(frame.columns)).encode())
    digest.update(pd.util.hash_pandas_object(frame, index=False).to_numpy().tobytes())
    summary = {
        "artifact_type": f"alpha_research.{kind}",
        "schema_version": 1,
        "input_fingerprint": digest.hexdigest(),
        "rows": len(frame),
        "n_dates": len(dates),
        "date_start": dates[0],
        "date_end": dates[-1],
        "definitions": dict(definitions),
        "statistics": asdict(settings),
        "provenance_declared": declared,
        "warnings": [
            "Pointwise descriptive intervals; no multiple-testing correction.",
            "Declared PIT/OOS provenance is not independently verified.",
            "Label returns exclude execution costs unless explicitly supplied as labels.",
            "Conditional associations are not causal contributions.",
        ],
    }
    summary.update(extra or {})
    return SignalReliabilityResult(summary, details, pd.DataFrame(profiles))
