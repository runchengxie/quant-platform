# 显式停牌估值

语言：简体中文 · [English](suspension-valuation.md)

日频适配层保留 Core 的可选估值策略。默认规则仍要求当日报价，才能提供完整估值证据。沿用的旧价不会变成可执行报价。

在使用复权价格、按日顺序执行 NAV 核算且不含公司行为事件的场景，可以声明 `valuation_policy="suspended_last_quote"`，指定独立的 `valuation_suspension_col` 和正整数 `valuation_max_stale_sessions`。Core 只在停牌字段明确为布尔真、旧价与财务账本中的先前真实报价一致、且未超过交易日年龄限制时，认可缺价持仓的策略估值。未知状态仍不完整。可交易、涨跌停、价格或流动性字段不能兼作停牌证据。

将 Core 的 `ExecutionSimConfig` 传给 `quant_platform.backtest.engine_daily.build_daily_request`，并设置 `price_basis="adjusted"`。适配层保留配置，把财务状态和政策校验交由 Core 处理。不会填充可执行报价、另建现金账本，也不会替具体投资产品批准估值假设。

读取结果时，应将 `valuation_marks.current_marks`、`missing_symbols` 与 `policy_valued_symbols`、`policy_quote_dates`、`policy_quote_ages`、`unresolved_symbols` 分开。`endpoint_complete` 表示在已声明策略下完整。原始及规范化摘要会记录策略和沿用旧价的端点数量，不应将其描述为全部使用当日报价。

原始股数口径、公司行为、理想成交和容量模式不支持这一选项，调用会被拒绝。旧价可能偏离可实现价值。该策略不能证明供应商真实性、历史发布时间、退市回收价值或成交质量。调用方应在发布结果时保留来源和时间证据。

详细语义由 Core 的[输入与估值契约](https://github.com/runchengxie/quant-backtest-engine/blob/main/docs/product/daily-inputs.zh-CN.md)维护。历史迁移记录和既有固定版本运行仍使用各自原始环境。
