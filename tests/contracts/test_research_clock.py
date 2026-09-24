from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

import pytest
from research_contracts import RESEARCH_CLOCK_SCHEMA_VERSION, ResearchClock, validate_research_clock


def _clock_mapping() -> dict[str, object]:
    return {
        "schema_version": RESEARCH_CLOCK_SCHEMA_VERSION,
        "timezone": "UTC",
        "information_cutoff_at": "2026-09-25T09:00:00+00:00",
        "signal_at": "2026-09-25T09:01:00+00:00",
        "decision_at": "2026-09-25T09:02:00+00:00",
        "earliest_order_at": "2026-09-25T09:03:00+00:00",
        "execution_window_start_at": "2026-09-25T09:04:00+00:00",
        "execution_window_end_at": "2026-09-25T09:05:00+00:00",
        "valuation_at": "2026-09-25T09:06:00+00:00",
        "timing_policy_id": "next_bar_open",
        "trading_calendar_ref": "synthetic-calendar-v1",
    }


def test_research_clock_accepts_ordered_utc_timeline_and_round_trips() -> None:
    clock = validate_research_clock(_clock_mapping(), require_execution=True)

    assert clock.signal_at.isoformat() == "2026-09-25T09:01:00+00:00"
    assert ResearchClock.from_mapping(clock.to_mapping()) == clock


def test_research_clock_compares_aware_times_across_offsets() -> None:
    payload = _clock_mapping()
    payload["timezone"] = "Asia/Shanghai"
    payload["information_cutoff_at"] = "2026-09-25T17:00:00+08:00"
    payload["signal_at"] = "2026-09-25T09:00:00+00:00"
    payload["decision_at"] = "2026-09-25T17:01:00+08:00"
    payload["earliest_order_at"] = "2026-09-25T09:02:00+00:00"
    payload["execution_window_start_at"] = "2026-09-25T17:03:00+08:00"
    payload["execution_window_end_at"] = "2026-09-25T09:04:00+00:00"
    payload["valuation_at"] = "2026-09-25T17:05:00+08:00"

    clock = validate_research_clock(payload, require_execution=True)

    assert clock.timezone == "Asia/Shanghai"


def test_research_clock_accepts_dst_offset_aware_datetimes() -> None:
    new_york = ZoneInfo("America/New_York")
    payload = _clock_mapping()
    payload["timezone"] = "America/New_York"
    payload["information_cutoff_at"] = datetime(2026, 11, 1, 0, 30, tzinfo=new_york).isoformat()
    payload["signal_at"] = datetime(2026, 11, 1, 1, 30, tzinfo=new_york, fold=0).isoformat()
    payload["decision_at"] = datetime(2026, 11, 1, 1, 30, tzinfo=new_york, fold=1).isoformat()
    payload["earliest_order_at"] = datetime(2026, 11, 1, 2, 0, tzinfo=new_york).isoformat()
    payload["execution_window_start_at"] = datetime(2026, 11, 1, 2, 15, tzinfo=new_york).isoformat()
    payload["execution_window_end_at"] = datetime(2026, 11, 1, 2, 30, tzinfo=new_york).isoformat()
    payload["valuation_at"] = datetime(2026, 11, 1, 2, 45, tzinfo=new_york).isoformat()

    assert validate_research_clock(payload, require_execution=True).timezone == "America/New_York"


def test_research_clock_rejects_signal_after_decision_across_dst_fold() -> None:
    new_york = ZoneInfo("America/New_York")
    payload = _clock_mapping()
    payload["timezone"] = "America/New_York"
    payload["information_cutoff_at"] = datetime(2026, 11, 1, 0, 30, tzinfo=new_york)
    payload["signal_at"] = datetime(2026, 11, 1, 1, 30, tzinfo=new_york, fold=1)
    payload["decision_at"] = datetime(2026, 11, 1, 1, 45, tzinfo=new_york, fold=0)
    payload["valuation_at"] = datetime(2026, 11, 1, 2, 30, tzinfo=new_york)
    payload["earliest_order_at"] = None
    payload["execution_window_start_at"] = None
    payload["execution_window_end_at"] = None

    with pytest.raises(ValueError, match="signal_at must be <= decision_at"):
        validate_research_clock(payload)


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("information_cutoff_at", "2026-09-25T09:02:00+00:00", "information_cutoff_at"),
        ("signal_at", "2026-09-25T09:03:00+00:00", "signal_at"),
        ("decision_at", "2026-09-25T09:07:00+00:00", "decision_at"),
        ("earliest_order_at", "2026-09-25T09:01:00+00:00", "earliest_order_at"),
        ("execution_window_start_at", "2026-09-25T09:01:00+00:00", "execution_window_start_at"),
        ("execution_window_end_at", "2026-09-25T09:03:00+00:00", "execution_window_start_at"),
        ("earliest_order_at", "2026-09-25T09:06:00+00:00", "earliest_order_at"),
        ("execution_window_end_at", "2026-09-25T09:07:00+00:00", "execution_window_end_at"),
    ],
)
def test_research_clock_rejects_each_invalid_ordering(field: str, value: str, message: str) -> None:
    payload = _clock_mapping()
    payload[field] = value

    with pytest.raises(ValueError, match=message):
        validate_research_clock(payload)


def test_research_clock_allows_no_execution_window_for_diagnostic_runs() -> None:
    payload = _clock_mapping()
    payload["earliest_order_at"] = None
    payload["execution_window_start_at"] = None
    payload["execution_window_end_at"] = None

    clock = validate_research_clock(payload)

    assert clock.execution_window_start_at is None
    assert clock.execution_window_end_at is None


def test_research_clock_rejects_partial_execution_window() -> None:
    payload = _clock_mapping()
    payload["execution_window_end_at"] = None

    with pytest.raises(ValueError, match="must be provided together"):
        validate_research_clock(payload)


def test_research_clock_requires_execution_fields_for_execution_aware_runs() -> None:
    payload = _clock_mapping()
    payload["earliest_order_at"] = None

    with pytest.raises(ValueError, match="earliest_order_at is required"):
        validate_research_clock(payload, require_execution=True)


def test_research_clock_rejects_naive_timestamps() -> None:
    payload = _clock_mapping()
    payload["signal_at"] = "2026-09-25T09:01:00"

    with pytest.raises(ValueError, match="signal_at must be timezone-aware"):
        validate_research_clock(payload)


def test_research_clock_rejects_unknown_schema_version() -> None:
    payload = _clock_mapping()
    payload["schema_version"] = "research.clock.v2"

    with pytest.raises(ValueError, match="unsupported research clock schema"):
        validate_research_clock(payload)
