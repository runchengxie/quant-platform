# 现金流飞书影子发布

`strategy_pipeline.cashflow_publication` 是 `strategy-app` 现金流运行器和飞书投递适配器之间的边界。

只有满足以下条件时，才能接收 `strategy_app.cashflow.selection.v1` 产物：

- 选股结果通过检查，并且属于 `cashflow_quality_top50_v1`。
- readiness 回执中的 `eligible_for_gray_push: true`。
- `production_eligible` 保持为 false，`eligible_for_live` 为 false。
- 目标列表非空。

命令会写入包含 `targets.json` 和 `receipt.json` 的不可变目录
`publications/<signal>_<hash>/`，然后更新安全的 `latest` 符号链接。
回执会固定选股文件和 readiness 文件的 hash。已有发布内容被修改时，命令会拒绝操作。

```bash
strategy-pipeline cashflow-publish-shadow \
  --selection /path/to/selection.json \
  --readiness /path/to/readiness.json \
  --output-root /path/to/cashflow-publications
```

这是影子发布契约，不会授予生产资格，也不会自行发送飞书消息。
