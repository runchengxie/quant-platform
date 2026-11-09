# Installation and environments

Language: English · [简体中文](installation.zh-CN.md)

Platform 0.2.0 supports Python 3.12 and 3.13 with Engine Core 0.2.0 and SDK 0.3.0 at merged revision `51ab1e8cb2267d938a0681b81f2419d504ed91cc`. Core and SDK use the same exact VCS pin; no PyPI publication is required. Engine owns minute execution, paper accounts, reservations, execution planning and deterministic matching/replay/impact. Compatibility modules expose the identical Core objects; the pending adapter preserves Platform's full sparse validation and actual optimizer result. OSQP, statistical risk, research calibration, `pool_sleeves`, daily backtests and model training remain Platform responsibilities. Aliases stay for at least two minor-release cycles and until all recorded supported consumers migrate.



`quant-platform` is a Python project. Use `uv` to create the environment, install the locked dependencies, and run project commands.

## Install the development environment

Run this command from the repository root:

```bash
uv sync --locked --all-groups
```

Verify that the public package entry point imports:

```bash
uv run python -c "import quant_platform; print('quant_platform is ready')"
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
