# quant-platform

`quant-platform` 提供可复用的量化研究与组合基础能力，包括回测、组合构造、风险分析、执行模拟、微观结构实验和研究产物契约。项目面向研究代码与工具开发，不保存真实策略输入、专有特征、凭证或研究结论。

[在线文档](https://runchengxie.github.io/quant-platform/)

## 快速开始

项目要求 Python 3.12 或更新版本，使用 `uv` 安装锁定依赖：

```bash
uv sync --locked --all-groups
uv run ruff check .
uv run pytest -q
```

项目保留 `portfolio_backtester` Python 命名空间，供现有研究代码兼容使用。常用入口和示例见[文档总览](docs/README.md)，Alpha 模块边界见[后端说明](docs/alpha/concepts/framework-backends.md)。

微观结构模型和模拟器位于 `packages/microstructure/`。Python 实现是默认后端。需要 Rust 撮合与批量回放时，可按[微观结构开发说明](docs/development/microstructure-rust.md)单独构建并安装原生扩展。

## 项目边界

- `quant-platform`：通用回测、组合、风险、执行模拟、微观结构机制和公开研究产物接口
- `quant-market-data-platform`：数据接入、标准化、质量治理、版本管理和数据发布
- `quant-research`：具体策略、专有特征、模型选择、实验与晋升判断
- `quant-intel-platform`：研究报告、看板和结果交付
- `quant-intel-deploy`：研究结果发布与部署

策略研究假设、专有特征和晋升规则由 `quant-research` 等私有研究层维护。

平台通过已发布的数据资产和版本化产物与其他项目协作，不直接接入数据供应商，也不依赖私有策略模块。

## 开发和质量检查

完整测试、覆盖率、类型检查和维护性命令见[测试与质量检查](docs/testing.md)。Ruff 会按仓库配置扫描源码、脚本和测试，`ty` 在 CI 中对配置的源码范围执行严格检查。

修改 `packages/research-contracts/` 后，如果测试仍读取旧构建产物，可重新安装本地包：

```bash
uv sync --locked --all-groups --reinstall-package research-contracts
```

公开发布边界检查应在干净 worktree 中运行，或按[测试说明](docs/testing.md)执行 clean export。不要把本地运行产物作为公开导出内容。

## 许可证

仓库采用 Apache License 2.0，许可范围以 [LICENSE](LICENSE) 为准。第三方依赖、真实数据、凭证和私有策略不属于本仓库许可证的覆盖范围。
