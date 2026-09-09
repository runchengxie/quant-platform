from datetime import UTC, datetime, timedelta

import pytest

from market_data_platform.ports import MarketDataView


def test_pit_view_accepts_records_known_at_cutoff() -> None:
    now = datetime.now(UTC)
    view = MarketDataView(({"effective_time": now - timedelta(days=1)},), "v1", "cal1", now, now)
    assert view.data_vintage == "v1"

def test_pit_view_rejects_future_information() -> None:
    now = datetime.now(UTC)
    with pytest.raises(ValueError, match="after knowledge_time"):
        MarketDataView(({"effective_time": now + timedelta(seconds=1)},), "v1", "cal1", now, now)
