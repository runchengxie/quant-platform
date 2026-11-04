# Canonical 回测证据 bundle

语言：简体中文 · [English](canonical-backtest-bundle.en.md)

`portfolio_backtester.backtest_result.v1` 把一次组合回测的统一账本保存成不可覆盖、可哈希、可重载的目录。
它服务于研究证据和跨仓交接，沿用现有 `CanonicalBacktestResult` 返回对象及订单、成交和现金模型。

## 证据等级

`BacktestEvidenceTier` 第一版提供以下两级。

- `diagnostic` 允许理想化成交、目标权重收益或缺少完整订单/现金证据的兼容研究。它可以写 bundle。
  下游晋级门禁不得把它当成可执行净值证据。
- `execution_aware` 要求 backend capability 明确支持 `order_lifecycle` 和 `daily_ledger`，要求完整
  `research.clock.v1` 执行窗口，并要求统一账本账户对账通过。

没有交易的合法区间也可以生成 `execution_aware` 证据，订单和成交表允许为空。后端须真实支持
订单、成交和每日账本，文件内容须与能力声明一致。

## 目录

写入器固定保存以下文件。

```text
backtest_result/
  manifest.json
  targets.parquet
  orders.parquet
  fills.parquet
  daily_positions.parquet
  daily_cash.parquet
  daily_nav.parquet
  cost_breakdown.parquet
  turnover_breakdown.parquet
  diagnostics.json
```

`manifest.json` 保存以下信息。

- schema、run id 和 evidence tier。
- `research.artifact-envelope.v2`。
- `research.clock.v1` mapping。
- backend 身份和 capability。
- 上游 artifact 引用。
- 每个文件的 SHA-256、required 状态和行数。
- reconciliation 结果。
- 可选的 `tca_calibration` 是由真实成交 TCA 生成的版本化成本校准回执，包含模型、来源版本、样本量和建议成本。
  它只作为审计和回测输入证据保存，bundle writer 不会自动应用建议，也不会因此改变 evidence tier 或晋升状态。

Artifact Envelope 的 `content_sha256` 对 canonical inventory 做哈希。manifest 本身不进入 inventory，
避免自引用哈希。

## 账户对账

当前统一账本提供以下日度聚合值。

```text
daily_positions.positions_value
daily_cash.cash
daily_nav.nav
```

`reconcile_unified_ledger` 按 `trade_date` 一对一对齐，并检查以下等式。

```text
nav = cash + positions_value
```

允许相对于账户规模的浮点容差。日期覆盖不一致、重复日期、非数值会计列或超过容差都会直接失败。

## 写入与读取

`write_backtest_bundle` 先在最终目录同级创建临时目录，写完 Parquet/JSON、计算 inventory 哈希并构造
Artifact Envelope，最后通过原子目录替换发布。目标目录已存在时直接拒绝覆盖。任何中间失败都会清理临时目录。

`read_backtest_bundle` 默认执行以下验证。

- manifest schema。
- evidence-tier completeness。
- Artifact Envelope。
- inventory content hash。
- inventory 中每个文件的内容 SHA-256。

读取器使用已有组合、订单、成交和 PnL 结果，不重新计算。

已有 `CanonicalBacktestResult` 的调用方可以使用 `portfolio_backtester.backends.write_execution_aware_result_bundle`。它要求结果携带完整 `unified_ledger`，检查结果视图与完整账本一致，并调用上述 writer。`NativePositionReplayBackend` 在 `ledger=True` 且有非空每日账本时提供该账本。零成交区间可以保留空订单或成交表及其 ID 列。调用方必须传入完整、时序合法的执行时钟、producer、配置哈希与至少一个输入来源。缺失或对账失败时不会发布有效目录。bundle 的 `daily_nav.parquet` 是执行感知净值来源，结果对象的 `performance` 是历史周期回放收益视图。

## ResearchClock 边界

`execution_aware` writer 会先检查 `research.clock.v1` 必需字段，再调用
`research_contracts.validate_research_clock(..., require_execution=True)` 校验完整执行时钟。
`write_execution_aware_result_bundle` 只接受一次决策对应的时钟。当结果元数据中的
`decision_count` 大于 1 时会拒绝写入。多次决策需要逐次时钟，不能把一个时钟当作整个序列的证明。
