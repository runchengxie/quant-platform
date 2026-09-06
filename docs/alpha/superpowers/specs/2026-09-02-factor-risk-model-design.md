# 因子风险模型设计

## 目标

增加通过 PIT 安全检查、与框架无关的因子风险估计，后续可以供组合优化和归因使用，同时保持 alpha 研究与组合维护方解耦。

## 设计

The caller supplies as-of exposures, historical factor returns, and historical specific returns. The risk model computes factor covariance with optional diagonal shrinkage, asset-specific risk, and the projected asset covariance `X F X' + D`.

The implementation does not infer factor returns, optimize portfolios, or import `portfolio_backtester`. All history must be at or before the explicit `as_of` date.

## 不在本次范围内

- no proprietary RQData data retrieval;
- no optimizer integration in this PR;
- no factor-selection policy;
- no claim that this simple covariance estimator is production-optimal;
- no external risk-model object in public artifacts.
