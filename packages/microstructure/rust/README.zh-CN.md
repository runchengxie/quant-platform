# Engine 原生构建入口

[English](README.md)

可选的 `quant-microstructure-core` 发行包及 `_microstructure_rs` 模块仅由 Engine 构建。
使用 [固定提供方版本](https://github.com/runchengxie/quant-backtest-engine/tree/51ab1e8cb2267d938a0681b81f2419d504ed91cc/core-native)，
运行 `maturin build --locked --release -m core-native/Cargo.toml`，将 wheel 安装到 Platform 测试环境，
再运行 `TICKNET_REQUIRE_RUST=1 python -m pytest tests/microstructure tests/test_engine_microstructure_compatibility.py`。
不要在 Platform 构建同名 wheel。原源码、锁文件与许可信息保留在 Git 历史中，哈希见 `docs/migration/engine-provider-b.json`。
Python 仍为默认后端。Rust 必须显式选择，且不提供逐笔成交冲击证据。
