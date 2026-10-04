# Microstructure development guide

Language: English · [简体中文](development-guide.md)

This page describes the current public code under `packages/microstructure` and its local test entry point. Strategy research, real market data, and production runtime configuration are outside this public package.

## Code layout

| Path | Responsibility |
| --- | --- |
| `packages/microstructure/src/ticknet/eventstream/` | Event-stream packing, datasets and windows, models, training, and evaluation |
| `packages/microstructure/src/ticknet/simulator/` | Synthetic event generation, order-book matching, replay, ordering, and impact analysis |
| `packages/microstructure/rust/` | Optional PyO3 extension for order-book matching, batch replay, and event ordering |
| `tests/microstructure/` | Deterministic and synthetic-data tests for these public components |

Python is the default implementation and behavioral reference. To use the Rust backend, build its wheel separately and select the backend explicitly. See the [optional Rust kernel guide](../development/microstructure-rust.en.md).

Historical FI-2010 reproduction code remains under `legacy/` and is not part of the default development path. Do not infer the current public API from archived guides or old entry points. Check `pyproject.toml`, `packages/microstructure/src/ticknet/`, and the relevant tests.

## Local checks

From the repository root, install the locked development dependencies and run the focused tests:

```bash
uv sync --locked --all-groups --extra microstructure
uv run --locked pytest tests/microstructure -q
```

See the [development and testing guide](../testing.md) for repository-wide quality checks, strict type checking, and CI gates. Rust parity tests are skipped in a regular Python environment when the extension is not installed. The Rust guide documents how to build the extension and require those tests.
