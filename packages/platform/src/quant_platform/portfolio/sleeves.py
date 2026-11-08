"""Complete long-only target pooling for one execution account, not fill attribution."""

import math

import numpy as np
import pandas as pd


def pool_sleeves(targets_by_sleeve, budgets):
    """Fixed fractions of one initial account budget; cash stays with the owner."""
    if not targets_by_sleeve or set(targets_by_sleeve) != set(budgets):
        raise ValueError("explicit matching sleeves and budgets required")
    fractions = list(budgets.values())
    if (
        any(type(v) not in {int, float} or not math.isfinite(v) or v < 0 for v in fractions)
        or math.fsum(fractions) > 1
    ):
        raise ValueError("finite nonnegative shared budget totaling at most one required")
    schedule, frames = None, []
    for name in sorted(targets_by_sleeve):
        frame = targets_by_sleeve[name].copy()
        if frame.empty or frame.duplicated(["entry_time", "symbol"]).any():
            raise ValueError("nonempty complete unique sleeve snapshots required")
        if any(not isinstance(s, str) or not s.strip() for s in frame.symbol):
            raise ValueError("nonempty sleeve symbols required")
        clocks = frame[["entry_time", "decision_time"]].drop_duplicates().sort_values("entry_time")
        if (
            clocks.entry_time.duplicated().any()
            or not (clocks.decision_time < clocks.entry_time).all()
        ):
            raise ValueError("unique causal sleeve schedule required")
        if any(t.tzinfo is None for t in clocks.entry_time) or any(
            t.tzinfo is None for t in clocks.decision_time
        ):
            raise ValueError("aware sleeve schedule required")
        current = list(clocks.itertuples(index=False, name=None))
        if schedule is not None and schedule != current:
            raise ValueError("same decision and entry schedule required")
        schedule = current
        if (
            not np.isfinite(frame.weight).all()
            or (frame.weight < 0).any()
            or (frame.groupby("entry_time").weight.sum() > 1).any()
        ):
            raise ValueError("finite long-only sleeve weights totaling at most one required")
        frame["weight"] *= budgets[name]
        frames.append(frame[["decision_time", "entry_time", "symbol", "weight"]])
    return (
        pd.concat(frames, ignore_index=True)
        .groupby(["decision_time", "entry_time", "symbol"], as_index=False, sort=True)
        .weight.sum()
    )
