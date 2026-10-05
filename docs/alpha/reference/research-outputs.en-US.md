# Alpha Research Outputs

[简体中文](research-outputs.md)

This page documents output artifacts produced by the alpha research modules in this repository. It is an artifact reference, not a promise that every module is exposed as a command-line subcommand. The current public CLI is `strategy-pipeline`; confirm its available commands with `strategy-pipeline --help`. The old `strategy alpha ...` examples are not registered by that CLI.

Run orchestration and the top-level `summary.json` contract are described in [Run summary sections](../../orchestration/output-summary.en.md). Cross-project artifact contracts are in the [Public API reference](../../reference/public-api.md).

## Output root

When a module uses the shared alpha output-path helper and no explicit output path is provided, its output root is resolved in this order:

1. `ALPHA_RESEARCH_OUTPUT_ROOT`
2. `QUANT_PLATFORM_OUTPUT_ROOT`
3. `DATA_PLATFORM_ROOT/quant-platform/research`
4. `$XDG_STATE_HOME/quant-platform/research`, or `~/.local/state/quant-platform/research` when `XDG_STATE_HOME` is unset

An explicit absolute path is used as given. An explicit relative path is resolved against the current working directory. Some tools resolve paths in their configuration file's directory instead; check the module contract before moving outputs.

## CPCV reports

The `alpha_research.cpcv` and `alpha_research.artifact_cpcv` modules can write reports to an output directory. The shared default is `reports/cpcv_<tag>/`; a missing configuration uses the `default` tag. An explicit output directory overrides this location.

The report contains:

- `cpcv_splits.csv`: split definitions, date ranges, purge/embargo information, and status.
- `cpcv_path_returns.csv`: returns by reconstructed path.
- `cpcv_path_metrics.csv`: path-level sample size, Sharpe, return, volatility, drawdown, IC, long-short, turnover, cost drag, and benchmark-relative metrics where available.
- `cpcv_summary.json`: split/path counts, final-OOS handling, purge mode, and aggregate path metrics.

The exact fields depend on whether the run uses pipeline-prepared context or an artifact-backed CPCV configuration. The summary and tests are authoritative for each mode. CPCV output is validation evidence; it does not itself approve a candidate.

## CSCV, PBO, and DSR

The `alpha_research.pbo` module reads a dated return matrix and writes `pbo_splits.csv` and `pbo_summary.json` under `reports/pbo/` by default. An optional `ExperimentRegistry` JSON file contributes the attempted-trial count used by DSR; the registry is not built by scanning run directories.

The summary records group and split counts, candidate and trial counts, PBO, selected out-of-sample Sharpe statistics, the selected full-sample candidate, maximum drawdown, and DSR fields. Candidate columns must represent comparable return series on a shared date index.

## Dynamic signal ensemble

The `alpha_research.dynamic_signal_ensemble` module writes to configured `output_dir` when present; a relative configured path is resolved from the configuration file. Otherwise it uses the shared default `reports/dynamic_signal_ensemble/`. Its files are:

```text
dynamic_scores.parquet
stock_weights.parquet
factor_weights.parquet
factor_monitor.csv
portfolio_monitor.csv
direction_calibration.csv
dynamic_signal_ensemble_summary.json
```

The summary includes `schema_version`, `artifact_type`, `no_level2`, `rolling_metrics_shifted`, date and signal counts, risk-penalty and correlation settings, average active-factor count and turnover metrics, the resolved configuration, and output file paths.

Rolling Rank IC, ICIR, long-short, coverage, and dispersion diagnostics are shifted by one period before use in selection. Direction calibration uses historical Rank IC and inertia; without enough reverse evidence, the previous direction is retained. This module does not read Level2 data, minute bars, or execution `targets.json`.

## Feature evidence

The `alpha_research.feature_evidence` helpers accept these modes: `generate-ablation`, `summarize-ablation`, `permutation-importance`, `factor-ic`, `sfi`, `correlation-audit`, and `drop-column-importance`. They take a YAML configuration and can write CSV and/or JSON results. Output columns vary by mode.

`generate-ablation` creates generated configurations and a `jobs.csv` plan; it does not run the jobs. Other modes summarize completed evidence or calculate their named diagnostic. See the [Feature Research Protocol](../concepts/feature-research-protocol.en-US.md) for the supported research workflow. The current `strategy-pipeline` CLI does not register these helpers as a command.

## Overfitting diagnostics

The `alpha_research.overfitting_diagnostics` module contains diagnostic helpers for event uniqueness, negative controls, scenario backtests, and candidate-freeze manifests. Their outputs are mode-specific:

- Uniqueness: event rows and a summary JSON.
- Negative controls: a CSV report.
- Scenario backtest: `scenario_paths.csv` and `scenario_summary.json`.
- Candidate freeze: a JSON manifest.

These helpers are not exposed as an alpha command group by the current `strategy-pipeline` CLI. Consult the module parser and tests before relying on any historical command example.

## Experiment registry

`alpha_research.experiment_registry.ExperimentRegistry` is an append-only JSON record of trials supplied by the caller. Its document has `schema_version`, `trial_count`, and `trials`; each trial records a candidate, feature set, universe, holding period, parameters, status, and a stable content-derived `trial_id`. PBO can read this file through its optional trial-registry input.

The registry does not recursively scan `summary.json` or `config.used.yml` files and does not automatically recover failed trials. Record the full attempted set at the point where experiments are run.

## Signal artifacts

`signals.parquet` and `signals.meta.json` are the standard alpha-to-backtest signal files. See the [Signal Artifact Contract](signal-artifacts.en-US.md) for fields, validation, and metadata.
