# FactorExpression 安全公式 DSL Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在 `alpha_research` 中提供一个不执行任意 Python 的安全因子公式 DSL，支持静态依赖/lookback 分析和 pandas DataFrame 执行。

**Architecture:** `ast.parse` 只负责构造语法树，`OperatorRegistry` 负责白名单算子及其元数据，验证器拒绝不支持的 AST 节点并检查窗口参数，解释器递归执行已验证节点。公开入口 `parse_factor()` 返回不可变的 `FactorExpression`，不加载数据、不写产物。

**Tech Stack:** Python 3.12、标准库 `ast`/`dataclasses`、pandas、pytest。

**Spec:** `docs/alpha/superpowers/specs/2026-09-14-factor-expression-design.md`

## Global Constraints

- 平台代码必须保持策略无关，不依赖私有研究模块、真实数据或凭证。
- 不新增第三方依赖。
- 禁止 `eval`、`exec`、导入、属性访问、下标访问、关键字参数和未来窗口。
- 输入使用带 `(symbol, date)` MultiIndex 的 pandas DataFrame，输出为同索引 Series。
- 时间序列窗口必须是正整数常量；lookback 取表达式树上的最大窗口。

---

### Task 1: Define the public expression API and rejection behavior

**Files:**
- Create: `packages/alpha/src/alpha_research/factor_expression.py`
- Create: `tests/test_factor_expression.py`
- Modify: `packages/alpha/src/alpha_research/__init__.py`

**Interfaces:**
- Produces `FactorExpression`, `OperatorRegistry`, `parse_factor`, `FactorExpression.required_columns()`, `lookback()`, `normalized()`, `operators()`, and `evaluate(frame)`.

- [ ] **Step 1: Write failing tests for public parsing and security**

```python
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
```

- [ ] **Step 2: Run the focused test to verify it fails**

Run: `uv run pytest tests/test_factor_expression.py -q`
Expected: FAIL because `alpha_research.factor_expression` does not exist.

- [ ] **Step 3: Implement the minimal AST validator and public object**

Implement an internal validated-node tree or validated AST wrapper. `parse_factor` must reject empty/multi-statement input, validate exact function names and argument counts, collect ordered column names and operator names, and compute maximum window. `FactorExpression.evaluate` may initially raise `NotImplementedError`; execution is added in Task 2.

- [ ] **Step 4: Run the focused test to verify it passes**

Run: `uv run pytest tests/test_factor_expression.py -q`
Expected: PASS for dependency, metadata, and rejection tests.

- [ ] **Step 5: Export the public API**

Add the three public names to `alpha_research.__init__` and keep internal validator helpers private.

- [ ] **Step 6: Commit**

```bash
git add packages/alpha/src/alpha_research/factor_expression.py \
  packages/alpha/src/alpha_research/__init__.py tests/test_factor_expression.py
git commit -m "feat: add safe factor expression parser"
```

### Task 2: Implement deterministic pandas execution for the first operators

**Files:**
- Modify: `packages/alpha/src/alpha_research/factor_expression.py`
- Modify: `tests/test_factor_expression.py`

**Interfaces:**
- Consumes the validated expression from Task 1 and a pandas DataFrame.
- Produces a pandas Series with the original index for `RANK`, `DELAY`, `RETURNS`, `STDDEV`, `CORRELATION`, `+`, `-`, `*`, `/`, and unary `+`/`-`.

- [ ] **Step 1: Add failing execution tests using a real synthetic MultiIndex frame**

```python
import numpy as np


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

    expected = pd.Series(
        [np.nan, 1.0, 1.0, np.nan, 1.0, 1.0], index=index, name="factor"
    )
    pd.testing.assert_series_equal(result, expected)


def test_rank_is_cross_sectional_by_date() -> None:
    index = pd.MultiIndex.from_product(
        [["A", "B"], pd.date_range("2026-01-01", periods=2)],
        names=["symbol", "date"],
    )
    frame = pd.DataFrame({"CLOSE": [1.0, 3.0, 2.0, 4.0]}, index=index)

    result = parse_factor("RANK(CLOSE)").evaluate(frame)

    assert result.loc[("A", "2026-01-01")] == 0.0
    assert result.loc[("B", "2026-01-01")] == 1.0
    assert result.loc[("A", "2026-01-02")] == 0.0
    assert result.loc[("B", "2026-01-02")] == 1.0
```

- [ ] **Step 2: Run the new tests to verify they fail**

Run: `uv run pytest tests/test_factor_expression.py -q`
Expected: FAIL because evaluation is not implemented.

- [ ] **Step 3: Implement registry-backed execution**

Use a small immutable operator specification containing arity, lookback function, and evaluator. Group rolling operations by the `symbol` level and require the expected `symbol`/`date` MultiIndex for time-series operators. Implement `RANK` as per-date percentile rank with `method="average"` and `pct=True`; use `shift`, `rolling.std(ddof=1)`, and rolling correlation.

- [ ] **Step 4: Add failure tests for invalid runtime inputs**

```python
def test_evaluate_rejects_missing_columns() -> None:
    with pytest.raises(KeyError, match="CLOSE"):
        parse_factor("CLOSE").evaluate(pd.DataFrame({"OPEN": [1.0]}))


def test_time_series_operator_requires_symbol_date_multiindex() -> None:
    with pytest.raises(ValueError, match="MultiIndex"):
        parse_factor("DELAY(CLOSE, 1)").evaluate(pd.DataFrame({"CLOSE": [1.0]}))
```

- [ ] **Step 5: Run all focused tests**

Run: `uv run pytest tests/test_factor_expression.py -q`
Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add packages/alpha/src/alpha_research/factor_expression.py tests/test_factor_expression.py
git commit -m "feat: execute factor expressions with pandas"
```

### Task 3: Document the DSL and run repository quality gates

**Files:**
- Create: `docs/alpha/concepts/factor-expression.md`
- Modify: `docs/alpha/concepts/index.md` if an index exists and needs the new page

- [ ] **Step 1: Write usage documentation**

Document the supported syntax, `(symbol, date)` index requirement, metadata methods, security boundary, and a worked example:

```python
factor = parse_factor("RANK(RETURNS(CLOSE, 20))")
factor.required_columns()
factor.lookback()
factor.evaluate(frame)
```

- [ ] **Step 2: Run documentation and diff checks**

Run: `git diff --check` and `python scripts/dev/check_documentation.py`
Expected: both exit 0.

- [ ] **Step 3: Run affected static checks and tests**

Run: `uv run ruff check packages/alpha/src/alpha_research/factor_expression.py tests/test_factor_expression.py`

Run: `uv run pytest tests/test_factor_expression.py -q`

Expected: both exit 0.

- [ ] **Step 4: Run the full repository test suite required by the repository rules**

Run: `uv sync --locked --all-groups`

Run: `uv run ruff check .`

Run: `uv run pytest`

Expected: commands exit 0; report any pre-existing failure separately rather than suppressing it.

- [ ] **Step 5: Commit documentation and final verification**

```bash
git add docs/alpha/concepts/factor-expression.md docs/alpha/concepts/index.md
git commit -m "docs: document factor expression DSL"
git diff --check origin/main...HEAD
git status --short --branch
```
