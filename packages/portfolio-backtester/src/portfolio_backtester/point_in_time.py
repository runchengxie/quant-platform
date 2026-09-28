"""Information-clock access to research input tables.

Rows must carry source availability timestamps. A market date alone is not
evidence that the value was available when a signal was formed.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import datetime

import pandas as pd
from research_contracts import ResearchClock, validate_research_clock


def _aware_timestamp(value: object, label: str) -> pd.Timestamp:
    if value is None or pd.isna(value):
        raise ValueError(f"{label} contains an unknown timestamp")
    if not isinstance(value, (str, datetime)):
        raise ValueError(f"{label} contains an invalid timestamp")
    try:
        timestamp = pd.Timestamp(value)
    except (TypeError, ValueError) as error:
        raise ValueError(f"{label} contains an invalid timestamp") from error
    if timestamp.tzinfo is None or timestamp.utcoffset() is None:
        raise ValueError(f"{label} must contain timezone-aware timestamps")
    return timestamp.tz_convert("UTC")


@dataclass(frozen=True)
class PointInTimeTable:
    frame: pd.DataFrame
    available_at_col: str
    event_at_col: str | None = None
    _available_at: pd.Series = field(init=False, repr=False)
    _event_at: pd.Series | None = field(init=False, repr=False)

    def __post_init__(self) -> None:
        required = {self.available_at_col}
        if self.event_at_col is not None:
            required.add(self.event_at_col)
        missing = required - set(self.frame.columns)
        if missing:
            raise ValueError(f"point-in-time table is missing {sorted(missing)}")
        # Keep a snapshot so mutations to the caller's DataFrame cannot make
        # historical reads change between decisions.
        object.__setattr__(self, "frame", self.frame.copy(deep=True))
        object.__setattr__(
            self,
            "_available_at",
            pd.Series(
                [
                    _aware_timestamp(value, self.available_at_col)
                    for value in self.frame[self.available_at_col]
                ],
                index=self.frame.index,
            ),
        )
        object.__setattr__(
            self,
            "_event_at",
            pd.Series(
                [
                    _aware_timestamp(value, self.event_at_col)
                    for value in self.frame[self.event_at_col]
                ],
                index=self.frame.index,
            )
            if self.event_at_col is not None
            else None,
        )


class PointInTimeDataView:
    """Expose only rows known by each decision's information cutoff."""

    def __init__(self, tables: Mapping[str, PointInTimeTable]) -> None:
        if not tables:
            raise ValueError("at least one point-in-time table is required")
        self._tables = dict(tables)

    def at(self, clock: ResearchClock | Mapping[str, object]) -> _BoundDataView:
        checked = validate_research_clock(
            clock.to_mapping() if isinstance(clock, ResearchClock) else clock,
            require_execution=True,
        )
        return _BoundDataView(self._tables, checked.information_cutoff_at)


class _BoundDataView:
    def __init__(self, tables: Mapping[str, PointInTimeTable], cutoff: datetime) -> None:
        self._tables = tables
        self._cutoff = pd.Timestamp(cutoff).tz_convert("UTC")

    def read(self, name: str) -> pd.DataFrame:
        table = self._tables[name]
        visible = table._available_at.le(self._cutoff)
        if table._event_at is not None:
            visible &= table._event_at.le(self._cutoff)
        return table.frame.loc[visible].copy(deep=True)


__all__ = ["PointInTimeDataView", "PointInTimeTable"]
