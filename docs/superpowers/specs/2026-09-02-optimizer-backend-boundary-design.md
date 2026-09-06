# 优化器后端边界设计

## 目标

建立由 `portfolio-backtester` 维护的稳定组合优化边界，让外部求解器可以接受评估，同时避免泄漏框架对象，也不替换现有 A 股执行语义。

## 设计

`PortfolioOptimizationRequest` carries pandas/native inputs: return history, optional expected returns, optional previous/benchmark weights, long-only bounds, and covariance shrinkage. `PortfolioOptimizationResult` returns only normalized weights and JSON-compatible diagnostics.

`OptimizerRegistry` provides explicit registration with no plugin discovery. Initial native baselines are equal weight and the repository's existing HRP implementation. Third-party adapters remain future optional dependencies and must emit the canonical result.

## 约束

- No new runtime dependency in this PR.
- Native baselines remain deterministic and framework-neutral.
- No alpha-research or strategy-pipeline runtime import.
- Long-short optimization is outside this first boundary.
- A-share order execution, T+1, fees, market rules, and capacity remain in existing replay/execution layers.
- Future external adapters require fixed-scenario differential evidence and rollback instructions.
