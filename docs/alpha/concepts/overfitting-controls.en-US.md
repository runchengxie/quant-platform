# Overfitting Controls

Language: English · [简体中文](overfitting-controls.md)

> Status: active  
> Owner: quant-market-research  
> Last verified: 2026-10-05  
> Source of truth: yes  
> Superseded by: n/a

This guide explains checks that reduce data leakage, unstable validation, feature-selection bias, and repeated-trial bias. It describes repository mechanisms, not a promise that every check runs in every pipeline. See [research outputs](../reference/research-outputs.en-US.md), [configuration](../../orchestration/reference/configuration.md), and [CLI helpers](../../orchestration/reference/cli-helpers.md) for their respective contracts.

## Main risks and checks

| Risk | Useful checks |
| --- | --- |
| Historical data contains information unavailable at the time | Point-in-time universe and versioned asset checks |
| Label windows overlap across train and test | Time-ordered splits, event-window purging, and CPCV |
| Adjacent observations share market conditions | Walk-forward evaluation and rolling training windows |
| Many trials were run but only the winner was retained | A complete trial registry, DSR, and PBO |
| Results depend on one particular return path | CPCV paths and scenario resampling |
| Correlated features mask each other's contribution | Ablation, permutation importance, SFI, and drop-column analysis |

PIT means using only information available at each historical decision time. CPCV is combinatorial purged cross-validation. DSR adjusts the Sharpe estimate for selection among multiple trials. PBO estimates how often an in-sample winner ranks poorly out of sample; CSCV is a common way to estimate it.

## What the repository provides

| Mechanism | Implementation and limits |
| --- | --- |
| Time split and event-window purge | Alpha research split APIs accept `cv_purge_mode` values `gap` and `event_window`. This is not a separately registered `strategy alpha` CLI command. |
| Walk-forward and final holdout | The pipeline supports `eval.walk_forward` and `eval.final_oos`. Keep the final holdout out of candidate selection. |
| CPCV and PBO | The alpha package contains CPCV and PBO helpers. Their parser helpers are not registered as public `strategy-pipeline` commands. |
| Feature evidence | The alpha package supports ablation, permutation importance, factor IC, SFI, correlation audit, and drop-column modes. Its parser helper is not a public `strategy-pipeline` subcommand. |
| Diagnostics | `overfitting_diagnostics` provides uniqueness, negative-control, scenario-backtest, and candidate-freeze modes through a package parser helper. These do not run automatically in ordinary training. |
| Trial registry | `ExperimentRegistry` is an append-only JSON API for recording comparable trial identities and statuses. It does not discover trials by scanning run directories. |
| Promotion gate | `alpha_research.promotion_gate` evaluates supplied reports and configuration. Check `strategy-pipeline --help` for the current public command surface. |

The public `strategy-pipeline` CLI does not register the historical commands `strategy alpha cpcv`, `strategy alpha pbo`, `strategy alpha feature-evidence`, `strategy trial-registry`, or `strategy promotion-gate`. Use package APIs or an explicitly configured research runner, and verify its invocation in the owning project before running it.

## A practical review sequence

1. Freeze the data assets, point-in-time universe, target, feature set, costs, and portfolio construction used for comparisons.
2. Use chronological validation. Configure `cv_purge_mode: event_window` when label windows can overlap, and verify that the selected runner forwards this setting to the split API.
3. Keep the final out-of-sample interval untouched until the candidate and its rules are fixed.
4. Compare a simple baseline with the candidate. Review feature-family ablations and stability evidence; use correlation and feature-importance diagnostics to understand substitutions.
5. Record failed as well as successful trials. DSR and PBO are informative only when the registry contains a sufficiently complete, comparable trial set.
6. Use CPCV or scenario resampling as targeted stress checks. They complement, but do not replace, forward-time and final-holdout evaluation.
7. Freeze the selected candidate and its evidence before simulated or shadow execution.

## Promotion evidence

The promotion-gate API accepts evidence such as main evaluation, backtest, walk-forward, final OOS, and cost/turnover reports. Optional hard rejections and soft thresholds include minimum CPCV path count and DSR trial count. These configuration-driven checks do not make a candidate reliable when inputs are incomplete or incomparable.

For every result, inspect data and trial coverage along with IC, long-short return, Sharpe, drawdown, turnover, costs, and exposures. A single high Sharpe, feature-importance score, or model run is not sufficient promotion evidence.
