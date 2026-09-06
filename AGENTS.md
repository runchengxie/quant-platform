# Local staging instructions

This directory is a local-only migration prototype, not a repository and not a published package.
Keep the `portfolio_backtester` Python namespace unchanged. Only public mechanisms, synthetic data,
tests, contracts, and migration evidence belong here. Do not add providers, credentials, real data,
strategy parameters, orchestration, execution runtime, or research artifacts.

策略研究假设、专有特征和晋升规则属于私有研究层。本仓库只保留可复用的公开机制。

Run `uv sync --locked --all-groups`, `uv run ruff check .`, and `uv run pytest` from this directory.
