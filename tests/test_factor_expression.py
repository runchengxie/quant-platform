import pandas as pd
import pytest
from alpha_research.factor_expression import FactorExpression, parse_factor
from numpy import nan


def test_parse_factor_exposes_dependencies_lookback_and_normalized_text() -> None:
    expression = parse_factor("RANK(RETURNS(CLOSE, 20)) * -STDDEV(CLOSE, 5)")

    assert isinstance(expression, FactorExpression)
    assert expression.required_columns() == ("CLOSE",)
    assert expression.lookback() == 20
    assert expression.operators() == ("RANK", "RETURNS", "STDDEV")
    assert expression.normalized() == "RANK(RETURNS(CLOSE, 20)) * -STDDEV(CLOSE, 5)"


@pytest.mark.parametrize(
    "source",
    [
        "__import__('os')",
        "CLOSE.real",
        "CLOSE[0]",
        "eval('CLOSE')",
        "RANK(x=CLOSE)",
        "DELAY(CLOSE, 0)",
        "CLOSE; OPEN",
    ],
)
def test_parse_factor_rejects_unsafe_or_invalid_syntax(source: str) -> None:
    with pytest.raises(ValueError):
        parse_factor(source)


def test_factor_expression_evaluates_time_series_and_cross_sectional_semantics() -> None:
    index = pd.MultiIndex.from_product(
        [["A", "B"], pd.date_range("2026-01-01", periods=3)],
        names=["symbol", "date"],
    )
    frame = pd.DataFrame(
        {"CLOSE": [1.0, 2.0, 4.0, 2.0, 4.0, 8.0]},
        index=index,
    )

    result = parse_factor("RETURNS(CLOSE, 1)").evaluate(frame)

    expected = pd.Series([nan, 1.0, 1.0, nan, 1.0, 1.0], index=index, name="factor")
    pd.testing.assert_series_equal(result, expected)


def test_rank_is_cross_sectional_by_date() -> None:
    index = pd.MultiIndex.from_product(
        [["A", "B"], pd.date_range("2026-01-01", periods=2)],
        names=["symbol", "date"],
    )
    frame = pd.DataFrame({"CLOSE": [1.0, 3.0, 2.0, 4.0]}, index=index)

    result = parse_factor("RANK(CLOSE)").evaluate(frame)

    assert result.loc[("A", "2026-01-01")] == 0.5
    assert result.loc[("B", "2026-01-01")] == 1.0
    assert result.loc[("A", "2026-01-02")] == 0.5
    assert result.loc[("B", "2026-01-02")] == 1.0


def test_evaluate_rejects_missing_columns() -> None:
    with pytest.raises(KeyError, match="CLOSE"):
        parse_factor("CLOSE").evaluate(pd.DataFrame({"OPEN": [1.0]}))


def test_time_series_operator_requires_symbol_date_multiindex() -> None:
    with pytest.raises(ValueError, match="MultiIndex"):
        parse_factor("DELAY(CLOSE, 1)").evaluate(pd.DataFrame({"CLOSE": [1.0]}))


def test_rolling_correlation_uses_two_series_and_window() -> None:
    index = pd.MultiIndex.from_product(
        [["A"], pd.date_range("2026-01-01", periods=3)],
        names=["symbol", "date"],
    )
    frame = pd.DataFrame(
        {"CLOSE": [1.0, 2.0, 4.0], "OPEN": [2.0, 4.0, 8.0]},
        index=index,
    )

    result = parse_factor("CORRELATION(CLOSE, OPEN, 2)").evaluate(frame)

    assert result.iloc[0] != result.iloc[0]
    assert result.iloc[1] == pytest.approx(1.0)
    assert result.iloc[2] == pytest.approx(1.0)


def test_nested_time_series_operators_accumulate_lookback() -> None:
    assert parse_factor("DELAY(RETURNS(CLOSE, 20), 5)").lookback() == 25


def test_time_series_operator_rejects_unsorted_dates() -> None:
    index = pd.MultiIndex.from_tuples(
        [("A", "2026-01-02"), ("A", "2026-01-01")], names=["symbol", "date"]
    )
    frame = pd.DataFrame({"CLOSE": [2.0, 1.0]}, index=index)

    with pytest.raises(ValueError, match="sorted"):
        parse_factor("DELAY(CLOSE, 1)").evaluate(frame)


def test_parse_factor_rejects_oversized_expression() -> None:
    with pytest.raises(ValueError, match="too large"):
        parse_factor("-" * 1000 + "CLOSE")
