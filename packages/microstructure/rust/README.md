# Engine-owned native build

[简体中文](README.zh-CN.md)

The optional `quant-microstructure-core` distribution and `_microstructure_rs` module
are built only by [Engine at 51ab1e8cb2267d938a0681b81f2419d504ed91cc](https://github.com/runchengxie/quant-backtest-engine/tree/51ab1e8cb2267d938a0681b81f2419d504ed91cc/core-native).

In that checkout, run `maturin build --locked --release -m core-native/Cargo.toml`.
Install its wheel into the Platform test environment and run
`TICKNET_REQUIRE_RUST=1 python -m pytest tests/microstructure tests/test_engine_microstructure_compatibility.py`.
Do not build a second Platform native wheel. Original source, lock and notices
remain in Git history; hashes are recorded in `docs/migration/engine-provider-b.json`.
Python is the default. Rust is explicit and cannot supply per-fill impact evidence.
