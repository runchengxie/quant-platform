# 现金流飞书影子发布

语言：简体中文 · [English](cashflow-publication.en.md)

`strategy_pipeline.cashflow_publication` 是 `strategy-app` 现金流运行器和飞书投递适配器之间的边界。
模块只写入研究用途的影子发布产物，不会发送飞书消息，也不会授予生产资格。

选股产物必须使用 `strategy_app.cashflow.selection.v1` schema，策略为 `cashflow_quality_top50_v1`，
并匹配固定策略口径 `cashflow_quality_top50_v1.quarterly_fcf_cap10.v1`：最多 50 个标的、单只权重上限 10%、
按季度调仓，信号时间为 `source_close_to_next_open`。

选股状态必须为 `passed`，不能标记为可实盘，且 `targets` 列表不能为空。标准模式下，
`cashflow_readiness.v1` 回执必须属于同一策略，`eligible_for_gray_push` 为 `true`，决策为
`candidate_for_gray_push`，没有失败的 gate，并包含已验证的 evidence attestation 和 64 位小写 SHA-256。
`production_eligible` 必须为 `false`。

可选 API 参数 `allow_reconstructed_pit` 对应 CLI 参数 `--allow-reconstructed-pit`，用于启用单独的研究模式。该模式要求选股标记 `pit_quality: reconstructed`，
就绪回执需使用 `continue_shadow` 决策、将 `eligible_for_gray_push` 设为 `false`，并在
`failed_gates` 中包含 `pit`。其余选股限制不变。此模式生成的产物仍仅供研究，且不可用于实盘。

命令由根项目的 `strategy-pipeline` CLI 注册，写入 `publications/<signal_date>_<hash-prefix>/` 不可变目录，
其中包含 `targets.json` 和 `receipt.json`，并更新 `latest` 符号链接。目标文件是选股输入的原样副本。
回执将 `publication_tier` 记为 `feishu_shadow`，以 SHA-256 固定选股和就绪文件，并记录
`research_only: true` 与 `eligible_for_live: false`。
重复执行时，如果已有文件未变，会返回原有产物。不完整或被修改的发布会被拒绝。

可选的来源参数包括 `--producer-repository`、`--producer-commit`、`--platform-repository` 和
`--platform-commit`。提供其中任意一项时，四项都必须提供。重建 PIT 模式需要显式添加
`--allow-reconstructed-pit`。

```bash
strategy-pipeline cashflow-publish-shadow \
  --selection /path/to/selection.json \
  --readiness /path/to/readiness.json \
  --output-root /path/to/cashflow-publications
```

这是影子发布契约，不会授予生产资格，也不会自行发送飞书消息。
