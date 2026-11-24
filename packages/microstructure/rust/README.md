# Engine-owned native build

[简体中文](README.zh-CN.md)

The optional `quant-microstructure-core` distribution and `_microstructure_rs` module
are built only by [the pinned Engine provider](https://github.com/runchengxie/quant-backtest-engine/tree/3e0514ee127fbf00ad4f627d72f91349df4a121f/packages/microstructure-native).

In that checkout, run `maturin build --locked --release -m packages/microstructure-native/Cargo.toml`.
Install its wheel into the Platform test environment and run
`TICKNET_REQUIRE_RUST=1 python -m pytest tests/microstructure tests/test_engine_microstructure_compatibility.py`.
Do not build a second Platform native wheel. Original source, lock and notices
remain in Git history; hashes are recorded in `docs/migration/engine-provider-b.json`.
Python is the default. Rust is explicit. Use the pinned provider's
[native evidence contract](https://github.com/runchengxie/quant-backtest-engine/blob/3e0514ee127fbf00ad4f627d72f91349df4a121f/docs/development/microstructure-rust.md)
for the supported per-fill and impact scope. A wheel from a different historical
provider is not interchangeable with the current Core API.
