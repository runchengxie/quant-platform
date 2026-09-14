# FactorExpression 安全公式 DSL 设计

## 目标

为 `alpha_research` 增加一个策略无关、可静态检查的因子公式表达层，让研究员和后续 Agent 能用简短公式构造因子，同时保留现有平台的 PIT、lookback 和证据链边界。

## 范围

本切片只实现 `FactorExpression`、算子注册表、语法/语义校验、静态元数据和 pandas 执行器。因子持久化、`FactorArtifact`、Agent tool registry、报告 facade 和图形 UI 属于后续切片。

## 公开接口

```python
from alpha_research.factor_expression import (
    FactorExpression,
    OperatorRegistry,
    parse_factor,
)

expression = parse_factor("RANK(RETURNS(CLOSE, 20)) * RANK(-STDDEV(CLOSE, 20))")
expression.required_columns()  # ("CLOSE",)
expression.lookback()  # 20
result = expression.evaluate(frame)
```

`frame` 是包含列名和 `(symbol, date)` MultiIndex 的 pandas DataFrame。计算结果是带原索引的 pandas Series。表达式只消费输入列，不负责数据加载、资产解析或发布。

## 安全边界

- 输入必须是单个表达式，不接受语句、赋值、导入或任意 Python 模块。
- 使用 Python `ast` 解析后只允许名称、数值常量、受限函数调用、算术二元运算和一元正负号。
- 函数名来自 `OperatorRegistry` 白名单。禁止属性访问、下标访问、lambda、comprehension、字符串拼接、关键字参数和双下划线名称。
- 不使用 `eval` 或 `exec`。执行器直接解释经过验证的语法树。
- `DELAY`、`RETURNS`、滚动统计等时间序列算子的窗口必须是正整数常量。不支持负窗口或未来引用。
- 时间序列执行要求每个 symbol 的 date 升序排列，输入不满足时明确拒绝。
- 公式源文本、AST 节点数量和 AST 深度都有上限，超限统一返回 `ValueError`。

## 第一批算子

| 算子 | 语义 | 窗口 |
| --- | --- | --- |
| `RANK(x)` | 每个 date 横截面百分位排名 | 无 |
| `DELAY(x, n)` | 每个 symbol 向后移动 n 个观测 | n |
| `RETURNS(x, n)` | `x / DELAY(x, n) - 1` | n |
| `STDDEV(x, n)` | 每个 symbol 的滚动样本标准差 | n |
| `CORRELATION(x, y, n)` | 每个 symbol 的滚动相关系数 | n |

算术运算支持 `+`、`-`、`*`、`/`，除法按 pandas 语义处理。无穷值和缺失值由下游研究诊断负责。跨截面 `RANK` 不增加 lookback。

## 静态元数据

验证后的表达式需要能返回：

- 所需输入列，按首次出现顺序去重。
- 最大 lookback。
- 稳定的规范表达式文本，供后续 digest/receipt 使用。
- 操作符名称集合，便于能力声明和审计。

## 测试策略

- 用合成 MultiIndex DataFrame 验证时间序列窗口和横截面 rank 的真实结果。
- 验证列依赖和最大 lookback。
- 对 `import`、属性访问、`eval`/`exec`、下标、关键字参数、未知算子、非正窗口和语句注入进行拒绝测试。
- 保持测试不依赖真实数据、外部服务或 PandaAI 包。

## 非目标

- 不复制或导入 PandaFactor 实现。
- 不支持任意 Python 函数、用户自定义 Python 代码或运行时插件加载。
- 不在本切片内引入新的第三方依赖。
