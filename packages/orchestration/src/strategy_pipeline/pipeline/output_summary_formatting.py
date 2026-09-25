"""Formatting helpers shared by output summary sections."""

from __future__ import annotations

from datetime import date, datetime
from typing import Any

import numpy as np
import pandas as pd


def _path_text(value: Any) -> str | None:
    return str(value) if value else None


def _date_text(value: date | datetime | None) -> str | None:
    return value.strftime("%Y%m%d") if value else None


def _date_list_text(values: Any) -> list[str]:
    return [pd.to_datetime(date).strftime("%Y%m%d") for date in values]


def _date_bounds_text(values: Any) -> dict[str, str | None]:
    dates = pd.to_datetime(list(values), errors="coerce")
    dates = dates[~dates.isna()]
    if len(dates) == 0:
        return {"start": None, "end": None}
    return {
        "start": dates.min().strftime("%Y%m%d"),
        "end": dates.max().strftime("%Y%m%d"),
    }


def _json_scalar(value: Any) -> Any:
    if value is None:
        return None
    try:
        if pd.isna(value):
            return None
    except (TypeError, ValueError):
        pass
    if isinstance(value, np.generic):
        return value.item()
    return value


def _frame_records(frame: Any) -> list[dict[str, Any]]:
    if not isinstance(frame, pd.DataFrame) or frame.empty:
        return []
    rows: list[dict[str, Any]] = []
    for row in frame.to_dict("records"):
        rows.append({str(key): _json_scalar(value) for key, value in row.items()})
    return rows
