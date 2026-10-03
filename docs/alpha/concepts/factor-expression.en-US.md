# Safe Factor-Expression DSL

Language: English · [简体中文](factor-expression.md)

`alpha_research.factor_expression` provides a strategy-agnostic factor formula layer. It offers a familiar formula interface but interprets only allowlisted expressions. It does not execute arbitrary Python, load data, or write research artifacts.

## Basic use

```python
from alpha_research import parse_factor

factor = parse_factor("RANK(RETURNS(CLOSE, 20))")

factor.required_columns()  # ("CLOSE",)
factor.lookback()  # 20
factor.operators()  # ("RANK", "RETURNS")
result = factor.evaluate(frame)
```

`frame` must be a pandas DataFrame. Time-series operators require a MultiIndex with levels named `symbol` and `date`. Rows for each symbol must be ordered by date; otherwise evaluation is rejected.

## Supported operators

| Operator | Behavior |
| --- | --- |
| `RANK(x)` | Cross-sectional percentile rank within each `date` |
| `DELAY(x, n)` | Shift by `n` observations within each symbol |
| `RETURNS(x, n)` | `x / DELAY(x, n) - 1` |
| `STDDEV(x, n)` | Rolling sample standard deviation within each symbol |
| `CORRELATION(x, y, n)` | Rolling correlation within each symbol |

Expressions support `+`, `-`, `*`, `/`, and unary plus/minus. Window `n` must be a positive integer constant. `lookback()` reports the maximum required history, including nested cumulative windows.

## Safety boundary

The parser uses Python's AST only to recognize syntax. Executable forms are limited to input columns, numeric constants, allowlisted functions, and basic arithmetic. Imports, attribute access, subscripting, keyword arguments, lambdas, `eval`, `exec`, double-underscore names, and future windows are rejected.

Researchers or agents can use `FactorExpression` to draft formulas. A formula still needs the caller's data-version, point-in-time, and research-evidence contracts before it can support a formal research conclusion.
