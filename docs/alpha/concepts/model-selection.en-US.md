# Model Selection Guide

Language: English · [简体中文](model-selection.md)

> Status: active  
> Owner: quant-market-research  
> Last verified: 2026-07-16  
> Source of truth: yes  
> Superseded by: n/a

Use this guide to choose a starting point among the trainable models. The registered model set and extension criteria are documented in [Model Landscape](model-landscape.md). Parameter and command details are in [orchestration configuration](../../orchestration/reference/configuration.md) and [CLI helpers](../../orchestration/reference/cli-helpers.md).

The registry also includes `fixed_score_artifact`. It replays frozen external scores without training a prediction model, so it belongs to the artifact-replay workflow.

## Quick choices

| Research goal | Starting model |
| --- | --- |
| Establish a nonlinear baseline | `xgb_regressor` |
| Test whether a same-day ranking objective adds value | `xgb_ranker` |
| Check a linear signal with mixed-scale features | `ridge_scaled` |
| Use a compatibility baseline for already aligned features | `ridge` |
| Test sparse linear constraints | `elasticnet` |
| Replay frozen external scores | `fixed_score_artifact` |

## Model roles

| Model | Training approach | Strength | Limitation |
| --- | --- | --- | --- |
| `xgb_regressor` | Fits a continuous target | Models nonlinear relationships and feature interactions | Requires stable time splits and checks for degenerate predictions |
| `xgb_ranker` | Learns rankings grouped by `trade_date` | Its objective matches cross-sectional ranking | Requires valid within-date groups and costs more to train and tune |
| `ridge` | Linear regression with L2 regularization | Fast, interpretable coefficients, and relatively stable under collinearity | Cannot represent complex nonlinear relationships |
| `ridge_scaled` | Fits scaling within each training fold, then applies Ridge | Handles financial features with mixed units without letting scale dominate regularization | Still linear; scaling must never be fit on test folds or future dates |
| `random_forest_regressor` | Random-forest regression | Provides a nonlinear tree-averaging baseline | Still needs time splits and mature labels; out-of-bag scores do not replace out-of-time validation |
| `elasticnet` | Linear regression with L1 and L2 regularization | Shrinks coefficients and can remove features | Requires choosing both `alpha` and `l1_ratio`; all-zero predictions are more likely |

The A-share preset currently uses `xgb_regressor`. For financial research, start with `ridge_scaled` as the linear comparator and use `ridge` as a compatibility check. Neither replaces strict time-based validation.

## Minimal configurations

### Ridge

```yaml
model:
  type: ridge
  params:
    alpha: 1.0
  sample_weight_mode: date_equal
```

Use `ridge` to check whether features have a stable linear relationship with a continuous target. If the linear result is weak, first review the data, target, and feature evidence before adding model complexity.

### Scaled Ridge

```yaml
model:
  type: ridge_scaled
  params:
    alpha: 1.0
```

`ridge_scaled` fits `StandardScaler` on each training fold before fitting Ridge. This is useful when financial features mix percentages, amounts, and ratios. Never fit the scaler on a test fold or future dates.

### XGBoost ranker

```yaml
model:
  type: xgb_ranker
  params:
    objective: rank:pairwise
```

`xgb_ranker` groups training rows by `trade_date`. After establishing a reproducible regression baseline, use it to test whether directly optimizing ranking improves cross-sectional results.

### ElasticNet

```yaml
model:
  type: elasticnet
  params:
    alpha: 1.0
    l1_ratio: 0.5
  sample_weight_mode: date_equal
```

Use `elasticnet` as a focused sparse-linear comparison. After a run, inspect `flag_constant_prediction` and `flag_zero_feature_importance` in `summary.json`.

### Frozen-score artifact

```yaml
model:
  type: fixed_score_artifact
  params:
    score_col: pred
```

The input must contain the column named by `score_col`. This path replays frozen scores as supplied and can validate an external strategy or a cross-repository signal handoff.

## Search discipline

The current public `strategy-pipeline` CLI does not expose alpha model-tuning or linear-sweep commands. The historical `strategy alpha tune`, `strategy alpha sweep-linear`, and `strategy summarize` examples are not supported by the current CLI. Confirm available commands with `strategy-pipeline --help` before relying on older notes.

When conducting a model search through a supported research runner, keep these boundaries:

1. Fix the data, target, features, and time split first.
2. Search `model.params`, `sample_weight`, and `train_window` during training.
3. After selecting a signal, use `strategy backtest grid` to test `top_k`, costs, buffers, and weights.
4. For small samples, use `min_cv_ic_valid_folds` to exclude trials with too few valid folds.
5. Keep the full trial ledger; do not record only the best configuration.

## Checks after a run

Inspect the run summary and evaluation artifacts for:

1. `eval.constant_prediction` for constant predictions.
2. `eval.zero_feature_importance` for zero feature importance.
3. `train_ic` and `test_ic` for the training/test gap.
4. `backtest_sharpe`, turnover, and costs for execution relevance.
5. Walk-forward and final out-of-sample evidence for stability over time.

For a fair model comparison, hold data assets, targets, time splits, costs, and portfolio construction constant. See [Overfitting Controls](overfitting-controls.md) for research governance.
