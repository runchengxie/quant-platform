"""Strategy-neutral validation for event windows and time-ordered folds."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from datetime import date, timedelta
from typing import Any

import numpy as np


def _date(value: object) -> date:
    if isinstance(value, date):
        return value
    return date.fromisoformat(str(value)[:10])


@dataclass(frozen=True, slots=True)
class EventWindow:
    event_id: str
    start: date
    end: date

    def __init__(self, event_id: str, start: object, end: object) -> None:
        if _date(end) < _date(start):
            raise ValueError("event window end must not precede start")
        object.__setattr__(self, "event_id", str(event_id))
        object.__setattr__(self, "start", _date(start))
        object.__setattr__(self, "end", _date(end))


@dataclass(frozen=True, slots=True)
class TemporalFold:
    fold: int
    train_indices: tuple[int, ...]
    test_indices: tuple[int, ...]
    purged_count: int
    embargoed_count: int

    def to_mapping(self) -> dict[str, Any]:
        return {
            "fold": self.fold,
            "train_indices": list(self.train_indices),
            "test_indices": list(self.test_indices),
            "purged_count": self.purged_count,
            "embargoed_count": self.embargoed_count,
        }


def purge_overlap(
    train: Sequence[EventWindow],
    test: Sequence[EventWindow],
    *,
    embargo_days: int = 0,
) -> tuple[list[EventWindow], dict[str, int]]:
    """Remove training events that overlap test labels or the test embargo."""
    if embargo_days < 0:
        raise ValueError("embargo_days must be non-negative")
    test_start = min((item.start for item in test), default=None)
    test_end = max((item.end for item in test), default=None)
    embargo_end = test_end + timedelta(days=embargo_days) if test_end else None
    kept: list[EventWindow] = []
    purged = 0
    embargoed = 0
    for item in train:
        overlaps = any(item.start <= other.end and item.end >= other.start for other in test)
        if overlaps:
            purged += 1
            continue
        in_embargo = (
            embargo_end is not None
            and test_start is not None
            and item.start > test_end
            and item.start <= embargo_end
        )
        if in_embargo:
            embargoed += 1
            continue
        kept.append(item)
    return kept, {"purged_count": purged, "embargoed_count": embargoed}


class PurgedWalkForwardSplit:
    """Build chronological folds from event windows with explicit purging."""

    def __init__(self, *, n_splits: int, test_size: int, embargo_days: int = 0) -> None:
        if n_splits < 1 or test_size < 1:
            raise ValueError("n_splits and test_size must be positive")
        if embargo_days < 0:
            raise ValueError("embargo_days must be non-negative")
        self.n_splits = n_splits
        self.test_size = test_size
        self.embargo_days = embargo_days

    def split(self, events: Sequence[EventWindow]) -> list[TemporalFold]:
        ordered = sorted(
            enumerate(events),
            key=lambda pair: (pair[1].start, pair[1].end, pair[1].event_id),
        )
        if not ordered:
            return []
        folds: list[TemporalFold] = []
        first_test_start = len(ordered) - self.n_splits * self.test_size
        for fold_number in range(self.n_splits):
            start = first_test_start + fold_number * self.test_size
            end = start + self.test_size
            if start <= 0 or end > len(ordered):
                continue
            test_pairs = ordered[start:end]
            train_pairs = ordered[:start]
            kept, receipt = purge_overlap(
                [item for _, item in train_pairs],
                [item for _, item in test_pairs],
                embargo_days=self.embargo_days,
            )
            kept_ids = {item.event_id for item in kept}
            folds.append(
                TemporalFold(
                    fold=fold_number + 1,
                    train_indices=tuple(
                        index for index, item in train_pairs if item.event_id in kept_ids
                    ),
                    test_indices=tuple(index for index, _ in test_pairs),
                    purged_count=receipt["purged_count"],
                    embargoed_count=receipt["embargoed_count"],
                )
            )
        return folds


def effective_sample_size(
    observations: int | Sequence[float] | np.ndarray,
    *,
    average_active_bets: float | None = None,
) -> float:
    """Estimate independent-equivalent observations under overlap/weights."""
    if average_active_bets is not None:
        if average_active_bets <= 0:
            raise ValueError("average_active_bets must be positive")
        return float(observations) / float(average_active_bets)
    values = np.asarray(observations, dtype=float)
    if values.ndim != 1 or values.size == 0 or not np.isfinite(values).all():
        raise ValueError("observations must be a non-empty finite one-dimensional array")
    denominator = float(np.square(values).sum())
    return float(np.square(values.sum()) / denominator) if denominator else 0.0
