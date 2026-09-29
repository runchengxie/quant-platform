from __future__ import annotations

from quant_platform.temporal_validation import EventWindow, PurgedWalkForwardSplit


def test_temporal_validation_is_available_from_stable_platform_namespace() -> None:
    events = [
        EventWindow("a", "2024-01-01", "2024-01-01"),
        EventWindow("b", "2024-01-02", "2024-01-02"),
    ]

    folds = PurgedWalkForwardSplit(n_splits=1, test_size=1).split(events)

    assert folds[0].test_indices == (1,)
