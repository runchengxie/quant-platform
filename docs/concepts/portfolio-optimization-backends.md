# 组合优化后端边界

`portfolio-backtester` 在接入第三方求解器前，先提供与框架无关的优化请求和结果边界。

## 设置这层边界的原因

仓库已经负责组合构造、HRP、换手、执行成本、容量、暴露和 A 股回放语义。
因此，外部优化器应接入由 owner 控制的边界，不应把 CVXPY、PyPortfolioOpt、cvxportfolio、Riskfolio 或 Ricequant 专用对象暴露给调用仓库。

前两个后端是有意保持简单的基线：

- `native.equal_weight`
- `native.hrp`

它们提供固定的参考行为，并复用现有 HRP 实现，不引入新的求解器依赖。

## 稳定请求

`PortfolioOptimizationRequest` 只携带平台类型：

- 历史收益。
- 可选预期收益。
- 可选上一期权重。
- 可选基准权重。
- 只做多的权重边界。
- 协方差收缩。

现在加入可选 alpha、上一期权重和基准权重输入，是为了让后续约束优化器可以直接复用请求类型。
原生基线不会假装使用自身不需要的输入。

## 稳定结果

`PortfolioOptimizationResult` 包含：

- 后端名称。
- 标准化后的组合权重。
- 兼容 JSON 的诊断信息。
- 带版本的结果 schema。

校验会强制检查资产身份、有限权重、权重和为 1、只做多语义和请求边界。

## 采用顺序

1. 保留等权、排名、sleeve 和 HRP 作为基线。
2. 为优化器边界增加固定场景测试。
3. 评估 PyPortfolioOpt 适配器，用于常规约束优化。
4. 完成许可证审查后，评估 cvxportfolio，用于考虑成本和多期约束的研究。
5. 在 Riskfolio-Lib 注册明确的使用场景前，将其保留为研究比较后端。
6. 将 RQOptimizer 作为基准、风格和行业、tracking error、换手和交易成本约束的领域设计参考，
   不把专有对象放入公开契约。

新适配器必须保持可选，输出 `PortfolioOptimizationResult`，记录求解器和版本，提供固定场景差异证据，
并确保缺少该依赖时原生基线仍可运行。
