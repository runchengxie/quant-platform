# Cashflow shadow publication

Language: English · [简体中文](cashflow-publication.md)

`strategy_pipeline.cashflow_publication` is the boundary between the `strategy-app` cashflow runner and its Feishu delivery adapter. It writes a research-only shadow publication. It does not send a Feishu message or grant production eligibility.

## Accepted selection and readiness

The selection must use schema `strategy_app.cashflow.selection.v1`, identify strategy `cashflow_quality_top50_v1`, and match policy `cashflow_quality_top50_v1.quarterly_fcf_cap10.v1`. The policy is fixed at 50 targets, a 10% maximum weight, quarterly rebalancing, and `source_close_to_next_open` signal timing. The selection status must be `passed`, it must not be marked live-eligible, and its `targets` list must be non-empty.

In the standard mode, the `cashflow_readiness.v1` receipt must identify the same strategy, set `eligible_for_gray_push` to `true`, use decision `candidate_for_gray_push`, have no failed gates, and include a verified evidence attestation with a 64-character lowercase SHA-256. `production_eligible` must be `false`.

The optional `--allow-reconstructed-pit` mode is a separate research-only path. It requires `pit_quality: reconstructed` in the selection and accepts a readiness receipt with decision `continue_shadow`, `eligible_for_gray_push: false`, and `pit` in `failed_gates`. All other selection constraints still apply. The resulting publication remains research-only and not live-eligible.

## CLI and output

The root project registers `cashflow-publish-shadow` on the `strategy-pipeline` CLI:

```bash
strategy-pipeline cashflow-publish-shadow \
  --selection /path/to/selection.json \
  --readiness /path/to/readiness.json \
  --output-root /path/to/cashflow-publications
```

The optional provenance arguments are `--producer-repository`, `--producer-commit`, `--platform-repository`, and `--platform-commit`. If any is supplied, all four are required. The API option `allow_reconstructed_pit` maps to the explicit CLI flag `--allow-reconstructed-pit`.

Each publication is written beneath `publications/<signal_date>_<hash-prefix>/` with `targets.json` and `receipt.json`. The targets file is an exact copy of the selection input. The receipt uses `publication_tier: feishu_shadow`, pins the selection and readiness files by SHA-256, and records `research_only: true` and `eligible_for_live: false`. A `latest` symlink points to the current publication.

Publication directories are immutable. Repeating the same publication returns the existing files if they still match; an incomplete or modified publication is rejected. These files support the shadow-delivery boundary only; the command does not upload data or send messages.
