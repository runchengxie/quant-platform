# Cross-sectional signal reliability

Language: English · [简体中文](signal-reliability.zh-CN.md)

Use these diagnostics to test whether the highest-scoring stocks have additional
predictive information and whether a factor retains information after controlling
for specified exposures. These are descriptive research statistics, not executed
portfolio results, causal attribution or an automatic choice of holding count.

## API

```python
from alpha_research.signal_reliability import (
    BlockStatistics, tail_return_profile, marginal_alpha_profile,
    conditional_factor_profile,
)

stats = BlockStatistics(block_length=5, repetitions=1000, min_dates=20, seed=7)
# panel: one row per trade_date/symbol, with caller-defined numeric columns.
tail = tail_return_profile(
    panel, score_col="score", target_col="future_return", ks=(10, 20, 50), statistics=stats,
)
marginal = marginal_alpha_profile(
    panel, score_col="score", target_col="future_return", ks=(10, 20, 50), statistics=stats,
)
conditional = conditional_factor_profile(
    panel, factor_cols=("factor",), control_cols=("size", "value"),
    industry_col="industry", min_obs=30, target_col="future_return",
    ks=(10, 20, 50), statistics=stats,
)
```

Column defaults for keys are `trade_date` and `symbol`; override `date_col` and
`symbol_col` when needed. K values must be strictly increasing positive integers.
Scores are descending unless `ascending=True`. Target values must be decimal
realized returns, with their horizon, benchmark and adjustment described in
`provenance`. No benchmark adjustment happens automatically.

All calls return `SignalReliabilityResult(summary, by_date, profile)`.

| Table | Meaning |
| --- | --- |
| `summary` | Artifact type, schema version 1, relevant-input fingerprint, date range, definitions, settings, declared provenance, warnings |
| `by_date` | `date`, `group`, `metric`, `value`, eligibility `status`, counts and diagnostic fields |
| `profile` | Date-equal `mean`, `n_dates`, `n_eligible_dates`, `ci_low`, `ci_high`, `invalid_resamples`, `interval_status` by group/metric |

Date keys are converted to UTC calendar dates; supply naive dates for a local
trading-date contract. Symbols become strings. Duplicate keys after normalization
are rejected. Input row order does not affect selections or fingerprints.
Nonfinite numeric values are treated as missing. Column roles must be distinct.

## Tail and marginal evidence

Tail groups are `band:start:end` and `top:K`. Bands are disjoint, starting at rank
one. Stocks are ranked by finite score, breaking ties by symbol, before inspecting
labels. A selected stock with a missing label is never replaced. Returns require
a full band and all its labels. Counts show `requested_count`, `actual_count`,
`n_labels`, `n_scores`, and `n_universe`. Status is `ok`, `missing_labels`, or
`insufficient_scores`; unavailable values are NaN. `tied_score_rows` in the summary
counts all rows sharing a score on their date.

Marginal groups are `top_minus_next:K` and `top_minus_2k:K`, metric `return_spread`.
The first compares ranks 1..K against K+1..2K; the second is half that spread for
these equal-weight, equal-sized groups. Both require all 2K scores and labels.
Their intervals are computed on the paired date spread, not by comparing two
separate confidence intervals. The name does not imply risk-adjusted or causal
alpha unless the caller has explicitly constructed an appropriate label.

## Conditional evidence

Each factor has group `factor:name` and these metrics:

- `raw_full_rank_ic`: Spearman IC on all finite factor/target pairs.
- `raw_rank_ic`: Spearman IC on the common complete-case sample used by controls.
- `partial_rank_ic`: Pearson correlation between residualized ranked factor and
  ranked target. Numeric controls are ranked and standardized; industry uses
  drop-first dummy indicators and the design includes an intercept.
- `conditional_coefficient`: OLS return slope for one factor standard deviation
  (`ddof=0`), controlling standardized numeric exposures, industry and intercept.

Both ranked factor and ranked target are projected onto the same design for
partial IC. This differs from the historical factor-residual-versus-raw-target
IC, whose behavior remains unchanged. Neither statistic is a causal contribution
or a nonlinear conditional-independence test.

Rows report `n_obs`, `n_raw_obs`, `n_universe`, and for controlled metrics
`design_rank`, `design_columns`, `condition_number`. Requested missing controls
are not silently dropped; missing industry is excluded rather than treated as a
new category. Constant or rank-deficient designs, condition numbers over `1e10`,
and factor residual standard deviation below `1e-8` are `unidentified`. The
factor/controls are standardized before these checks. Rank and return regressions
are checked independently. Other statuses are `insufficient_observations`,
`insufficient_degrees_of_freedom`, and `not_requested` when no controls are given.
`min_obs` must be at least three; usable observations must also exceed the full
design's column count.

### Paired model evidence

Optionally pass `baseline_col`, `augmented_col` and `paired_provenance`:

```python
identity = dict(label_id="label-v1", universe_id="universe-v1", split_id="oos-v1",
                prediction_availability="before_label_start")
paired = dict(
    baseline=identity | {"run_id": "baseline-run"},
    augmented=identity | {"run_id": "factor-added-run"},
    feature_change="Add the candidate factor; keep other settings fixed",
)
```

Both identities must match except distinct nonempty run IDs. This is a declaration,
not a leakage audit. Match both finite prediction columns on the same keys first;
report `n_prediction_pairs` and original `n_universe`. IC further requires valid
labels; Top K ranks before checking labels. Group `incremental` reports
`rank_ic_delta`; `incremental:top:K` reports `top_return_delta`, always augmented
minus baseline. No subtraction of arbitrary scores from returns occurs. Absent
predictions gives `incremental_status=not_provided`; supplied evidence is
`provided_declared_oos`. Costs and actual tradability require separate execution
results; this API does not infer their incremental effect.

## Time dependence, provenance and limits

Moving non-circular blocks sample positions in the full supplied date grid,
including dates with unavailable metrics. Each resample draws enough full blocks
and truncates to the original length. Calendar dates absent entirely from the
panel cannot be inferred. Block length is in supplied dates and cannot exceed
that grid; choose it for label overlap and serial dependence. Settings include
positive repetitions, at least two `min_dates`, nonnegative seed and confidence
strictly between zero and one.

NaNs remain inside sampled blocks, then finite sampled values are averaged.
A resample with fewer than `min_dates` usable values is invalid. Fewer than 90%
valid resamples (or fewer than two) produces `insufficient_resamples`; too few
original usable dates produces `insufficient_dates`. The mean is still reported
when available. Intervals require status `ok` and are percentile pointwise
intervals; no selection-bias or multiple-comparison correction is applied.

`provenance` accepts JSON-compatible metadata. Record label maturity, data and
model revisions, universe, split identity, control availability, return treatment
and prior trials. Fingerprints identify normalized relevant input values, not
PIT correctness, training isolation or execution realism. Do not use these results
alone to promote a strategy. Research configuration, outputs and private panels
belong to their owning research project, outside this public source repository.
