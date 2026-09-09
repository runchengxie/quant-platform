"""Point-in-time market data boundary contracts."""

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Protocol


@dataclass(frozen=True, slots=True)
class MarketDataView:
    records: tuple[Mapping[str, Any], ...]
    data_vintage: str
    calendar_version: str
    as_of: datetime
    knowledge_time: datetime

    def __post_init__(self) -> None:
        if not self.data_vintage.strip() or not self.calendar_version.strip():
            raise ValueError("data_vintage and calendar_version are required")
        if self.knowledge_time > self.as_of:
            raise ValueError("knowledge_time must be <= as_of")
        for record in self.records:
            effective = record.get("effective_time")
            if isinstance(effective, datetime) and effective > self.knowledge_time:
                raise ValueError("market data contains information after knowledge_time")


class MarketDataPort(Protocol):
    def bars(
        self,
        instrument: str,
        *,
        start: datetime,
        end: datetime,
        as_of: datetime,
        knowledge_time: datetime,
    ) -> MarketDataView: ...
    def instruments(self, *, as_of: datetime, knowledge_time: datetime) -> MarketDataView: ...
    def trading_calendar(self, *, calendar_version: str) -> tuple[str, ...]: ...
