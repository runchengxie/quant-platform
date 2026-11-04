# 带符号权重的模拟组合优化

[English](signed-paper-optimization.md)

`quant_platform.portfolio.signed_optimization` 用于合成数据或模拟研究，权重以
组合净资产比例表示，可正可负。它独立于现有只做多优化器，不证明可交易性、融资、
融券可得性、券源锁定或账户资格。所有结果都包含 `paper_only=True` 和
`executable=False`，优化成功也不例外。

`SignedOptimizationRequest` 要求显式提供 pandas Series：`expected_returns`、
`current_weights`、`lower_bounds`、`upper_bounds`、`trade_costs`、`borrow_costs`、
`holding_costs`，以及方形 `covariance` DataFrame 和 `factor_loadings` DataFrame。
所有资产索引须唯一、无缺失且顺序完全一致。数值必须有限。协方差须对称、半正定。
缺失成本会被拒绝，零成本也必须显式声明为假设。

`horizon_days` 必须是正整数，收益、协方差、借券及持仓成本率都对应这个持有期。
`units` 必须为 `"horizon_decimal"`。收益和成本以净资产小数比例表示，协方差单位
为收益小数的平方。交易成本按交易净资产绝对额一次性收取，不自动换算持有期。
调用者负责各输入口径一致，并在非空 `assumptions` 字符串中记录假设。
两个时间戳均须包含时区，`information_time <= decision_time` 表示全部输入的最晚
信息时间不晚于决策时间。该检查不能独立核实历史可得性或消除估计偏差。

调用 `optimize_signed_paper(request)`。目标为最小化
`risk_aversion / 2 * w.T @ covariance @ w - expected_returns @ w`，再加
`trade_costs @ abs(w-current_weights)`、`borrow_costs @ max(-w,0)` 和
`holding_costs @ abs(w)`。所有成本率须非负，仅代表假设。约束包括逐资产上下限、
`sum(w) == net_target`、`sum(abs(w)) <= gross_limit`，以及 `factor_bounds`
中具名因子暴露的有限上下界。金额中性不等于 beta 中性。需要后者时应提供 beta
载荷列和明确暴露约束。总敞口是上限，不是强制投资额或最低敞口。系统不据此推算
现金账户或现金收益。

凸规划通过辅助变量表示绝对值，先用 SciPy HiGHS 线性规划寻找可行起点，再用带
解析梯度的 SLSQP 求解。成功结果包含实际权重、总敞口、净敞口、交易净资产绝对额
之和（不除以二）、扣费前预期收益、方差、各项假设成本、全部因子暴露，以及非负
约束违反量 `residuals`，容差为 `1e-7`。仅当实际总敞口大于 `1e-7` 时，`active`
才为真。零敞口明确标为非投资状态。

`infeasible` 表示可行性线性规划确认约束不相容。`numerical_failure` 表示求解失败
或残差超限。两者都不返回权重或经济评分，也没有替代组合。SLSQP 成功只是该凸模型
的数值解，不是执行许可。稠密求解器面向小规模研究。

本模型未覆盖整股交易、保证金机制、融资与现金账户、市场冲击、借券召回风险或
历史券源证据。真实执行仍须独立的数据证据、风险检查和执行契约。
