# 分钟执行情景

[English](minute-execution.en.md)

`portfolio_backtester.minute_execution` 提供独立、可选的长仓执行情景。它使用原始价格和明确的公司行动，不改变现有日频 API。分钟成交均价是历史成交额除以股数、再限制在该分钟 OHLC 范围内的代理价格，不能据此认定真实委托能成交，更不能识别自身订单的冲击。

入口为 `MinuteExecutionConfig` 和 `simulate_minute_execution(targets, bars, config, corporate_actions=())`。结果包含 `daily`、`orders`、`fills`、`holdings` 与 `summary`。持仓日报仅列正持仓，只有该日期存在于 `daily` 时，缺少证券持仓行才表示零持仓。

`targets` 是完整目标快照，包含 `decision_time`、`entry_time`、`symbol`、`weight`。时间必须为带时区的 pandas Timestamp，下单必须晚于决策。未列出的旧持仓目标为零。新目标取消前一批仍未完成的订单。订单股数按下单之前已经可用的参考价确定，不能读取未来分钟安排释放数量。

`bars` 包含 `symbol,time,open,high,low,close,volume,amount,up_limit,down_limit,tradable`。价格和成交额用元，成交量用股。`time` 是行情可用时点。可另外提供 `interval_start`，表示该行成交量覆盖区间的开始。未提供时保守使用 `time-1分钟`。只有整个成交区间开始时已超过子单释放和延迟的记录才可成交。接收延迟不能把订单生效前的成交量变成可用流动性。

释放计划由 `release_slices` 和 `execution_minutes` 预先确定，时长按墙钟分钟计算，包含午休。每分钟同一证券的订单共享参与率上限。卖出先于买入，买入受含费现金约束。模型检查 T+1、配置的整手及方向对应的涨跌停触及。触及涨停不模拟买入，触及跌停不模拟卖出。整数零股可在整笔清仓且流动性足够时卖出。小数权益保留并单列，不假定能卖出。

公司行动使用已有 `CorporateAction` 合约。在登记日收盘捕获持股，除权日建立应收现金及股票，到账日或上市日转为可用。尚未上市的送股计入目标敞口但不可卖。除权日首条新行情之前的参考价按已知普通分配调整，此时订单标为 `synthetic_ex_reference`，不能将其称为观察到的报价。重整转增、配股及其他特殊分配需由调用方核验，不能套用普通送股。

现金、持仓及待上市股票缺少当日有效估值时，保留缺失净值与证券诊断。调用方还应核对收盘报价、完整交易日历、历史资格、全部公司行动及输入版本。`commission_minimum_cny` 默认零，可选最低佣金按母单聚合，只在首次成交或累计佣金超过最低值时增量收费。`sell_tax_bp` 单列卖出税费，必须不大于卖出总费率。无成交不收费，现金不足时不能执行含费买入或亏现金的卖出。按母单计最低佣金是假设，真实券商可能按子单收费，需用交割单校准。模型没有真实排队、隐藏流动性或永久冲击。
