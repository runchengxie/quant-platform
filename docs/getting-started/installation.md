# 安装与环境

`quant-platform` 是一个 Python 项目。推荐使用 `uv` 创建环境、安装锁定依赖并运行命令。

## 安装开发环境

在仓库根目录执行：

```bash
uv sync --locked --all-groups
```

验证公开入口可以导入：

```bash
uv run python -c "import portfolio_backtester; print('portfolio_backtester is ready')"
```

## 运行检查

```bash
uv run ruff check .
uv run pytest -q
```

完整测试会覆盖回测、组合构造、成本、执行模拟、产物契约和迁移兼容行为。第一次使用时，可以先阅读[第一个回测](first-backtest.md)，不需要先理解整个测试套件。

## 可选依赖

部分能力通过可选依赖提供：

| 能力 | 安装方式 |
| --- | --- |
| Qlib 后端 | `uv sync --locked --all-groups --extra qlib` |
| 微观结构模块 | `uv sync --locked --all-groups --extra microstructure` |
| 文档站 | `uv sync --locked --all-groups` |

仓库的公开平台代码不需要数据供应商凭证，也不要求先接入真实行情数据。新人教程使用合成数据，便于先理解接口和输出。

## 下一步

完成安装后，继续阅读[运行第一个回测](first-backtest.md)。
