# quant-platform

`quant-platform` 是可复用的量化研究框架，提供回测、组合构造、风险分析、执行模拟和公共研究产物契约。它面向研究代码与工具开发，不保存真实策略数据、专有特征、凭证或研究结论。

本项目属于 Quant Research 项目系列，与同系列的数据平台、研究控制面、回测运行时和报告交付项目各自独立维护、按接口协作。

[在线文档](https://runchengxie.github.io/quant-platform/)

## 快速开始

项目需要 Python 3.12 或更新版本，并使用 `uv` 管理环境：

```bash
uv sync --locked --all-groups
```

安装后可以直接运行[第一个回测示例](docs/getting-started/first-backtest.md)。示例使用合成数据，不需要真实行情或数据供应商凭证。

## 接下来读什么

- [平台概览](docs/concepts/platform-overview.md)：了解框架包含哪些能力
- [安装与环境](docs/getting-started/installation.md)：了解依赖和可选组件
- [第一个回测](docs/getting-started/first-backtest.md)：跟着示例跑通流程
- [读取回测结果](docs/getting-started/understanding-results.md)：了解输出内容
- Alpha 模块边界见[后端说明](docs/alpha/concepts/framework-backends.md)
- [执行模拟指南](docs/guides/execution-simulation.md)和[AFML 仓位与风险](docs/concepts/afml-sizing-and-risk.md)
- [文档总览](docs/README.md)：按主题查找接口、契约和开发说明

## 项目边界

本项目维护策略无关的量化通用能力。策略研究假设、专有特征和晋升规则属于私有研究层。市场数据生产由 [`quant-market-data-platform`](https://github.com/runchengxie/quant-market-data-platform) 负责，研究状态与策略专属逻辑由私有 `quant-research` 负责，已提交任务的持久化执行由 [`quant-backtest-runtime`](https://github.com/runchengxie/quant-backtest-runtime) 负责。

安装选项、依赖范围、项目边界和各模块的技术细节见 `docs/`。本项目保留现有 `portfolio_backtester` Python 导入名称，以兼容使用它的研究代码。
