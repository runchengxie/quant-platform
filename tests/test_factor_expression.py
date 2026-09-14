import pandas as pd
import pytest

from alpha_research.factor_expression import FactorExpression, parse_factor


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

