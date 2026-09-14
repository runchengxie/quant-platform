# FactorExpression 安全公式 DSL

`alpha_research.factor_expression` 提供一个策略无关的因子公式层。它借鉴了量化平台常见的公式体验，但只解释经过白名单校验的表达式，不执行任意 Python，也不负责加载数据或写入研究产物。

## 基本用法

```python
from alpha_research import parse_factor

factor = parse_factor("RANK(RETURNS(CLOSE, 20))")

factor.required_columns()  # ("CLOSE",)
factor.lookback()  # 20
factor.operators()  # ("RANK", "RETURNS")
result = factor.evaluate(frame)
```

`frame` 必须是 pandas DataFrame。使用时间序列算子时，索引需要包含名为 `symbol` 和 `date` 的 MultiIndex 层，每个 symbol 的行必须按 date 升序排列，否则执行会被拒绝。

## 支持的算子

| 算子 | 说明 |
| --- | --- |
| `RANK(x)` | 按 date 做横截面百分位排名 |
| `DELAY(x, n)` | 每个 symbol 向后移动 `n` 个观测 |
| `RETURNS(x, n)` | `x / DELAY(x, n) - 1` |
| `STDDEV(x, n)` | 每个 symbol 的滚动样本标准差 |
| `CORRELATION(x, y, n)` | 每个 symbol 的滚动相关系数 |

表达式支持 `+`、`-`、`*`、`/` 以及一元正负号。窗口 `n` 必须是正整数常量，表达式的 `lookback()` 返回所有算子窗口中的最大值。

## 安全边界

公式通过 Python AST 解析，但 AST 只用于识别语法结构。可执行结构限于输入列、数值常量、白名单函数和基本算术。导入、属性访问、下标访问、关键字参数、lambda、`eval`、`exec`、双下划线名称和未来窗口都会被拒绝。

因此，`FactorExpression` 适合由研究员或 Agent 生成公式。它仍然需要接入调用方的数据版本、PIT 和研究证据契约后，才能用于正式研究结论。
