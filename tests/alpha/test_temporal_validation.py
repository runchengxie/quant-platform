from __future__ import annotations

import numpy as np
import pandas as pd
from alpha_research.temporal_validation import (
    EventWindow,
    PurgedWalkForwardSplit,
    effective_sample_size,
    purge_overlap,
)


def test_purge_overlap_removes_label_intersection_and_embargo() -> None:
    train = [
        EventWindow("old", "2024-01-01", "2024-01-02"),
        EventWindow("overlap", "2024-01-03", "2024-01-06"),
        EventWindow("embargo", "2024-01-11", "2024-01-12"),
    ]
    test = [EventWindow("test", "2024-01-05", "2024-01-10")]

    kept, receipt = purge_overlap(train, test, embargo_days=1)

    assert [item.event_id for item in kept] == ["old"]
    assert receipt["purged_count"] == 1
    assert receipt["embargoed_count"] == 1


def test_walk_forward_split_is_chronological_and_serializable() -> None:
    dates = pd.date_range("2024-01-01", periods=8, freq="D")
    events = [
        EventWindow(str(index), date, date + pd.Timedelta(days=1))
        for index, date in enumerate(dates)
    ]

    folds = PurgedWalkForwardSplit(n_splits=2, test_size=2, embargo_days=0).split(events)

    assert len(folds) == 2
    assert max(folds[0].train_indices) < min(folds[0].test_indices)
    assert folds[0].test_indices == (4, 5)
    assert folds[0].to_mapping()["purged_count"] >= 1


def test_effective_sample_size_accounts_for_overlapping_active_bets() -> None:
    assert effective_sample_size(100, average_active_bets=4) == 25.0
    assert np.isclose(effective_sample_size(np.array([1.0, 2.0, 3.0])), 2.571428571428571)
