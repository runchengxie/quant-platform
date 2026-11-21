# Cross-sectional signal reliability

## Intent and scope

Add reusable research diagnostics for the case where an overall predictive
relationship does not establish reliable performance among the highest scores.
The first delivery includes tail returns, marginal head returns, conditional
factor evaluation, and a private research consumer. It provides evidence for
human research decisions; it does not select an optimal holding count or prove
causal factor contributions.

The platform accepts caller-supplied scored observations, realized labels,
controls, and optional matched out-of-sample model predictions. It neither
downloads data nor trains models. Research owns universe definitions, label
construction, maturity checks, split policy, trial history, and execution runs.

## Approaches

1. Extend the existing factor diagnostic result in place. This offers automatic
   pipeline inclusion but couples new statistical semantics to a legacy residual
   IC definition and changes established result contracts.
2. Add an independent, versioned signal reliability API and an explicit research
   runner. This preserves compatibility and allows common input/provenance and
   sample policies across all three diagnostics. Recommended approach; the user
   selected the initial platform/research slice and requested conditional factor
   evaluation in the same delivery.
3. Implement separate experiment scripts only. This is cheaper initially but
   duplicates statistics and makes cross-study comparisons harder.

Approach 2 is proposed. Existing factor diagnostics remain available unchanged.

## Public interfaces and ownership

Add `alpha_research.signal_reliability` with a result dataclass containing
`summary`, `by_date`, and `profile` tables. Expose three functions:

- `tail_return_profile`: equal-weight realized returns for disjoint score-rank
  bands and cumulative Top K portfolios.
- `marginal_alpha_profile`: date-paired Top K minus Next K realized label means;
  Next K comprises ranks K+1 through 2K. Also report Top K minus Top 2K, which
  equals half that spread only for complete equal-sized groups.
- `conditional_factor_profile`: raw and controlled cross-sectional evidence,
  plus optional paired model prediction evidence.

Each accepts a DataFrame with explicit date, symbol, score/factor and target
column names. K values, ascending/descending direction, minimum observations,
control columns and statistical settings are explicit arguments. No strategy
defaults, real strategy parameters or private data enter the public repository.
Use focused private modules for validation, uncertainty and conditional rows.

## Common input and inference contract

- Require unique non-null date/symbol keys, valid dates and explicitly named
  columns. Reject duplicate keys, conflicting column roles, invalid K values or
  invalid statistical settings. Sort dates chronologically.
- Rank the finite scores within each date before inspecting realized labels.
  Break score ties deterministically by symbol and report ties. Missing or
  infinite labels never move a lower-ranked stock into a selected band.
- Emit requested bands for every date, including unavailable/incomplete bands.
  Report requested/actual stock counts, finite label counts, and status. An
  incomplete or label-incomplete band has no return estimate by default.
  Do not shrink K silently or replace missing labels with zero.
- Summaries weight eligible dates equally. Keep all requested dates in the
  time grid. Use moving non-circular blocks of consecutive date positions,
  preserving missing positions; summarize finite observations within resamples
  and report effective dates and invalid resamples. Never bootstrap individual
  stocks as independent time observations.
- Caller chooses block length, bootstrap repetitions, seed, confidence level,
  and minimum usable dates. Reject block length larger than the date grid.
  Too few usable dates yields an unavailable interval, not a zero interval.
  Confidence intervals are pointwise descriptive intervals, without automatic
  multiple-testing correction or causal interpretation. Report these limits.
- Carry versioned artifact type, source fingerprints, column definitions,
  statistical settings, date range, sample coverage, caller provenance and
  warnings. Hash only relevant normalized input columns deterministically.
  A caller assertion of OOS or PIT status is recorded as declared, not verified.

## Tail and marginal returns

K boundaries define bands 1..K1, K1+1..K2, etc., plus each cumulative Top K.
Marginal analysis independently requires 2K available scores and complete
labels for both groups on each eligible date. Profile each paired spread
directly; do not infer its interval from overlapping separate group intervals.

Labels are supplied returns in decimal units. If the caller supplies benchmark
relative or risk-adjusted returns, retain that definition in metadata. The API
does not call raw differences causal alpha or estimate trading costs. Results
must distinguish statistical label returns from executed portfolio returns.

