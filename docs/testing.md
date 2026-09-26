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

## 验证安装边界

在独立 worktree 中验证基础环境，防止开发依赖掩盖缺失的运行依赖：

```bash
uv sync --locked --no-default-groups
.venv/bin/python scripts/check_minimal_install.py
uv run --locked --no-default-groups --with pytest pytest -q tests/test_backtest_backends.py tests/test_backtest_bundle.py tests/test_optimizer_backends.py tests/test_execution_sim.py
uv sync --locked --no-default-groups --extra ml
uv run --locked --no-default-groups --extra ml --with pytest pytest -q tests/alpha/test_modeling.py tests/alpha/test_feature_engineering_short_series.py
```

CI 在 Python 3.12 和 3.13 上运行这两种安装模式。基础环境会检查 XGBoost、scikit-learn、pandas-ta 及其专用的 Numba、llvmlite、NCCL 依赖均未安装，再验证实际回测和结果包。机器学习环境验证模型拟合与特征计算。微观结构 CI 还会独立安装 `microstructure` 并运行训练指标计算，验证其 scikit-learn 依赖。完整开发环境继续运行全部测试。

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
| `contracts-coverage` | 运行 `tests/contracts`，并要求已安装 `research-contracts` 的覆盖率至少达到 80% |
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

`coverage` 模式依赖 `pytest-cov`，只生成报告，不设置全仓最低覆盖率门槛。`contracts-coverage` 单独对已安装的 `research-contracts` 设置 80% 门槛。Python 覆盖率报告不包括 Rust 扩展。

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

PR 与 `main` 推送会运行全仓 Ruff 代码和格式检查、严格类型检查、完整 pytest 测试集及 `pip-audit`。Rust job 会单独构建可选 wheel，并在 `TICKNET_REQUIRE_RUST=1` 下运行 microstructure 测试。在线文档 workflow 使用 strict 模式构建 MkDocs 并检查链接。维护性预算由本地 `maintainability` 模式检查。

## 类型检查范围

`scripts/dev/run_tests.sh typecheck` 和 `typecheck-release` 会按 `pyproject.toml` 的 `[tool.ty.src]` 检查配置范围，并启用 `--error-on-warning`。当前范围包括 `portfolio-backtester`、orchestration、execution、alpha、microstructure 和 `scripts/`。CI 运行相同的严格检查，不传入缩小后的路径列表。

只有两个可选依赖保留逐文件导入例外：Qlib 后端需要 `qlib` extra，Rich 渲染器在没有 Rich 时使用纯文本输出。其他已配置源码的类型诊断都会阻断检查。

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
