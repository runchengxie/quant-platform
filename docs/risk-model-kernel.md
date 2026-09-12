# Barra-like risk model kernel

`portfolio_backtester.risk_model` provides a small, public, strategy-agnostic
risk model for research diagnostics. It is deliberately a Barra-like kernel,
not a claim of compatibility with any commercial vendor model.

## Responsibility boundary

The caller owns the point-in-time (PIT) construction of exposures and returns.
The kernel does not fetch data, infer a security universe, build A-share
factors, or apply an index methodology. A-share factor builders and report
adapters belong in `quant-market-research`; private cash-flow, micro-cap, and
DailyWatch20 holdings belong in `quant-research`.

## Input contract

Exposures are a wide `pandas.DataFrame` with a two-level index named
`as_of_date` and `symbol`. Each remaining column is one factor exposure. The
return panel is a `Series` (or one-column `DataFrame` named `total_return`) with
the same index. Duplicate keys and non-finite returns are rejected. Missing
factor exposures are not silently imputed; rows lacking a complete set of
factors are excluded from that day's regression and appear in its diagnostics.

The PIT owner should record, alongside these frames, the source version,
publication timestamp, eligibility rules, corporate-action basis, and the
factor definition version. Those metadata are intentionally not guessed by
this numerical kernel.

## Estimation

`estimate_factor_returns` runs one weighted cross-sectional ridge regression
per date:

\[
r_{i,t} = X_{i,t} f_t + e_{i,t}.
\]

The kernel does not add an intercept. Supply an `intercept` exposure column if
the model specification requires one. The result contains factor returns,
fitted and residual asset returns, and date-level observation/rank/condition
number/weighted-R² diagnostics.

`build_risk_model` estimates an exponentially weighted factor covariance from
the trailing factor-return history, shrinks it toward a diagonal matrix, and
projects numerical negative eigenvalues to zero. Specific variance is the
exponentially weighted residual variance by symbol. These are statistical
stabilizers, not economic guarantees.

For portfolio weights \(w\), exposures \(B\), factor covariance \(\Sigma\),
and diagonal specific variance \(D\):

\[
b = B^T w,\qquad
\sigma^2_{factor} = b^T\Sigma b,\qquad
\sigma^2_{specific} = \sum_i w_i^2 D_i.
\]

`attribute_portfolio_risk` returns the factor exposure, Euler factor variance
contributions \(b_j(\Sigma b)_j\), specific variance, total variance, and
volatility. Contributions reconcile to factor variance by construction.

## Synthetic example

```python
factor_result = estimate_factor_returns(exposures, returns)
risk = build_risk_model(
    factor_result.factor_returns,
    factor_result.residual_returns,
)
attribution = attribute_portfolio_risk(
    weights,
    exposures_for_model_date,
    risk.factor_covariance,
    risk.specific_variance,
)
```

Use the diagnostics before interpreting a report: insufficient cross-sections,
poor matrix conditioning, missing PIT exposures, short residual histories, and
unstable covariance eigenvalues should be surfaced as evidence limitations.