## Conditional factor evidence

For each factor/date, use a common complete-case sample for factor, label,
numeric controls and optional industry. Missing industry is missing data,
not a fabricated industry. Report raw full-sample coverage separately from
matched raw statistics so sample changes are visible.

On that common sample report:

1. Raw Spearman IC.
2. Partial rank IC: rank-transform the factor, target and numeric controls
   within date, build an intercept plus ranked numeric controls and industry
   dummies (drop one category), project both ranked factor and ranked target
   onto that design, then compute Pearson correlation of their residuals.
3. A conditional OLS coefficient: regress original-unit realized returns on a
   within-date standardized factor and standardized numeric controls plus
   industry dummies and intercept. Report coefficient per one cross-sectional
   factor standard deviation, observations, design rank and conditioning.

No implicit control discovery or automatic dropping of requested controls.
Require sufficient residual degrees of freedom. Flag constant factors,
rank-deficient designs and near-zero factor residual variance as unidentified;
do not manufacture a coefficient or correlation. A controls-free request may
report raw evidence but marks controlled evidence as not requested.

These statistics describe linear conditional relationships (rank-linear for
partial IC); they do not recover a hidden true return contribution. Preserve
the existing residual-factor-versus-raw-return IC behavior unchanged.

## Incremental model evidence

Accept optional baseline and augmented OOS score columns on exactly matched
date/symbol rows. Compute per-date paired Rank IC differences and paired Top K
label-return differences, with direct block intervals. Both portfolios use
the same complete prediction universe, and ranked selections retain missing
label failures instead of backfilling. Report coverage lost by matching.

Require caller metadata identifying baseline/augmented runs, feature change,
label, universe, split identity and prediction availability. Incompatible or
incomplete declared identities reject the comparison. Metadata cannot certify
absence of leakage. Predictions may be arbitrary ranking scores: never
subtract a score from a return or report regression error without calibration.
Absent paired predictions yields `not_provided`, not an inferred model gain.
Cost-adjusted incremental evidence requires separately supplied and matched
execution results; the initial API does not claim it from predicted scores.

## Research integration and data boundary

Add an opt-in research CLI/configuration consuming a caller-selected local
Parquet panel and provenance JSON. It writes versioned summary JSON and detail
tables under an explicit output directory in the owning project's data root,
rejecting output inside source checkouts/worktrees. No production pipeline
defaults or production strategy parameters change.

Use the merged platform public API, pin its merged revision and update the
research lockfile. Never copy the new statistics into the research repository
or leave it depending on a feature branch. Add an English usage/limitations
document and an aligned Chinese companion with reciprocal links.

Historical reproduction is a separate evidence step: inventory the referenced
saved panels, label definitions, data fingerprints and OOS dates read-only.
Run only when sufficient inputs are available and compatible. Otherwise record
the exact missing inputs and a reproducible command; do not claim independent
confirmation of previously reported returns or PIT correctness.

## Validation and delivery

Synthetic tests cover monotone, saturated and reversed tails; tied scores;
small universes; missing labels without rank backfill; deterministic paired
block intervals; missing dates; changing universes; and malformed inputs.

Conditional fixtures use known positive factor coefficients with independent
noise and with correlated negative controls. Test raw sign reversal versus
positive controlled evidence, industry controls, complete-case matching,
collinearity and constant factors. Incremental tests verify exact paired
samples, absent evidence and incompatible metadata.

Research tests exercise config parsing, provenance retention, output boundary,
serialization and use of the public provider API. Run platform-required locked
sync, Ruff and full pytest; run the affected research suite, static checks and
documentation checks according to repository instructions. Record the actual
source revisions and commands. Merge the provider before updating the consumer,
respect required remote checks, then clean only this task's branches/worktrees.

## Builder decisions and exclusions

The builder may choose exact helper names, table column names, serialization
layout and conservative numerical tolerances, documenting them in API usage.
Use existing NumPy/Pandas dependencies; add no model framework.

Excluded from this delivery: automatic K optimization, training new models,
causal attribution, production changes, new backtest execution/accounting,
uncertainty-based stock selection and public Observatory pages. Existing
execution systems remain the source of costs and tradability evidence.
