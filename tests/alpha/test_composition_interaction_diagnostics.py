import pandas as pd
import pytest
from alpha_research.factor_composition_diagnostics import double_sort_profile


def test_double_sort_difference_in_differences_is_one_percentage_point():
    index = pd.MultiIndex.from_product(
        [[pd.Timestamp("2026-01-01")], list("ABCDEFGH")], names=["date", "symbol"]
    )
    factors = pd.DataFrame(
        {
            "Q": [0.0, 0.0, 0.0, 0.0, 1.0, 1.0, 1.0, 1.0],
            "V": [0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 1.0, 1.0],
        },
        index=index,
    )
    labels = pd.Series([0.005, 0.005, 0.015, 0.015, 0.01, 0.01, 0.03, 0.03], index=index)
    result = double_sort_profile(factors, labels, quality="Q", value="V", bins=2, min_cell=2)
    assert result.by_date.interaction_spread.iloc[0] == pytest.approx(0.01)
    assert result.cells.observations.eq(2).all()
    sparse = double_sort_profile(
        factors.iloc[:1], labels.iloc[:1], quality="Q", value="V", bins=2, min_cell=2
    )
    assert pd.isna(sparse.by_date.interaction_spread.iloc[0])
