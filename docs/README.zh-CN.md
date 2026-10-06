# quant-platform 文档

语言：简体中文 · [English](README.md)

> status: active
> owner: quant-platform
> audience: human and agent
> last_verified: 2026-09-25
> source_of_truth: yes
> superseded_by: n/a

这里集中记录 `quant-platform` 的输入约定、执行假设、输出契约和开发检查。

如果你第一次接触这个项目，建议先阅读下面的新人入口。它们使用合成数据和最小示例，帮助你先跑通完整流程，再进入详细的接口和契约说明。

## 新人入口

1. [平台概览](concepts/platform-overview.zh-CN.md)
2. [安装与环境](getting-started/installation.zh-CN.md)
3. [运行第一个回测](getting-started/first-backtest.zh-CN.md)
4. [读取回测结果](getting-started/understanding-results.zh-CN.md)
5. [术语表](reference/glossary.zh-CN.md)

## 深入阅读顺序

1. [根目录 README](https://github.com/runchengxie/quant-platform/blob/main/README.md)
2. [常用入口](guides/entry-points.zh-CN.md)
3. [通用多策略袖套组合构造](guides/sleeve-portfolio.md)
4. [组合式回测规范](concepts/backtest-spec.md)
5. [回测配置解析](concepts/backtest-configuration.md)
6. [回测后端边界](concepts/backend-architecture.md)
7. [机器可读框架状态账本](https://github.com/runchengxie/quant-platform/blob/main/docs/framework-integration-ledger.yml)
8. [成本与执行假设](concepts/execution-costs.md)
9. [执行容量与每日净值模拟](guides/execution-simulation.md)
10. [已退出公开发布的风格因子回测片段](concepts/style-factor-portfolio-weighting.md)
11. [AFML 仓位与策略风险](concepts/afml-sizing-and-risk.md)
12. [换手率口径](concepts/turnover.md)
13. [成本口径](concepts/cost-breakdown.zh-CN.md)
14. [因子收益和风险归因](concepts/factor-attribution.md) · [English](concepts/factor-attribution.en.md)
15. [公司行动账本](corporate-action-ledger.md) · [English](corporate-action-ledger.en.md)
16. [回测结果解读](concepts/backtest-interpretation.md)
17. [市场基准阶梯](concepts/benchmark-ladder.md)
18. [持仓输出约定](reference/outputs/positions.zh-CN.md)
19. [回测输出契约](reference/outputs/backtest-outputs.md)
20. [执行分配参考资产](reference/allocation-reference.zh-CN.md)
21. [公开 API](reference/public-api.zh-CN.md)
22. [测试和质量检查](testing.zh-CN.md) · [English](testing.md)
23. [微观结构开发说明](microstructure/README.md)
24. [可选 Rust 模拟内核](development/microstructure-rust.md)
25. [会计与执行路线图](governance/accounting-execution-roadmap.md)
26. [网格回测辅助函数](grid-support.md)
27. [历史迁移材料](migration/legacy-materials/README.md)
28. [运行时内核契约](architecture/runtime-kernel.zh-CN.md)
29. [Barra-like 风险模型内核](risk-model-kernel.zh-CN.md)
30. [组合执行性能分析记录](development/portfolio-execution-profiling-2026-09.zh-CN.md)

编码代理默认读取根 README、本页和一个与任务相关的分类目录，不递归读取全部 Markdown 文件。

## 事实来源

| 内容 | 代码位置 |
| --- | --- |
| 顶层公开入口 | `packages/portfolio-backtester/src/portfolio_backtester/__init__.py` |
| 通用多袖组合构造 | `packages/portfolio-backtester/src/portfolio_backtester/sleeve_portfolio.py` |
| 回测规范 | `packages/portfolio-backtester/src/portfolio_backtester/backtest_spec.py` |
| 回测配置解析 | `packages/portfolio-backtester/src/portfolio_backtester/backtest_config.py` |
| 高层 API | `packages/portfolio-backtester/src/portfolio_backtester/api.py` |
| 输入和输出契约 | `packages/portfolio-backtester/src/portfolio_backtester/contracts.py` |
| 执行领域契约 | `packages/portfolio-backtester/src/portfolio_backtester/execution_contracts.py` |
| 执行分配参考资产 | `packages/portfolio-backtester/src/portfolio_backtester/allocation_reference.py` |
| 后端协议与规范化结果 | `packages/portfolio-backtester/src/portfolio_backtester/backends/` |
| 成本与滑点 | `packages/portfolio-backtester/src/portfolio_backtester/execution.py` |
| 持仓回放 | `packages/portfolio-backtester/src/portfolio_backtester/position_backtest.py` |
| 晋级证据成交模拟 | `packages/portfolio-backtester/src/portfolio_backtester/promotion_sidecar.py` |
| 测试入口 | `scripts/dev/run_tests.sh` |
| 网格回测辅助函数 | `packages/portfolio-backtester/src/portfolio_backtester/grid_support.py` |
| 微观结构模拟接口 | `packages/microstructure/src/ticknet/simulator/` |
| Rust 模拟内核 | `packages/microstructure/rust/src/lib.rs` |

代码、测试和文档发生冲突时，应先核对当前实现，再在同一次改动中修正文档。

## 文档边界

本仓库记录通用组合构造和回测行为。数据下载、因子研究、模型训练、具体策略规则、任务编排和券商下单由调用方负责。

历史迁移记录保留在 PR、发布说明或维护记录中。用户指南优先说明当前版本的输入、行为和输出。

`migration/legacy-materials/` 下的只读副本用于历史对照，不是当前 API、受支持的开发入口或现行行为的事实源。先查当前职责和迁移文档。只有需要复现历史实现或核对迁移一致性时再打开旧副本。跨仓历史索引和逐项清单由私有 `quant-research` 维护。

## 历史归属

- [组合回测命名空间](namespace-migration.md)
- [DailyWatch20 组合职责归属](ownership-migration.md)
- [旧仓再资格样本外（OOS）对照桥](guides/incumbent-requalification-oos-controls.md)
