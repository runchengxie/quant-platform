# 开发与维护

语言：简体中文 · [English](development-guide.en.md)

本页说明 `packages/microstructure` 当前公开代码的职责和本地检查入口。策略研究、真实行情和生产运行配置不属于这个公开包。

## 代码结构

| 路径 | 职责 |
| --- | --- |
| `packages/microstructure/src/ticknet/eventstream/` | 事件流打包、数据集与窗口、模型、训练和评估 |
| `packages/microstructure/src/ticknet/simulator/` | 合成事件生成、订单簿撮合、回放、排序和影响分析 |
| `packages/microstructure/rust/` | 可选 PyO3 扩展，提供订单簿撮合、批量回放和事件排序 |
| `tests/microstructure/` | 上述公开实现的合成数据和确定性测试 |

Python 是默认实现和行为参考。需要 Rust 后端时，按[可选 Rust 内核说明](../development/microstructure-rust.md)单独构建 wheel 并显式选择后端。

历史 FI-2010 复现代码保留在 `legacy/`，不属于当前默认开发链路。不要从已归档的说明或历史入口推断当前公开 API，先检查 `pyproject.toml`、`packages/microstructure/src/ticknet/` 和相应测试。

## 本地检查

从仓库根目录安装锁定的开发依赖并运行相关测试：

```bash
uv sync --locked --all-groups --extra microstructure
uv run --locked pytest tests/microstructure -q
```

全仓质量检查、严格类型检查和 CI 质量门禁见[开发与测试说明](../testing.md)。Rust parity 测试在普通 Python 环境没有安装扩展时会跳过，强制测试 Rust 后端的构建步骤见 Rust 内核说明。
