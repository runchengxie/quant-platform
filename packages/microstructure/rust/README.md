# Engine-owned native build

[简体中文](README.zh-CN.md)

The optional `quant-microstructure-core` distribution and `_microstructure_rs` module
are built only by [the pinned Engine provider](https://github.com/runchengxie/quant-backtest-engine/tree/d13ffd45158b003fe6c6874da73d3ab6065388f2/packages/microstructure-native).

In that checkout, run `maturin build --locked --release -m packages/microstructure-native/Cargo.toml`.
Install its wheel into the Platform test environment and run
`TICKNET_REQUIRE_RUST=1 python -m pytest tests/microstructure tests/test_engine_microstructure_compatibility.py`.
Do not build a second Platform native wheel. Original source, lock and notices
remain in Git history; hashes are recorded in `docs/migration/engine-provider-b.json`.
Python is the default. Rust is explicit. Use the pinned provider's
[native evidence contract](https://github.com/runchengxie/quant-backtest-engine/blob/d13ffd45158b003fe6c6874da73d3ab6065388f2/docs/development/microstructure-rust.md)
for the supported per-fill and impact scope. A wheel from a different historical
provider is not interchangeable with the current Core API.
