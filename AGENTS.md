# quant-platform 工作规则

这是公开的可复用量化研究平台仓库。保留 `portfolio_backtester` Python 命名空间，直到完成兼容迁移。

`research-workspace` 处于 sunset 过渡期。新的通用回测、组合构造、风险、执行模拟和公共契约应优先落在本仓库。`market-data-platform` 保持独立，继续负责数据接入、标准化、质量治理、版本和已发布数据资产。本仓库只消费其发布资产。旧 `portfolio-backtester` 和 `quant-execution-engine` 只用于迁移兼容、历史复现和事实核对。

`portfolio_backtester` Python 命名空间暂时保持不变。本仓库只接收公开机制、合成数据、测试、契约和迁移证据，不接收数据供应商、凭证、真实数据、策略参数、任务编排、执行运行时或研究产物。

策略研究假设、专有特征和晋升规则属于私有研究层。本仓库只保留可复用的公开机制。

- 策略假设、现金流 ML、专有特征和模型选择留在 `quant-research`。
- 平台代码必须保持策略无关，不依赖私有策略模块、真实策略数据或凭证。
- 不要为了迁移方便复制策略实现。需要兼容时保留薄 adapter，并记录删除条件。
- 详细规则见 `docs/migration/research-workspace-sunset.md`。

## 并行开发流程

多个 agent 同时工作时，每项改动都必须使用独立 worktree 和功能分支。推荐流程如下：

```bash
git fetch origin
git worktree add /home/richard/code/.worktrees/<任务名> -b feat/<任务名> origin/main
cd /home/richard/code/.worktrees/<任务名>
uv run pytest
git push -u origin feat/<任务名>
gh pr create --base main --head feat/<任务名>
```

PR 合并到 `main` 后，删除远端和本地旧分支以及对应 worktree：

```bash
git push origin --delete feat/<任务名>
git branch -d feat/<任务名>
git worktree remove /home/richard/code/.worktrees/<任务名>
```

不要让多个 agent 直接修改同一个工作树，也不要在 `main` 上直接提交。

Run `uv sync --locked --all-groups`, `uv run ruff check .`, and `uv run pytest` from this directory.
