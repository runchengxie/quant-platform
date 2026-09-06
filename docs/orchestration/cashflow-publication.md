# Cashflow Feishu shadow publication

`strategy_pipeline.cashflow_publication` is the boundary between the
`strategy-app` cashflow runner and the Feishu delivery adapter.

It accepts a `strategy_app.cashflow.selection.v1` artifact only when:

- the selection is passed and belongs to `cashflow_quality_top50_v1`;
- the readiness receipt says `eligible_for_gray_push: true`;
- `production_eligible` remains false and `eligible_for_live` is false;
- the target list is non-empty.

The command writes an immutable `publications/<signal>_<hash>/` directory with
`targets.json` and `receipt.json`, then updates the safe `latest` symlink. The
receipt pins both the selection and readiness file hashes. A modified existing
publication is rejected.

```bash
strategy-pipeline cashflow-publish-shadow \
  --selection /path/to/selection.json \
  --readiness /path/to/readiness.json \
  --output-root /path/to/cashflow-publications
```

This is a shadow publication contract; it does not grant production eligibility
and does not send a Feishu message by itself.
