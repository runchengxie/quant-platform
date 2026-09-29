# quant-platform

`quant-platform` is a reusable quantitative research framework for backtesting, portfolio construction, risk analysis, execution simulation, and public research artifact contracts. It is designed for research code and tools. It does not store real strategy data, proprietary features, credentials, or research conclusions.

[中文 README](README.zh-CN.md) · [English language policy](docs/LANGUAGE_POLICY.md) · [中文语言政策](docs/LANGUAGE_POLICY.zh-CN.md)

[Online documentation](https://runchengxie.github.io/quant-platform/)

## Quick start

Requirements: Python 3.12 or newer and `uv`.

```bash
uv sync --locked --all-groups
```

Then run the [first backtest example](docs/getting-started/first-backtest.md). It uses synthetic data and does not require real market data or provider credentials.

## Read next

- [Platform overview](docs/concepts/platform-overview.md)
- [Installation and environments](docs/getting-started/installation.md)
- [First backtest](docs/getting-started/first-backtest.md)
- [Understanding results](docs/getting-started/understanding-results.md)
- [Framework backends](docs/alpha/concepts/framework-backends.md)
- [Execution simulation](docs/guides/execution-simulation.md)
- [Documentation index](docs/README.md)

## Project boundary

This repository maintains strategy-agnostic quantitative mechanisms. Strategy assumptions, proprietary features, and promotion rules belong to the private research layer. Market data production belongs to [quant-market-data-platform](https://github.com/runchengxie/quant-market-data-platform), strategy-specific research belongs to private `quant-research`, and persistent execution of submitted jobs belongs to [quant-backtest-runtime](https://github.com/runchengxie/quant-backtest-runtime).

The Alpha module boundary is documented in [framework backends](docs/alpha/concepts/framework-backends.md).

The existing `portfolio_backtester` Python import namespace remains for compatibility.
