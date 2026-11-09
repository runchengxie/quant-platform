# 安装与环境

语言：简体中文 · [English](installation.md)

Platform 0.1.0 支持 Python 3.12 和 3.13，依赖 Engine core 0.1.0，并显式安装
minute、cost、scenario 扩展及 SDK 0.3.0。两个包都通过固定 Git 子目录依赖解析到
已合并的 Engine 提交 `19a2ae714b567fc1a46cf996fa5a86a90138bc44`，不要求 PyPI 发布。
原有分钟、公司行动、冲击和基础证据接口直接导出同一个 Engine 类和函数。
统计风险、通用 QP 优化、因子流程及尚未迁移的集成仍属于 Platform。
仅使用 SDK 的 Rust 会话适配器仍需显式选择。不支持的 execution-aware 证据仍为 false。


`quant-platform` 是一个 Python 项目。推荐使用 `uv` 创建环境、安装锁定依赖并运行命令。

## 安装开发环境

在仓库根目录执行：

```bash
uv sync --locked --all-groups
```

验证公开入口可以导入：

```bash
uv run python -c "import quant_platform; print('quant_platform is ready')"
```

## 运行检查

```bash
uv run --locked ruff check .
uv run --locked ruff format --check .
uv run --locked ty check --error-on-warning
uv run --locked pytest -q
```

以上是 Python 源码检查。CI 还验证精简依赖与 ML 依赖模式、构建可选 Rust wheel，并审计导出的锁定依赖。Rust 测试需要单独安装 wheel，默认 Python 测试不能证明该后端通过验证。根项目没有配置覆盖率门槛。完整 CI 命令见 `.github/workflows/ci.yml`。

完整测试会覆盖回测、组合构造、成本、执行模拟、产物契约和迁移兼容行为。第一次使用时，可以先阅读[第一个回测](first-backtest.zh-CN.md)，不需要先理解整个测试套件。

## 可选依赖

部分能力通过可选依赖提供：

| 能力 | 安装方式 |
| --- | --- |
| Qlib 后端 | `uv sync --locked --all-groups --extra qlib` |
| 微观结构模型与 Python 模拟器 | `uv sync --locked --all-groups --extra microstructure` |
| Rust 微观结构后端 | 按[开发说明](../development/microstructure-rust.md)单独构建和安装 wheel |
| 文档站 | `uv sync --locked --all-groups` |

仓库的公开平台代码不需要数据供应商凭证，也不要求先接入真实行情数据。新人教程使用合成数据，便于先理解接口和输出。

## 下一步

完成安装后，继续阅读[运行第一个回测](first-backtest.zh-CN.md)。
