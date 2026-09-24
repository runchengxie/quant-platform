# 测试和质量检查

本页说明 `quant-platform` 的本地测试入口、公开 CI 和实际检查范围。

## 安装开发依赖

```bash
uv sync --locked --all-groups
```

项目使用 Python 3.12，依赖版本由 `uv.lock` 固定。

仓库中的 `research-contracts` 是本地路径依赖。修改这个包后，如果测试仍然读取旧版本，
重新安装该包：

```bash
uv sync --locked --all-groups --reinstall-package research-contracts
```

完整测试和公共发布检查应在干净的任务 worktree 中运行。主检出中的 `.env.local`、`out/`、
`state/` 和其他 worktree 属于本机环境，可能干扰发布边界检查。

## 统一入口

```bash
scripts/dev/run_tests.sh <mode> [args...]
```

| 模式 | 实际范围 |
| --- | --- |
| `all` | 完整 `pytest` 测试集 |
| `fast` | `all` 的兼容别名 |
| `unit` | `all` 的兼容别名 |
| `coverage` | 完整测试集，并统计 `packages/` 与 `scripts/` 下 Python 源码覆盖率 |
| `lint` | Ruff 代码检查 |
| `format` | Ruff 格式检查 |
| `format-all` | `format` 的兼容别名 |
| `typecheck` | `ty` 配置范围 |
| `typecheck-release` | `typecheck` 的兼容别名 |
| `maintainability` | 维护性指标和当前预算 |

`fast` 和 `unit` 没有缩小测试范围。

## 常用命令

```bash
scripts/dev/run_tests.sh all
scripts/dev/run_tests.sh coverage
scripts/dev/run_tests.sh all tests/test_execution_contracts.py
scripts/dev/run_tests.sh all tests/test_backtest_backends.py
scripts/dev/run_tests.sh all -k position_backtest
scripts/dev/run_tests.sh lint
scripts/dev/run_tests.sh format
scripts/dev/run_tests.sh typecheck
scripts/dev/run_tests.sh typecheck-release
scripts/dev/run_tests.sh maintainability
```

覆盖率依赖 `pytest-cov`。目前只生成报告，不设置最低覆盖率门槛。Python 覆盖率报告不包括 Rust 扩展。

## 依赖安全检查

公开 CI 使用 `pip-audit` 检查锁定依赖中的已知漏洞。本地可运行同一命令：

```bash
uvx --from pip-audit pip-audit --strict -r <(uv export --locked --all-groups --extra dev --extra microstructure --format requirements-txt --no-hashes --no-emit-project --no-emit-local --no-emit-package quant-platform --no-emit-package research-contracts --no-emit-package research-code-quality)
```

当前 CI 不运行 Bandit 或未使用依赖扫描。新增此类门禁前，应先定义实际扫描的源码和依赖范围。

## 推送前检查

在包含工作区治理的检出中，顶层共享 `pre-push` 会按照工作区清单运行本仓库的导入检查、Ruff、格式检查、`ty` 和完整测试集。

单独克隆本仓库时不会继承共享钩子。推送前应手动运行上方列出的 `lint`、`format`、`typecheck`、`all` 和 `maintainability`。

公共发布边界检查使用干净导出目录：

```bash
bash scripts/public_release/build_clean_export.sh \
  --revision HEAD \
  --destination /tmp/quant-platform-public-export
```

不要把主检出目录中的本地运行产物直接当作公开导出结果。

## GitHub Actions 状态

`.github/workflows/ci.yml` 在 PR 和主分支推送时运行公开质量门禁。`.github/workflows/docs.yml` 独立构建 MkDocs 并发布在线文档。本地命令和工作区共享 `pre-push` 提交前提供反馈。

PR workflow 覆盖：

- Ruff 代码和格式检查。
- 公开源代码和测试范围的 Ruff 检查。
- 框架中立的执行契约。
- 后端协议、规范化结果和 `native` 固定对照样例。
- 框架状态账本。
- 持仓回放回归。
- 包导入检查。

Rust 微观结构检查和 Python 主检查分别运行。在线文档 workflow 使用 strict 模式检查导航页面中的相对链接。`ty` 警告和维护性预算由本地门禁检查。

## 类型检查范围

本地 `scripts/dev/run_tests.sh typecheck` 按 `pyproject.toml` 的 `[tool.ty.src]` 配置检查源码和脚本，并显式加入五个源码根目录解析内部导入。该命令启用 `--error-on-warning`，目前仍有历史诊断，因此尚不能视为全仓类型检查通过。

公开 CI 只检查下面三个迁移包。警告保留为提示，错误仍会使任务失败。最近一次检查在这三个包中报告 306 条诊断，主要是 Pandas 类型信息不足引起的 `Unknown` 推断。CI 会放行这些警告，因此不能把这项结果当成无警告的类型检查：

```bash
uv run --locked --extra dev ty check --exit-zero-on-warning \
  packages/alpha/src packages/orchestration/src packages/execution/src
```

`packages/portfolio-backtester`、`packages/microstructure` 和测试目录中的类型问题目前属于分层治理范围。加入源码根目录后，原先由路径配置造成的 unresolved-import 错误已消除，剩余 warning 仍需按模块分层治理。扩大阻断范围前，应先修复目标模块的类型问题，并同步更新 CI、脚本和本页说明。

扩大类型覆盖时，应先修复目标模块，再更新配置和测试说明。新后端边界先由运行时契约测试保护，后续在共享账本迁移时纳入完整静态检查。

## 测试重点

当前测试集主要覆盖：

- Top-K 组合构造和收益计算
- `BacktestSpec` 序列化和历史入口一致性
- 持仓回放和退出规则
- 成本、滑点和交易约束
- 执行容量模拟
- 持仓契约和策略配置
- A 股整手约束
- benchmark、容量、暴露和报告
- 流动性代理、缓冲区和换手限制
- 框架中立的订单状态、重复事件和乱序事件归约
- 规范化后端结果与固定对照场景
- 包导入和跨仓库依赖隔离
- 维护性指标脚本

新增公开入口或修改输出契约时，应增加行为测试、固定对照样例和导入测试。
