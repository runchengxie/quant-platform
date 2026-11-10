# 日频执行消费接口

[English](engine-daily.md)

Platform 0.3.0 使用同一已合并 Engine 提交 `ad0895f1c2015eb31bd364b40741b0f7cd6e0048` 的 Core 0.3.0 和 SDK 0.3.0。日频金融计算、诊断腿与区间核算、旧交易核算、费用模型及结果类由 Engine 统一维护。Platform 负责目标选择、在原消费边界获取供应方日历、研究统计和结果包发布。

## 旧研究工作流

native、sequenced、position 和 top-k 的既有参数继续可用。日频和持仓包装函数返回原来的 Engine 结果类。原始金融表及 `UnifiedLedger` 的八张表均来自该计算所有者。Platform 按原公式恢复区间收益的分布、回撤时长、退出延迟、年度及上下半年统计，同时保留八个金融区间汇总字段和 schema/config/period/skipped 元数据。

这些历史统计描述旧计算路径的原始收益。沿用旧价格估值时，原始收益未必具有完整估值证据，不能代替中立产品的保守汇总。旧接口仍保留原有的上市状态和容量选项执行限制。新的严格配置会拒绝不支持的组合。执行资格窗口的结束时间并不代表延迟成交的实际截止时间。

## 显式中立请求

`quant_platform.backtest.engine_daily.build_daily_request` 接收已经选定的持仓、价格、显式 `ExecutionCalendar`、研究时钟和 Engine 的 `ExecutionSimConfig`。它转换日期并保留明确指定的列，不获取日历、不构造目标，也不额外加入默认流动性列。`run_daily` 调用 Engine，再添加作用范围明确的研究统计。

`quant_platform.backtest.engine_clocks.to_execution_clocks(value: ResearchClock | Mapping[str, Any]) -> ClockSet` 使用精确的 UTC 纳秒字符串。entry 取已提供资格边界中的较晚时间。研究契约没有提供观测证据时，available/effective/report 保持未知。原 native v1/v2 整数时钟契约不变。

## 规范化产品结果

```python
from quant_platform.backtest.engine_results import to_canonical_result

partial_view = to_canonical_result(product_result)
full_view = to_canonical_result(product_result, artifact_root=owned_output_directory)
```

兼容签名为 `to_canonical_result(result: ProductResult, *, artifact_root: Path | None = None) -> CanonicalBacktestResult`。单参数调用只消费已提供的规范化证据，不补造完整账本。显式可信根目录允许校验原始产物的相对 URI、媒体类型、SHA256 和 schema，然后解码原有八张账本表。不会猜测当前目录、联网获取、任意导入模块或执行 dtype 文本。未知 schema/dtype 和越界路径均会失败。

原始表齐全与估值证据完整是两个独立事实。`performance.net_return` 来自保守的 `daily_return`，期初或期末缺少估值时仍为未知。原收益保留为 `raw_executed_return`，并附作用范围说明。缺失价格后的恢复区间仍是未知，下一完整观测区间才可重新得到支持。产品汇总原样保留，不会将未知累计收益替换成零或旧研究统计中丢弃缺失值后的结果。

`metadata.product_result` 保留每张表的 available/unavailable 声明和原因。可用的空表与不可用证据不同。`metadata.full_owner_artifact_verified` 表示原始产物已验证。`metadata.execution_aware` 还要求估值证据完整。结果包发布拒绝 `execution_aware=False`。多决策结果仍需要后续支持逐决策时钟的结果包 schema，现有单时钟发布接口会拒绝它。

## 能力和兼容边界

原始 Rust 会话适配器仍有既定限制，不会补造统一账本，也不会自动改走 Python。显式验证后的 Rust 转换保留原表及 `execution_aware=False`。区间诊断收益不代表具备日频现金、成交或借券保证金能力。公司行为应收项目仍可从原始表读取。旧现金加持仓账本的表示方式不证明完整应收项目勾稽。

别名至少保留两个次版本周期，并等待每个登记使用方完成迁移。Platform 和合成样例通过，不等于固定版本的 Runtime/Go/Python 环境或旧检查点已迁移。它们仍须保留完整原发布依赖闭包。参阅 [C 所有权映射](https://github.com/runchengxie/quant-platform/blob/main/docs/migration/engine-provider-c.json)、历史 [A](https://github.com/runchengxie/quant-platform/blob/main/docs/migration/engine-provider-a.json) 与 [B](https://github.com/runchengxie/quant-platform/blob/main/docs/migration/engine-provider-b.json) 记录，以及 [Engine 日频契约](https://runchengxie.github.io/quant-backtest-engine/product/daily-inputs.zh-CN/)。

## 应收权益的表示范围

当所有者日表含未支付现金或股票应收权益时，历史八表无法表示其完整财富。转换器在 `metadata.owner_result` 保留已验证的原始 daily/actions/holdings 和全部八表，但将 canonical 日账本及统一账本标为不可用，并设置 `execution_aware=False`。`canonical_ledger_limitation` 区分未支付与未知应收权益。未知或非有限数值绝不按零处理。实际支付转移完全保留所有者输出，不补造现金、不修改绩效或摘要。这是表示范围限制，不是新增的市场损失或金融失败。

[消费层迁移契约](../migration/provider-c-consumer.zh-CN.md) 记录实现与验收范围。
