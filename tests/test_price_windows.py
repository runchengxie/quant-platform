from __future__ import annotations

import numpy as np
import pandas as pd
import pytest
from pandas.testing import assert_frame_equal

from quant_platform.prices import convert_price_window


def quotes():
    return pd.DataFrame(
        {
            "symbol": ["AAA"] * 3,
            "trade_date": ["2024-01-02", "2024-01-03", "2024-01-04"],
            "available_at": [f"2024-01-0{day}T08:00:00Z" for day in (2, 3, 4)],
            "close": [100.0, 50.0, 60.0],
            "volume": [10, 20, 30],
            "amount": [1000, 1000, 1800],
        },
        index=[7, 3, 9],
    )


def factors():
    return quotes()[["symbol", "trade_date", "available_at"]].assign(adj_factor=[1, 2, 2])


def convert(prices=None, factor_rows=None, **kwargs):
    return convert_price_window(
        quotes() if prices is None else prices,
        basis=kwargs.pop("basis", "pit_qfq"),
        as_of=kwargs.pop("as_of", "2024-01-04T08:00:00Z"),
        source_ref="synthetic:quotes-v1",
        factors=factors() if factor_rows is None else factor_rows,
        factor_source_ref="synthetic:factors-v1",
        price_columns=("close",),
        **kwargs,
    )


@pytest.mark.parametrize(
    ("basis", "expected"),
    [("raw", [100, 50, 60]), ("hfq", [100, 100, 120]), ("pit_qfq", [50, 50, 60])],
)
def test_price_units_and_total_return_momentum(basis, expected):
    result = convert(basis=basis)
    assert result.prices.close.tolist() == expected
    assert result.basis == basis
    assert result.as_of == pd.Timestamp("2024-01-04T08:00:00Z")
    if basis != "raw":
        assert result.prices.close.iloc[-1] / result.prices.close.iloc[0] - 1 == pytest.approx(0.2)
    if basis == "pit_qfq":
        assert result.anchors.adj_factor.tolist() == [2]
        assert result.prices.close.iloc[-1] == 60
    else:
        assert result.anchors.empty


def test_raw_needs_no_factor_history():
    result = convert_price_window(
        quotes(),
        basis="raw",
        as_of="2024-01-04T08:00:00Z",
        source_ref="quotes:1",
        price_columns=("close",),
    )
    assert result.prices.close.tolist() == [100, 50, 60]
    assert result.factor_source_ref is None


def test_each_security_uses_its_own_anchor_and_preserves_nonprice_columns():
    source = pd.concat([quotes(), quotes().assign(symbol="BBB", close=[40, 20, 25])])
    fact = pd.concat([factors(), factors().assign(symbol="BBB", adj_factor=[3, 6, 6])])
    original, original_factors = source.copy(deep=True), fact.copy(deep=True)
    result = convert(source, fact)
    assert result.prices.close.tolist() == [50, 50, 60, 20, 20, 25]
    assert result.anchors.set_index("symbol").adj_factor.to_dict() == {"AAA": 2, "BBB": 6}
    assert result.prices.volume.tolist() == [10, 20, 30, 10, 20, 30]
    assert result.prices.amount.tolist() == [1000, 1000, 1800, 1000, 1000, 1800]
    assert result.prices.index.tolist() == source.index.tolist()
    assert_frame_equal(source, original)
    assert_frame_equal(fact, original_factors)
    result.prices.loc[:, "close"] = 1
    assert_frame_equal(source, original)


def test_later_events_and_revisions_do_not_change_frozen_earlier_windows():
    cutoff = "2024-01-03T08:00:00Z"
    baseline = convert(quotes().iloc[:2], factors().iloc[:2], as_of=cutoff)
    future_quote = quotes().iloc[[0]].assign(available_at="2024-01-04T07:00:00Z", close=200)
    future_factor = factors().iloc[[0]].assign(available_at="2024-01-04T07:00:00Z", adj_factor=10)
    result = convert(
        pd.concat([quotes(), future_quote]), pd.concat([factors(), future_factor]), as_of=cutoff
    )
    assert_frame_equal(result.prices, baseline.prices)
    assert_frame_equal(result.anchors, baseline.anchors)
    assert result.prices.close.tolist() == [50, 50]


