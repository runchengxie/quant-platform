# 成本口径

语言：简体中文 · [English](cost-breakdown.md)

`CostBreakdown` 为回测结果提供统一的费用视图：

| 字段 | 含义 |
|------|------|
| `fee_cost` | 成本模型返回值，通常表示显式费用 |
| `slippage_cost` | 独立滑点模型返回值 |
| `total_cost` | 两者之和 |

当前 `DetailedTradeFeeModel` 同时计算佣金、税费、过户费和内置滑点。使用该模型时，内置滑点会进入 `fee_cost`。因此 `fee_cost` 不能一概解释为纯显式费用。

同时启用明细费用模型的内置滑点和独立滑点模型，会叠加两套滑点假设。需要把费用和滑点分列时，应把 `DetailedTradeFeeModel` 的 `buy_slippage_bps` 与 `sell_slippage_bps` 设为 0，再通过独立滑点模型计算 `slippage_cost`。

报告应保存成本模型、滑点模型和全部参数。当前 `CostBreakdown` 已提供佣金、税费、过户费、价差、临时冲击、永久冲击、机会成本和融资成本分项。使用实际知道的分项构造结果时，使用 `from_components`，以保持汇总字段和分项总和一致。
