# Model Landscape and Extension Criteria

Language: English · [简体中文](model-landscape.md)

> Status: reference  
> Owner: quant-market-research  
> Last verified: 2026-10-03  
> Source of truth: yes  
> Superseded by: n/a

This page describes the registered model types, remaining diagnostic gaps, and requirements for adding a model. See [Model Selection](model-selection.en-US.md) for usage guidance and [Benchmark Ladder](../../concepts/benchmark-ladder.md) for the comparison protocol.

`quant-market-research` owns model families and research criteria. `strategy_pipeline` owns configuration, commands, and experiment orchestration in this repository.

## Registered model types

The current A-share example uses `xgb_regressor`. The registry contains six trainable models and one frozen-score replay adapter:

| Model type | Role | Main use |
| --- | --- | --- |
| `xgb_regressor` | Default nonlinear model | Predict continuous returns and capture nonlinear effects and feature interactions |
| `xgb_ranker` | Ranking model | Learn same-day cross-sectional ordering grouped by `trade_date` |
| `ridge` | Linear baseline | Check for a stable linear relationship between features and target |
| `ridge_scaled` | Scaled linear baseline | Standardize features within each training fold before fitting Ridge |
| `random_forest_regressor` | Non-boosted tree baseline | Compare tree-based nonlinear effects with linear and boosted-tree models |
| `elasticnet` | Sparse linear comparator | Test whether regularization and feature sparsity add value |
| `fixed_score_artifact` | Frozen-score adapter | Read external scores for deterministic replay and cross-system handoff |

The first six entries train a model. `fixed_score_artifact` replays existing scores and is not a trained-model comparator. These entries and their defaults are registered in `packages/alpha/src/alpha_research/modeling.py`.

## Remaining diagnostic gaps

### Survival targets

`alpha_research.event_labeling` can record Triple Barrier labels, barrier types, and event times. The model registry and training, splitting, and evaluation workflows do not currently provide a survival model.

Before adding one, validate event-table coverage, censoring patterns, and stability over time, then define a reproducible training and evaluation contract.

## Possible future extensions

| Candidate | Evidence it could add | Conditions before adoption |
| --- | --- | --- |
| LightGBM or CatBoost | Whether findings depend on the XGBoost implementation | Keep the current protocol stable and justify dependency and maintenance costs |
| Quantile regression or NGBoost | Return-distribution and tail-risk evidence | Define evaluation metrics and show how distributional information changes a portfolio decision |
| Survival model | Barrier-event probability and timing | Stabilize Triple Barrier event data and complete the training/evaluation contract |
| Model ensemble | Combine independent, stable signals | Establish independent out-of-sample evidence for each base model and freeze the ensemble rule in advance |
| Clustering, dimensionality reduction, or deep representations | State identification or feature compression | Show that simpler models cannot answer the question and define a testable incremental benefit |

Classification models are appropriate only for formally defined classification labels and decision thresholds. Continuous-return targets should generally use regression or ranking models.

## Minimum requirements for a new model

Before adding a model:

1. State the distinct diagnostic question it addresses.
2. Register its canonical name, aliases, default parameters, fit method, and feature-importance source.
3. Add parameter validation, behavior tests, and checks for degenerate output.
4. Compare it with existing models using identical data, targets, time splits, costs, and portfolio construction.
5. Record training time, dependency footprint, and maintenance cost.
6. Require stable incremental results in walk-forward or a frozen out-of-sample period before adding it to common presets.

The current priority is stronger interpretable diagnostics and stricter target, time-split, and out-of-sample evidence. The number of registered models is not a progress metric.
