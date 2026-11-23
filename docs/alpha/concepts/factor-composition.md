# Factor composition

Use `alpha_research.factor_composition` to compare signal construction rules without changing portfolio sizing. The API is strategy independent; experiment hypotheses, datasets, OOS splits and promotion decisions belong to the consuming research project.

```python
from alpha_research.factor_composition import (
    FactorInput,
    FactorCompositionSpec,
    compose_factors,
)

spec = FactorCompositionSpec(
    composition_id="example_blend",
    version="v1",
    inputs=(FactorInput("Q", "example_quality", "v1"), FactorInput("V", "example_value", "v2")),
    method="interaction",
    weights={"Q": 0.4, "V": 0.4},
    interactions=(("Q", "V", 0.2),),
)
result = compose_factors(panel, spec)
```

`panel` is a pandas DataFrame with a unique two-level `date`/`symbol` MultiIndex; `date` contains pandas timestamps. Index level order does not matter. Rows retain their input order. Each input alias identifies a numeric column and a versioned registered factor. Input availability, universe membership, corporate actions and PIT alignment remain the caller's data contract. The composer does not certify those properties.

## Supported methods

| Method | Configuration and meaning |
| --- | --- |
| `equal` | Equal input coefficients. |
| `weighted` | Explicit signed `weights`; coefficients are literal, never implicitly normalized. |
| `rank` | Equal blend of per-date percentile average ranks, after direction alignment. Overrides `normalization`. |
| `hierarchical` | `groups` partitions all input aliases; equal coefficients inside each group and equal total group weights. |
| `residualized` | `residualize={target: [exposures]}` uses per-date OLS with an intercept, then blends residualized and remaining inputs. Regressions all use original preprocessed inputs; mapping order has no effect. Optional explicit weights. |
| `interaction` | Explicit main-effect weights plus `(left, right, coefficient)` terms. A centered product rewards both positive-positive and negative-negative inputs; it is not a standalone high-quality/cheap selector. |
| `conditional` | Preprocessed `gate > threshold` uses `weights`; otherwise `low_weights`. Gate direction and normalization match the other inputs. |
| `ic` / `icir` | Rolling cross-sectional Rank IC mean / unannualized mean-to-sample-standard-deviation ratio. Negative strengths are clipped to zero; declared factor directions are never silently reversed. ICIR standard deviations have a `1e-8` floor. |
| `covariance` | Solve a shrunk input correlation system against mean Rank IC, clip negative coefficients and normalize. This is a constrained heuristic, not a maximum-IR optimizer. |
| `pca` | Fit historical feature PCA; average the requested components after orienting each largest absolute loading positive. No return supervision or claim of Alpha optimality. |
| `ridge` / `pls` | Fit historical return regression. `regularization` is Ridge alpha; `n_components` controls PLS/PCA. |
| `lightgbm` | Optional bounded deterministic tree regressor; model search remains Research-owned. Install `quant-platform[composition-ml]`. |

Ridge, PLS and PCA require the existing `ml` extra or `composition-ml`. LightGBM uses 50 trees, 7 leaves, depth 3, minimum 5 rows per leaf, learning rate 0.05, L2 `regularization`, seed 0 and one worker. These fixed defaults are part of this implementation's provenance, not tuned strategy advice.

## Preprocessing and missingness

`direction` is exactly +1 or -1. `normalization` is `zscore` (default, population standard deviation), `rank`, or `none`, always per date. Constant observed columns become zero under z-score; missing entries remain missing. No winsorization, imputation or industry neutralization is implicit: perform those through the owning preprocessing pipeline and include them in the factor's versioned identity.

`missing_policy="propagate"` leaves a row's score missing when any required input is missing, even if its weight is zero. `"error"` rejects missing inputs. Infinite inputs, duplicate keys, unknown configuration keys, incomplete weights and invalid group definitions fail. Singular or saturated residualization fails instead of generating misleading residuals. Static residuals are not automatically restandardized.

## Historical fitting and leakage boundaries

Supervised methods require exactly aligned `labels` and `label_available_at` Series. Each fitting row must have both feature time and label availability strictly before its prediction time. Availability cannot precede feature time; timezone awareness must be consistent. The `window` is the most recent prior feature dates, not the number of matured observations. IC methods exclude an entire date until all its supplied labels have matured; valid complete cases must meet `min_cross_section`.

Warmup requires `min_periods` distinct training dates, plus enough valid rows. Insufficient history, unusable IC, no positive strength, absent prediction inputs or insufficient model rank produce missing scores and an explicit fit-audit status. There is no fallback equal-weight prediction. `max_weight_turnover` caps the L1 coefficient change between successive successful IC-family fits; it is not portfolio turnover and does not constrain Ridge/PLS/tree fits.

The pure composer supports prequential fitting using matured earlier outcomes. A locked OOS consumer can mask OOS labels before calling it. This policy belongs to the experiment, not to the factor formula. In particular, overlapping return labels require their real horizon-end availability; shifting the IC series by one row is insufficient.

## Provenance and catalog integration

`FactorCompositionSpec.from_mapping/to_mapping` uses `alpha_research.factor_composition.v1`. Frozen inputs and immutable coefficient mappings prevent configuration mutation. `fingerprint` hashes canonical configuration only; it is not a dataset digest or an implementation-code hash.

Results include scores, transformed inputs, effective linear coefficients and a fit audit. Audit rows include training boundaries, label availability, training digest, model-state digest when applicable, and status. Tree weights are missing because a nonlinear model has no equivalent fixed linear coefficient. PCA coefficients are loadings; Ridge/PLS intercepts and fitted model state are covered by the model-state digest, not added as an input factor.

Use `result.to_factor_spec(...)` to register the output in the existing FactorCatalog with versioned dependencies. Supply the actual owner, frequency, PIT semantics, universe semantics and implementation SHA-256. The description retains the composition configuration fingerprint. No second authoritative FactorSpec or ExperimentRegistry is introduced.

## Interaction research

`alpha_research.factor_composition_diagnostics.double_sort_profile` provides independent rank buckets, cell mean forward returns and the extreme-cell difference in differences. Ties stay together; missing or undersized extreme cells yield missing spreads. Restrict labels to the intended evaluation window and availability cutoff before calling it. This descriptive statistic is not causal evidence or a significance test.

Use the existing [factor diagnostics](../README.md), [feature evidence protocol](feature-research-protocol.en-US.md) and [overfitting controls](overfitting-controls.en-US.md) for marginal contribution, ablation and temporal validation. Scores can enter the existing signal artifact contract through a Research-owned adapter; composition does not allocate holdings or publish evidence.
