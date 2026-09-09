from datetime import UTC, datetime
import pytest
from quant_execution_engine.runtime_events import LocalEventBus, TradingDayStarted

def test_local_event_bus_preserves_subscription_order() -> None:
    bus = LocalEventBus(); seen: list[str] = []
    event = TradingDayStarted(datetime.now(UTC), "2026-01-01")
    bus.subscribe(TradingDayStarted, lambda _: seen.append("a"))
    bus.subscribe(TradingDayStarted, lambda _: seen.append("b"))
    bus.publish(event)
    assert seen == ["a", "b"]

def test_local_event_bus_rejects_publish_after_close() -> None:
    bus = LocalEventBus(); bus.close()
    with pytest.raises(RuntimeError, match="closed"):
        bus.publish(TradingDayStarted(datetime.now(UTC), "2026-01-01"))
