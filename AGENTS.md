# quant-platform 工作规则

这是公开的可复用量化研究平台仓库。保留 `portfolio_backtester` Python 命名空间，直到完成兼容迁移。
这里只放公开机制、合成数据、测试、契约和迁移证据。不要加入数据供应商、凭证、真实数据、
策略参数、私有编排、执行运行时或研究产物。

策略研究假设、专有特征和晋升规则属于私有研究层。本仓库只保留可复用的公开机制。

在仓库根目录运行 `uv sync --locked --all-groups`、`uv run ruff check .` 和 `uv run pytest`。
