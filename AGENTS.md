# quant-platform 工作规则

## PR review 豁免

由用户本人提交，或由用户明确委托 agent 完成的 PR，无需单独的人工 review。这是持续有效的授权，不需要逐个 PR 确认，并覆盖本文件中的一般 PR review 要求。必需检查仍须通过，合并冲突必须解决。不得绕过 GitHub 分支保护或 ruleset 强制要求的审批。

这是公开的可复用量化研究平台仓库。保留 `portfolio_backtester` Python 命名空间，直到完成兼容迁移。

公共框架迁移已经完成。现有 Python 通用回测、组合构造、风险、执行模拟和公共契约继续维护在本仓库。独立 Rust 引擎入口、版本化订单意图契约和 NautilusTrader 薄适配维护在 `quant-backtest-engine`。移除旧回测接口前必须完成调用方迁移和语义对照。`quant-market-data-platform` 独立负责数据接入、标准化、质量治理、版本和已发布数据资产，本仓库只消费其发布资产。`research-workspace`、旧 `portfolio-backtester` 和旧 `quant-execution-engine` 仅用于历史复现和兼容核对。

独立引擎的显式客户端位于 `portfolio_backtester.backends.engine_sessions`，只负责内容摘要固定的子进程调用、结果勾稽与规范化，不复制数量规划或撮合，不自动注册，也不代表完整统一执行结果包。

`portfolio_backtester` Python 命名空间暂时保持不变。本仓库只接收公开机制、合成数据、测试、契约和迁移证据，不接收数据供应商、凭证、真实数据、策略参数、任务编排、执行运行时或研究产物。

策略研究假设、专有特征和晋升规则属于私有研究层。本仓库只保留可复用的公开机制。

- 策略假设、现金流 ML、专有特征和模型选择留在 `quant-research`。
- 平台代码必须保持策略无关，不依赖私有策略模块、真实策略数据或凭证。
- 不要为了迁移方便复制策略实现。需要兼容时保留薄 adapter，并记录删除条件。
- 历史边界见 `docs/migration/research-workspace-sunset.md`。

`packages/microstructure/rust/` 是可选的 PyO3 原生扩展，提供订单簿撮合、批量回放和事件排序。Python 实现仍是默认后端和行为参考。Rust wheel 独立构建，不会随根 Python 包自动安装。只有明确选择 `backend="rust"` 时才需要安装它，详细步骤见 `docs/development/microstructure-rust.md`。

## 并行开发流程

多个 agent 同时工作时，每项改动都必须使用独立 worktree 和功能分支。先从工作区明确指定的机器配置或环境变量解析 `CODE_ROOT`。以下 Bash 示例假定已导出该变量，任务目录使用仓库名前缀以避免跨仓重名。推荐流程如下：

```bash
git fetch origin
git worktree add "${CODE_ROOT}/.worktrees/quant-platform-<任务名>" -b feat/<任务名> origin/main
cd "${CODE_ROOT}/.worktrees/quant-platform-<任务名>"
uv run pytest
git push -u origin feat/<任务名>
gh pr create --base main --head feat/<任务名>
```

PR 合并到 `main` 后，删除远端和本地旧分支以及对应 worktree：

```bash
git worktree remove "${CODE_ROOT}/.worktrees/quant-platform-<任务名>"
git branch -d feat/<任务名>
git push origin --delete feat/<任务名>
```

清理前确认 PR 已合并到 `main`，且任务 worktree 没有唯一未保存内容。只清理本任务资源。发现未提交或未合并改动时保留 worktree 和分支并报告。

不要让多个 agent 直接修改同一个工作树，也不要在 `main` 上直接提交。

Run `uv sync --locked --all-groups`, `uv run ruff check .`, and `uv run pytest` from this directory.

平台通用入口使用 `quant_platform.portfolio`、`quant_platform.analytics`、`quant_platform.backtest`。源码位于 `packages/platform/src`。`portfolio_backtester` 仅作兼容别名，生产代码不得新增直接导入。`quant_platform._portfolio` 是暂存的内部实现，不是公开 API。中立契约不得依赖执行模拟器。独立引擎原始字典 SDK 由 engine 仓库维护，平台仅保留标准分析结果转换。
