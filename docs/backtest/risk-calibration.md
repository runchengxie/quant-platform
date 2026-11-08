# Risk calibration and missingness

Language: English · [简体中文](risk-calibration.zh-CN.md)

`quant_platform.analytics.risk_calibration.audit_risk_calibration` compares supplied
forecast means and marginal risk with observed outcomes at exactly the same target
interval and unit. It retains unavailable, stale, missing and incompatible rows.
The result is a retrospective descriptive audit. It is not a point-in-time data
reader, an unseen-market test, or an actual-risk certificate. Existing risk-model
and aligned-risk defaults remain unchanged.

```python
from quant_platform.analytics.risk_calibration import audit_risk_calibration

report = audit_risk_calibration(
    forecasts,
    outcomes,
    as_of=audit_clock,
    minimum_observations=20,
)
```

## Required evidence

Inputs are pandas DataFrames. Every clock is an explicit timezone-aware timestamp
and is normalized to UTC. Numeric inputs may be missing, but supplied values must
be finite. No unknown return becomes zero. Empty frames retain the required
columns. Neither input is mutated.

| Forecast columns | Meaning |
| --- | --- |
| `symbol`, `target_start`, `target_end` | Named asset/factor, positive target interval |
| `forecast_at`, `available_at` | Decision and availability of the supplied forecast |
| `unit` | `return_fraction`, `return_bps`, `price_change:<currency>`, or `factor:<declared-unit>` |
| `forecast_mean` | Explicit expected outcome in `unit`, required even for an intentional zero-mean assumption |
| `forecast_variance` or `forecast_volatility` | At most one nonmissing measure per row. Variance is in squared units, volatility in `unit`. Both missing is retained as unknown |
| `liquidity`, `regime` | Nonblank caller cohort labels. Use an explicit `unknown` label if necessary |

| Outcome columns | Meaning |
| --- | --- |
| `symbol`, `target_start`, `target_end`, `unit` | Exact forecast matching key |
| `realized` | Observed outcome in the declared horizon unit |
| `available_at` | When this outcome became available, no earlier than observation completion |
| `observation_start`, `observation_end` | Actual observed interval, exposing stale endpoint evidence |

The forecast key additionally includes `forecast_at`, allowing several decisions
about one target. Duplicate keys fail rather than selecting a convenient version.
Outcome revisions must be resolved by the caller before auditing. Duration is
elapsed UTC nanoseconds, not inferred trading sessions. Units are exact declarations,
not provider-verified semantics. No annualization, currency conversion, factor
normalization or horizon scaling is performed. A price change in CNY must not be
labeled as a fractional return.

A variance pair requires forecast availability no later than decision, decision
no later than target start and `as_of`, and completed target and outcome availability
no later than `as_of`. Observed start and end must equal target start and end.
A missing exact key with another outcome for the same symbol/start is marked
`incompatible_outcome`. Every original forecast stays in `rows`, with `issues`
and `paired`. Every outcome stays in `outcomes`, including unmatched rows, with
`match_status`, `matched_forecasts` and its own availability/missingness issues.
A matching key alone does not imply an eligible pair.

Raw unavailable values remain visible for this retrospective audit, including
`matched_realized`. Consumers must use `paired` and the optional comparison status,
never treat the full table as a strategy-visible information set. Output-derived
forecast column names such as `paired`, `issues`, `horizon_ns`, `residual`,
`squared_residual`, `predicted_variance`, `matched_realized`, `exposure_status`,
`interval_status` and `interval_covered` are reserved and rejected as input names.
Other extra forecast columns are preserved, including arbitrary column names.

## Comparable denominators and sample evidence

`summary` separates exact `unit` and `horizon_ns`. `cohorts` additionally separates
`liquidity` and `regime`, retaining entirely missing illiquid cohorts. Coverage is
eligible variance pairs divided by all forecasts in that group. Predicted variance
and realized squared residual use exactly those same pairs:

- `residual = realized - forecast_mean`.
- `predicted_variance = forecast_variance`, or `forecast_volatility * forecast_volatility` once.
- `realized_squared_residual = mean(residual * residual)`.
- `variance_ratio = mean(residual * residual) / mean(predicted_variance)`.

These are descriptive conditional second-moment diagnostics, not an unbiased
variance estimator or a full covariance calibration. Known nonzero forecast means
are removed. Duplicate decisions and assets still weight the row-level moments
as rows, with their dependence counts separately visible. Different units or
horizons never share one numerical mean.

`tail_observations` counts positive-variance pairs only. `two_sigma_exceedances`
counts `abs(residual) > 2 * sqrt(predicted_variance)` strictly, and
`two_sigma_rate` uses that exact tail denominator. This is not a Gaussian 95%
coverage statement. Zero-variance pairs remain in moment diagnostics and are
separately counted by `zero_variance_nonzero_residuals`. A zero predicted mean
variance gives an unknown ratio. Empty coverage or tail denominators give unknown
rates and exceedance counts, not healthy zeros. Unrepresentable calculations fail
explicitly. Positive calculations cannot silently underflow to exact zero.
Scaled moment averaging avoids unnecessary summation overflow or premature
underflow.