def test_latest_eligible_quote_and_factor_vintages_are_selected_independently():
    revised_quote = quotes().iloc[[0]].assign(available_at="2024-01-03T06:00:00Z", close=110)
    revised_factor = factors().iloc[[0]].assign(available_at="2024-01-03T07:00:00Z", adj_factor=1.2)
    result = convert(pd.concat([quotes(), revised_quote]), pd.concat([factors(), revised_factor]))
    assert result.prices.close.tolist() == [50, 60, 66]
    assert result.prices.trade_date.tolist() == [
        pd.Timestamp("2024-01-03"),
        pd.Timestamp("2024-01-04"),
        pd.Timestamp("2024-01-02"),
    ]


def test_anchor_can_be_newer_than_last_quote_without_fabricating_a_quote():
    result = convert(quotes().iloc[:1])
    assert result.prices.close.tolist() == [50]
    assert result.anchors.trade_date.tolist() == [pd.Timestamp("2024-01-04")]


def test_missing_quote_stays_unknown_and_shanghai_market_date_is_used():
    result = convert(quotes().assign(close=[np.nan, 50, 60]), as_of="2024-01-04T00:00:00+08:00")
    assert len(result.prices) == 2
    assert np.isnan(result.prices.close.iloc[0])
    assert result.prices.close.iloc[1] == 50


@pytest.mark.parametrize("basis", ["invalid", "RAW", None])
def test_unknown_basis_rejects(basis):
    with pytest.raises(ValueError):
        convert(basis=basis)


@pytest.mark.parametrize("cutoff", ["2024-01-04", "bad", 123, pd.NaT])
def test_ambiguous_as_of_rejects(cutoff):
    with pytest.raises(ValueError):
        convert(as_of=cutoff)


@pytest.mark.parametrize("target", ["quote", "factor"])
@pytest.mark.parametrize("change", ["duplicate", "naive_clock", "numeric_date", "bad_symbol"])
def test_ambiguous_source_rows_reject(target, change):
    frame = quotes() if target == "quote" else factors()
    if change == "duplicate":
        frame = pd.concat([frame, frame.iloc[[0]]])
    elif change == "naive_clock":
        frame["available_at"] = "2024-01-02"
    elif change == "numeric_date":
        frame["trade_date"] = 20240102
    else:
        frame["symbol"] = " "
    with pytest.raises(ValueError):
        convert(prices=frame) if target == "quote" else convert(factor_rows=frame)


@pytest.mark.parametrize("value", [0, -1, np.inf, np.nan, "invalid"])
def test_invalid_factors_reject_instead_of_falling_back_to_one(value):
    with pytest.raises(ValueError):
        convert(factor_rows=factors().assign(adj_factor=value))


@pytest.mark.parametrize("value", [0, -1, np.inf, "invalid"])
def test_invalid_nonmissing_raw_prices_reject(value):
    with pytest.raises(ValueError):
        convert(prices=quotes().assign(close=value))


def test_unavailable_factor_for_historical_quote_rejects():
    frame = factors()
    frame.loc[7, "available_at"] = "2024-01-05T08:00:00Z"
    with pytest.raises(ValueError, match="factor"):
        convert(factor_rows=frame)


def test_empty_eligible_window_rejects():
    with pytest.raises(ValueError):
        convert(as_of="2024-01-01T08:00:00Z")


@pytest.mark.parametrize("missing", ["source_ref", "factor_source_ref", "factors", "close"])
def test_missing_required_inputs_reject(missing):
    args = {
        "basis": "pit_qfq",
        "as_of": "2024-01-04T08:00:00Z",
        "source_ref": "quotes:1",
        "factors": factors(),
        "factor_source_ref": "factors:1",
        "price_columns": ("close",),
    }
    source = quotes()
    if missing == "close":
        source = source.drop(columns="close")
    else:
        args[missing] = None
    with pytest.raises(ValueError):
        convert_price_window(source, **args)


def test_hfq_overflow_rejects_and_pit_ratio_avoids_intermediate_overflow():
    source = quotes().iloc[:1].assign(close=1e200)
    fact = factors().iloc[:1].assign(adj_factor=1e200)
    with pytest.raises(ValueError, match="finite"):
        convert(source, fact, basis="hfq")
    assert convert(source, fact).prices.close.tolist() == [1e200]
