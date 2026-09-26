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

生产环境可以按用途安装：

```bash
# 只安装回测、组合和公共契约所需依赖
uv sync --locked --no-default-groups

# 需要模型训练、交叉验证或技术指标特征时
uv sync --locked --no-default-groups --extra ml
```

`ml` 包含 XGBoost、scikit-learn 和 pandas-ta。基础安装保留回测使用的 NumPy、pandas、SciPy、Arrow 等依赖。开发依赖仍包含完整机器学习环境，因此原有开发和测试命令保持可用。使用 Qlib 研究流程时同时启用 `--extra ml --extra qlib`。

其他仓库通过依赖声明 `quant-platform[ml]` 启用机器学习功能，并固定平台提交。只使用回测的运行时声明 `quant-platform` 即可。升级到这一安装方式时，使用 `alpha_research.modeling`、特征计算或训练流程的调用方需要显式启用 `ml`。

项目保留 `portfolio_backtester` Python 命名空间，供现有研究代码兼容使用。常用入口和示例见[文档总览](docs/README.md)，Alpha 模块边界见[后端说明](docs/alpha/concepts/framework-backends.md)。

微观结构模型和模拟器位于 `packages/microstructure/`。Python 实现是默认后端。需要 Rust 撮合与批量回放时，可按[微观结构开发说明](docs/development/microstructure-rust.md)单独构建并安装原生扩展。

## 项目边界

- `quant-platform`：通用回测、组合、风险、执行模拟、微观结构机制和公开研究产物接口
- `quant-backtest-runtime`：回测任务协议、SQLite 状态、worker、资源控制、CLI 和独立发布
- `quant-market-data-platform`：数据接入、标准化、质量治理、版本管理和数据发布
- `quant-research`：具体策略、专有特征、模型选择、实验与晋升判断
- `quant-intel-platform`：研究报告、看板和结果交付
- `quant-intel-deploy`：研究结果发布与部署

回测任务的通用脚本、合成数据示例和运维说明统一在[运行时仓库](https://github.com/runchengxie/quant-backtest-runtime)维护，具体步骤见[任务协议](https://github.com/runchengxie/quant-backtest-runtime/blob/main/docs/jobs.md)和[发布与恢复](https://github.com/runchengxie/quant-backtest-runtime/blob/main/docs/operations.md)。

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
