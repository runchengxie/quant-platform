# Rust 微观结构内核

语言：简体中文 · [English](microstructure-rust.en.md)

`packages/microstructure/rust` 是 `ticknet.simulator` 的可选 PyO3 wheel。Python 仍是参考实现和默认后端。wheel 提供价格优先、时间优先的订单簿，支持对生成的背景单和干预单做批量回放，也支持事件索引排序。研究编排、模型生成、冲击分析和执行引擎仍由 Python 负责。

## 构建与使用

先安装项目依赖，再在同一环境中构建并安装 wheel。`rust-toolchain.toml` 指定 Rust 1.98.1，根目录开发依赖组提供由 `uv.lock` 锁定版本的 Maturin：

```bash
uv sync --locked --all-groups --extra microstructure
uv run --locked maturin build --locked --release \
  -m packages/microstructure/rust/Cargo.toml --out /tmp/microstructure-wheels
uv pip install --python .venv/bin/python /tmp/microstructure-wheels/*.whl
TICKNET_REQUIRE_RUST=1 .venv/bin/pytest tests/microstructure -q
```

使用 `MatchingEngine(backend="rust")` 选择原生订单簿。`ReplaySession` 会通过一次原生调用发送所有待处理订单，并在时间戳相同时保留干预单优先级及公开的 `Tick` 输出类型。使用 `sort_simulator_events(events, backend="rust")` 选择原生排序。普通源码安装不会自动要求 Rust 编译器，也不会静默切换后端。若请求 Rust 后端但未安装 wheel，Python 会抛出 `ModuleNotFoundError`。

原生 wheel 通过 `abi3` 支持 Python 3.12 及以上版本。它独立于根 setuptools 包构建，部署时必须同时安装根包和该 wheel。订单 ID 在活动订单簿中必须唯一，这与模拟器事件契约一致。Rust 边界使用有符号 64 位整数表示价格和数量。本仓库不提交真实行情、凭证或基准输出。

## 正确性与性能测量

`tests/microstructure/test_rust_parity.py` 使用带固定种子的随机订单流、撤单、初始盘口、匿名档位缩量、事件排序和批量回放对比两个后端。CI Rust job 会构建 wheel，并设置 `TICKNET_REQUIRE_RUST=1` 运行这些测试。普通 Python job 在没有可选 wheel 时会跳过它们。

基准脚本为两个后端生成相同的合成事件，检查所有 tick 和最终最优价格一致，并报告中位耗时：

```bash
.venv/bin/python scripts/benchmarks/microstructure_replay.py \
  --events 100000 --seed 42 --repeats 5
```

2026-09-24 的开发工作树测量使用 CPython 3.13.14 和 Rust 1.98.1，处理 100,000 个背景单和 1,000 个干预单时，Python 用时 1.137 秒，Rust 用时 0.250 秒，中位速度为 4.54 倍，且输出一致。这是单进程合成回放结果，不代表交易所延迟、实盘表现或任意行情数据上的速度。
