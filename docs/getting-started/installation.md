# Installation and environments

Language: English · [简体中文](installation.zh-CN.md)

`quant-platform` is a Python project. Use `uv` to create the environment, install the locked dependencies, and run project commands.

## Install the development environment

Run this command from the repository root:

```bash
uv sync --locked --all-groups
```

Verify that the public package entry point imports:

```bash
uv run python -c "import portfolio_backtester; print('portfolio_backtester is ready')"
```

## Run checks

```bash
uv run --locked ruff check .
uv run --locked ruff format --check .
uv run --locked ty check --error-on-warning
uv run --locked pytest -q
```

These are the Python source checks. CI also tests lean and ML dependency modes, builds the optional Rust wheel, and audits exported locked dependencies. The Rust tests require the separately installed wheel; a default Python run does not validate that backend. There is no configured root coverage threshold. See `.github/workflows/ci.yml` for the complete CI commands.

The full test suite covers backtesting, portfolio construction, costs, execution simulation, artifact contracts, and migration compatibility. If this is your first time in the repository, start with [your first backtest](first-backtest.md); you do not need to understand the entire suite first.

## Optional dependencies

Some capabilities use optional dependency groups:

| Capability | Installation |
| --- | --- |
| Qlib backend | `uv sync --locked --all-groups --extra qlib` |
| Microstructure models and Python simulator | `uv sync --locked --all-groups --extra microstructure` |
| Rust microstructure backend | Build and install the wheel separately using the [development guide](../development/microstructure-rust.en.md) |
| Documentation site | `uv sync --locked --all-groups` |

The public platform code does not require data-provider credentials or live market data. The introductory tutorials use synthetic data so you can understand the interfaces and outputs first.

## Next step

After installation, continue to [run your first backtest](first-backtest.md).
