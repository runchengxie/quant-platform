# quant-platform

[English README](README.md)

Platform 0.1.0 支持 Python 3.12 和 3.13，依赖 Engine core 0.1.0，并显式安装
minute、cost、scenario 扩展及 SDK 0.3.0。两个包都通过固定 Git 子目录依赖解析到
已合并的 Engine 提交 `19a2ae714b567fc1a46cf996fa5a86a90138bc44`，不要求 PyPI 发布。
原有分钟、公司行动、冲击和基础证据接口直接导出同一个 Engine 类和函数。
统计风险、通用 QP 优化、因子流程及尚未迁移的集成仍属于 Platform。
仅使用 SDK 的 Rust 会话适配器仍需显式选择。不支持的 execution-aware 证据仍为 false。


`quant-platform` 是可复用的量化研究框架，提供回测、组合构造、风险分析、执行模拟和公共研究产物契约。它面向研究代码与工具开发，不保存真实策略数据、专有特征、凭证或研究结论。

本项目属于 Quant Research 项目系列，与同系列的数据平台、研究控制面、回测运行时和报告交付项目各自独立维护、按接口协作。

[在线文档](https://runchengxie.github.io/quant-platform/)

语言规范见 [English](docs/LANGUAGE_POLICY.md) · [简体中文](docs/LANGUAGE_POLICY.zh-CN.md)

## 快速开始

项目需要 Python 3.12 或 3.13，并使用 `uv` 管理环境。

```bash
uv sync --locked --all-groups
```

安装后可以直接运行[第一个回测示例](docs/getting-started/first-backtest.md)。示例使用合成数据，不需要真实行情或数据供应商凭证。

## 接下来读什么

- [平台概览](docs/concepts/platform-overview.zh-CN.md)介绍框架能力
- [安装与环境](docs/getting-started/installation.zh-CN.md)说明依赖和可选组件
- 按[第一个回测](docs/getting-started/first-backtest.zh-CN.md)运行合成示例
- 用[结果说明](docs/getting-started/understanding-results.zh-CN.md)核对输出
- Alpha 模块边界见[后端说明](docs/alpha/concepts/framework-backends.md)
- [执行模拟指南](docs/guides/execution-simulation.md)和[AFML 仓位与风险](docs/concepts/afml-sizing-and-risk.md)
- 更多接口、契约和开发说明见[文档总览](docs/README.zh-CN.md)

## 项目边界

本项目维护策略无关的量化通用能力。策略研究假设、专有特征和晋升规则属于私有研究层。市场数据生产由 [`quant-market-data-platform`](https://github.com/runchengxie/quant-market-data-platform) 负责，研究状态与策略专属逻辑由私有 `quant-research` 负责，已提交任务的持久化执行由 [`quant-backtest-runtime`](https://github.com/runchengxie/quant-backtest-runtime) 负责。

安装选项、依赖范围、项目边界和各模块的技术细节见 `docs/`。本项目保留现有 `portfolio_backtester` Python 导入名称，以兼容使用它的研究代码。

## 独立 Rust 引擎

[quant-backtest-engine](https://github.com/runchengxie/quant-backtest-engine) 提供独立的 Rust 库和 CLI，通过薄适配层调用 NautilusTrader。现有 Python 后端继续受支持。引擎职责、已验证能力和迁移条件见[后端边界](docs/concepts/backend-architecture.md#独立-rust-引擎)。
