# Local staging instructions

This directory is a local-only migration prototype, not a repository and not a published package.
Keep the `portfolio_backtester` Python namespace unchanged. Only public mechanisms, synthetic data,
tests, contracts, and migration evidence belong here. Do not add providers, credentials, real data,
strategy parameters, orchestration, execution runtime, or research artifacts.

`DailyWatch20` 是为现有调用方保留的兼容例外。本仓库不扩展策略研究假设、特征或晋升规则。

Run `uv sync --locked --all-groups`, `uv run ruff check .`, and `uv run pytest` from this directory.
