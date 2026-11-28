"""Price-unit conversion from caller-supplied, independently timed vintages.

Source references and observation clocks are caller declarations, not certificates.
No fills, inventory, cash flows or corporate-action entitlements are inferred here.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from numbers import Real
from re import fullmatch
from typing import Literal

import numpy as np
import pandas as pd

PriceBasis = Literal["raw", "hfq", "pit_qfq"]
_KEY = ["symbol", "trade_date"]
_ANCHORS = ["symbol", "trade_date", "adj_factor", "available_at"]


@dataclass(frozen=True)
class PriceWindow:
    """Converted copies and declared lineage; DataFrames remain caller-mutable."""

    prices: pd.DataFrame
    basis: PriceBasis
    as_of: pd.Timestamp
    source_ref: str
    factor_source_ref: str | None
    anchors: pd.DataFrame


def _clock(value: object) -> pd.Timestamp:
    if isinstance(value, str) and not fullmatch(
        r"\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}(?::\d{2}(?:\.\d{1,9})?)?(?:Z|[+-]\d{2}:?\d{2})",
        value,
    ):
        raise ValueError("timestamps require a complete ISO calendar date, time and offset")
    if not isinstance(value, (str, datetime, pd.Timestamp)):
        raise ValueError("observation clocks and as_of must be timezone-aware timestamps")
    try:
        clock = pd.Timestamp(value)
    except (TypeError, ValueError) as exc:
        raise ValueError("invalid observation timestamp") from exc
    if pd.isna(clock) or clock.tzinfo is None:
        raise ValueError("observation clocks and as_of must be timezone-aware timestamps")
    return clock.tz_convert("UTC")


def _session(value: object) -> pd.Timestamp:
    if isinstance(value, str) and not fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        raise ValueError("trade_date strings must use complete ISO YYYY-MM-DD dates")
    if not isinstance(value, (str, date, pd.Timestamp)):
        raise ValueError("trade_date must be a timezone-naive calendar date")
    try:
        day = pd.Timestamp(value)
    except (TypeError, ValueError) as exc:
        raise ValueError("invalid trade_date") from exc
    if not isinstance(day, pd.Timestamp) or day.tzinfo is not None or day != day.normalize():
        raise ValueError("trade_date must be a timezone-naive calendar date")
    return day


def _reference(value: object, name: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be a nonempty source reference")


def _vintage(frame: pd.DataFrame, cutoff: pd.Timestamp, required: Sequence[str]) -> pd.DataFrame:
    if not isinstance(frame, pd.DataFrame) or not frame.columns.is_unique:
        raise ValueError("source must be a DataFrame with unique columns")
    if missing := {*_KEY, "available_at", *required} - set(frame.columns):
        raise ValueError(f"missing source columns: {sorted(missing)}")
    work = frame.copy(deep=True).reset_index(drop=True)
    if not work.symbol.map(
        lambda v: isinstance(v, str) and bool(v.strip()) and v == v.strip()
    ).all():
        raise ValueError("symbol must be a normalized nonempty string")
    work["trade_date"] = pd.to_datetime(work.trade_date.map(_session))
    work["available_at"] = pd.to_datetime(work.available_at.map(_clock), utc=True)
    if work.duplicated([*_KEY, "available_at"]).any():
        raise ValueError("duplicate source vintage")
    horizon = cutoff.tz_convert("Asia/Shanghai").tz_localize(None).normalize()
    selected = (
        work.loc[work.available_at.le(cutoff) & work.trade_date.le(horizon)]
        .sort_values("available_at", kind="stable")
        .drop_duplicates(_KEY, keep="last")
        .sort_index()
    )
    selected.index = frame.index.take(selected.index)
    return selected


def _positive(values: pd.Series, *, allow_missing: bool, label: str) -> np.ndarray:
    missing = values.isna().to_numpy()
    valid_types = values.loc[~missing].map(
        lambda v: isinstance(v, (Real, Decimal, str)) and not isinstance(v, (bool, np.bool_))
    )
    if not valid_types.all():
        raise ValueError(f"{label} requires real numeric values")
    converted = pd.to_numeric(values, errors="coerce").to_numpy(dtype=float, na_value=np.nan)
    invalid = ~np.isfinite(converted) | (converted <= 0)
    if allow_missing:
        invalid &= ~missing
    if invalid.any():
        raise ValueError(f"{label} must be finite and positive")
    return converted


def _adjust(
    prices: pd.DataFrame,
    factors: pd.DataFrame,
    basis: PriceBasis,
    columns: Sequence[str],
) -> pd.DataFrame:
    if factors.empty:
        raise ValueError("no eligible factors")
    fact = factors.set_index(_KEY)
    keys = pd.MultiIndex.from_frame(prices[_KEY])
    selected = fact.reindex(keys)
    daily = _positive(selected.adj_factor, allow_missing=False, label="factor coverage")
    anchors = pd.DataFrame(columns=_ANCHORS)
    if basis == "pit_qfq":
        anchors = (
            factors.reset_index(drop=True)
            .sort_values("trade_date", kind="stable")
            .drop_duplicates("symbol", keep="last")
            .loc[:, _ANCHORS]
            .sort_values("symbol", kind="stable")
            .reset_index(drop=True)
        )
        base = prices.symbol.map(anchors.set_index("symbol").adj_factor).to_numpy(dtype=float)
        with np.errstate(over="ignore", under="ignore", invalid="ignore", divide="ignore"):
            daily = daily / base
    for column in columns:
        raw = _positive(prices[column], allow_missing=True, label=column)
        with np.errstate(over="ignore", under="ignore", invalid="ignore"):
            adjusted = raw * daily
        if ((~np.isfinite(adjusted) | (adjusted <= 0)) & ~np.isnan(raw)).any():
            raise ValueError("converted nonmissing prices must be finite and positive")
        prices[column] = adjusted
    return anchors


def convert_price_window(
    prices: pd.DataFrame,
    *,
    basis: PriceBasis,
    as_of: str | pd.Timestamp,
    source_ref: str,
    factors: pd.DataFrame | None = None,
    factor_source_ref: str | None = None,
    price_columns: Sequence[str] = ("open", "high", "low", "close"),
) -> PriceWindow:
    """Convert eligible raw quote vintages to RAW, supplier-scale HFQ or PIT QFQ.

    Both tables require symbol, trade_date and timezone-aware available_at. Factor
    rows additionally require adj_factor. Latest eligible vintages are selected
    independently before joining; missing required factors reject. A source clock
    must describe actual historical availability to support a PIT claim.
    """
    if basis not in ("raw", "hfq", "pit_qfq"):
        raise ValueError("basis must be raw, hfq or pit_qfq")
    _reference(source_ref, "source_ref")
    cutoff = _clock(as_of)
    columns = tuple(price_columns)
    protected = {*_KEY, "available_at", "adj_factor", "volume", "amount", "turnover"}
    if (
        isinstance(price_columns, str)
        or not columns
        or any(not isinstance(c, str) or not c.strip() for c in columns)
        or len(set(columns)) != len(columns)
        or protected.intersection(columns)
    ):
        raise ValueError("price_columns must contain distinct price fields only")
    result = _vintage(prices, cutoff, columns)
    if result.empty:
        raise ValueError("no eligible quotes")
    for column in columns:
        _positive(result[column], allow_missing=True, label=column)
    anchors = pd.DataFrame(columns=_ANCHORS)
    if basis != "raw":
        _reference(factor_source_ref, "factor_source_ref")
        if factors is None:
            raise ValueError("adjusted prices require factors")
        eligible = _vintage(factors, cutoff, ("adj_factor",))
        eligible["adj_factor"] = _positive(
            eligible.adj_factor, allow_missing=False, label="adj_factor"
        )
        anchors = _adjust(result, eligible, basis, columns)
    return PriceWindow(
        result, basis, cutoff, source_ref, factor_source_ref if basis != "raw" else None, anchors
    )
