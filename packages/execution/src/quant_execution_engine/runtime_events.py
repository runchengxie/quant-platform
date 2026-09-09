"""Typed, deterministic lifecycle events local to a runtime instance."""
from collections import defaultdict
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from typing import TypeVar

T = TypeVar("T")

@dataclass(frozen=True, slots=True)
class RuntimeEvent:
    occurred_at: datetime

@dataclass(frozen=True, slots=True)
class TradingDayStarted(RuntimeEvent):
    trading_date: str

@dataclass(frozen=True, slots=True)
class MarketDataAvailable(RuntimeEvent):
    trading_date: str
    data_vintage: str

@dataclass(frozen=True, slots=True)
class StrategyEvaluated(RuntimeEvent):
    strategy_ref: str
    target_count: int

@dataclass(frozen=True, slots=True)
class OrderRequested(RuntimeEvent):
    intent_id: str

@dataclass(frozen=True, slots=True)
class PreTradeRiskChecked(RuntimeEvent):
    intent_id: str
    outcome: str

@dataclass(frozen=True, slots=True)
class FillGenerated(RuntimeEvent):
    fill_id: str
    intent_id: str

@dataclass(frozen=True, slots=True)
class PortfolioUpdated(RuntimeEvent):
    portfolio_id: str

@dataclass(frozen=True, slots=True)
class ValuationCompleted(RuntimeEvent):
    portfolio_id: str
    nav: str

@dataclass(frozen=True, slots=True)
class TradingDayCompleted(RuntimeEvent):
    trading_date: str

EventHandler = Callable[[RuntimeEvent], None]

class LocalEventBus:
    def __init__(self) -> None:
        self._handlers: dict[type[RuntimeEvent], list[EventHandler]] = defaultdict(list)
        self._closed = False

    def subscribe(self, event_type: type[T], handler: Callable[[T], None]) -> None:
        if self._closed:
            raise RuntimeError("event bus is closed")
        self._handlers[event_type].append(handler)  # type: ignore[arg-type]

    def publish(self, event: RuntimeEvent) -> None:
        if self._closed:
            raise RuntimeError("event bus is closed")
        for handler in tuple(self._handlers[type(event)]):
            handler(event)

    def close(self) -> None:
        self._closed = True
