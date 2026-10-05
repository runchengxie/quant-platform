# Feature research protocol

Language: English · [简体中文](feature-research-protocol.md)

Use this protocol when the universe, labels, evaluation design, backtest rules, and market data are fixed, and the remaining question is which feature groups add useful evidence. Change one feature decision at a time so results remain interpretable.

This page describes a reusable workflow. Strategy hypotheses, proprietary feature sets, and promotion decisions belong in the owning research project, not in this public platform guide.

## Compare feature groups

Group candidate features by their intended role, such as momentum, liquidity, valuation, profitability, or data freshness. These are examples, not a required taxonomy. Record the exact feature names and rationale in the experiment configuration.

Start with a baseline, then remove one group at a time while keeping the universe, labels, evaluation windows, costs, and backtest settings unchanged. Compare each variant with the baseline. Do not infer independent value from a single feature-importance ranking alone.

The `alpha_research.feature_evidence.generate_ablation_jobs` helper creates a baseline configuration, one configuration per configured feature family, and a `jobs.csv` plan. It does not execute the generated jobs. The summarizer compares completed runs and reports metric deltas against the baseline. The helper accepts a `feature_evidence` configuration; ablation generation requires a `base_config` whose `features.list` is populated.

These helpers are not registered as a `strategy-pipeline` command. The repository's current CLI help lists `afml-evidence` and `research-protocol`, but no feature-evidence command. Do not use old `strategy alpha feature-evidence` examples.

## Check coverage before adding sparse inputs

For a feature that is available only for part of the history, inspect coverage before interpreting model results. The dataset builder can log `Feature availability collapse before complete-case filter` when availability drops materially. Also compare retained dates and sample counts across otherwise identical variants.

Treat zero feature importance and constant predictions as diagnostics to investigate, not as automatic promotion or rejection rules. Review them alongside out-of-sample metrics, turnover, costs, and feature stability where those outputs are available.

## Keep the comparison controlled

- Change only the feature list or family under test.
- Keep the baseline and every ablation on the same data and evaluation contract.
- Record generated configurations and completed run locations.
- Check coverage, out-of-sample results, turnover, and costs before drawing a conclusion.
- Label probes and diagnostic runs clearly; do not present them as production recommendations.

## Related pages

- [Research outputs](../reference/research-outputs.en-US.md) describes the evidence helpers and their output boundaries.
- [Research protocols](research-protocols.en-US.md) describes the separate exploratory, candidate, and release gates.
