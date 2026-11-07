import pandas as pd
import pytest

from quant_platform.backtest.legacy.execution import ParticipationSlippageModel


@pytest.mark.parametrize("liquidity", [None, float("nan"), 0, -1, float("inf")])
def test_strict_coverage_rejects_missing_liquidity(liquidity):
    model = ParticipationSlippageModel(impact_bps=10, coverage_policy="raise")
    row = None if liquidity is None else pd.Series({"A": liquidity})
    with pytest.raises(ValueError, match="liquidity"):
        model.cost(pd.Series({"A": 0.1}), pricing_row=row, is_initial=False, side="buy")


def test_strict_coverage_rejects_extrapolation_instead_of_clipping():
    model = ParticipationSlippageModel(
        impact_bps=10, max_participation=0.1, coverage_policy="raise"
    )
    with pytest.raises(ValueError, match="calibrat"):
        model.cost(
            pd.Series({"A": 0.1}), pricing_row=pd.Series({"A": 1000}), is_initial=False, side="buy"
        )


def test_default_is_strict_and_legacy_fallback_requires_opt_in():
    trade = pd.Series({"A": 0.1})
    with pytest.raises(ValueError, match="liquidity"):
        ParticipationSlippageModel(impact_bps=10).cost(
            trade, pricing_row=None, is_initial=False, side="buy"
        )
    assert (
        ParticipationSlippageModel(impact_bps=10, coverage_policy="legacy").cost(
            trade, pricing_row=None, is_initial=False, side="buy"
        )
        == 0
    )
