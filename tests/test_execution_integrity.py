import pandas as pd
import pytest

from quant_platform.portfolio.sleeves import pool_sleeves


def target():
    return pd.DataFrame(
        {
            "decision_time": [pd.Timestamp("2026-01-01", tz="UTC")],
            "entry_time": [pd.Timestamp("2026-01-02", tz="UTC")],
            "symbol": ["A"],
            "weight": [1.0],
        }
    )


def test_pool_uses_one_total_cash_budget_and_rejects_schedule_or_weight_changes():
    pooled = pool_sleeves({"one": target(), "two": target()}, {"one": 0.5, "two": 0.5})
    assert pooled.weight.tolist() == [1.0]
    changed = target()
    changed["decision_time"] += pd.Timedelta(seconds=1)
    with pytest.raises(ValueError, match="schedule"):
        pool_sleeves({"one": target(), "two": changed}, {"one": 0.5, "two": 0.5})
    with pytest.raises(ValueError, match="budget"):
        pool_sleeves({"one": target(), "two": target()}, {"one": 0.6, "two": 0.6})