For example, synthetic variances `[1, 1, 4, 4]`, zero means and outcomes
`[1, -3, 2, -6]` give predicted mean variance `2.5`, squared-residual mean `12.5`,
ratio `5` and two exceedances in four positive-variance pairs. Removing the final
two outcomes leaves predicted mean variance `1` and squared-residual mean `5`.
The absent higher-variance forecasts remain in coverage, not in just one moment.

Each summary reports nominal `paired_observations`, `distinct_target_intervals`
without multiplying by assets/decisions, and `nonoverlapping_target_intervals`.
The last is the maximum disjoint set using earliest-finish scheduling on half-open
`[start, end)` intervals. It is a dependence warning count, not an independence
estimator. Sixty correlated asset rows on two dates count as two target intervals.
Four daily-start two-day horizons have four distinct and two nonoverlapping intervals.

The positive-integer minimum defaults to 20 and is checked in every comparable
unit/duration group. Below-threshold distinct or nonoverlapping counts produce
`insufficient_target_intervals` or `insufficient_nonoverlapping_intervals`.
Otherwise status is still `descriptive_only_independence_unverified`. The overall
status retains any group's insufficiency. Cohort statuses remain visible.
`independence_status="unverified"` and `effective_independent_observations=None`
always apply. Nonoverlap does not remove serial, common-factor or selection
dependence. No confidence interval or power guarantee is manufactured.

## Optional supplied exposures and prediction bounds

An exposure comparison uses forecast `target_exposure`, `exposure_unit`,
`exposure_source`, `exposure_available_at` and outcome `actual_exposure`,
`exposure_unit`, `exposure_source`, `exposure_observed_at`, `exposure_available_at`.
Target availability must precede the decision. Actual observation lies within the
declared target interval, including its endpoints, and actual availability follows
observation and does not exceed `as_of`. Units must be identical nonblank labels.
No factor exposure is inferred from returns or covariance.

`exposure_comparison` retains target/actual values, sources, clocks, status,
`signed_gap = actual - target` and `absolute_gap`. `exposure_observations` counts
supported comparisons in each summary/cohort. Missing values, unit mismatches,
missing evidence and unavailable/out-of-horizon observations leave gaps unknown.
There is no averaging of gaps across incompatible exposure units. This comparison
has independent eligibility, so missing risk does not erase valid exposure gaps
and missing exposure does not invalidate valid variance pairs. Without supplied
exposure columns the optional table is `None` and supported count is zero.

Supply forecast `prediction_lower`, `prediction_upper`, `prediction_unit`,
`prediction_source`, `prediction_available_at` to audit explicit prediction bounds.
Bounds must be finite, ordered and in exactly the forecast outcome unit, available
by decision. Optional `prediction_nominal_level` lies strictly between 0 and 1.
No nominal probability is inferred when it is absent. Outcome availability and
actual horizon must satisfy the same observation checks as above.

`prediction_intervals` retains row-level supplied bounds, source, availability,
nominal level, status and inclusive `covered = lower <= realized <= upper`.
Summaries expose `interval_observations`, `interval_covered` and
`interval_coverage` from supported bounds/outcomes only. Missing bound or outcome
evidence leaves coverage unknown. These comparisons do not require variance or
mean evidence and never derive bounds from sigma. Mixed nominal levels remain
visible row by row, and their pooled descriptive fraction is not calibration at
one claimed nominal level. Without supplied bounds the table is `None`.

## Supplied covariance rank and provenance

Optional forecast `raw_covariance`, `covariance_labels`, `covariance_unit`,
`covariance_available_at`, `covariance_source` provide auditable matrix values,
unique nonblank dimension labels, exactly `<unit>^2`, availability by decision and
a caller source identity. Optional `shrunk_covariance` uses the same labels/unit.
Matrices must be finite, square, symmetric and positive semidefinite within
scale-relative floating-point tolerance. `rank_diagnostics` computes raw and
supplied shrunk matrix rank with NumPy's default rank tolerance, reports dimension
and preserves raw rank deficiency even when the supplied shrunk matrix is full rank.
Missing raw matrices or scalar-only rank assertions produce unavailable ranks.
Future evidence cannot support rank. Incomplete/invalid supplied matrix contracts
fail. This does not audit the fitting sample, shrinkage coefficient or transform,
heterogeneous factor units, economic covariance, or realized cross-asset covariance.
A PSD or full-rank matrix never establishes calibration.

`input_digest` hashes ordered JSON-serialized input records, excluding pandas
index labels. It binds these parsed values, not original source-file bytes,
provider authenticity or economic truth. Caller manifests must separately bind
raw source bytes, model/fit version and clocks, code/consumer revisions, unit
semantics and provenance. `provenance_status="caller_asserted"`,
`real_calibration="unavailable"` and `certified=False` remain explicit. Seen
historical samples remain seen. Independent later observations and justified
clustered uncertainty require separate research evidence.

Synthetic acceptance cases are in
[`tests/test_risk_calibration.py`](https://github.com/runchengxie/quant-platform/blob/main/tests/test_risk_calibration.py).
See also [the risk-model kernel](../risk-model-kernel.md) and
[cost evidence](transaction-cost-evidence.md).
