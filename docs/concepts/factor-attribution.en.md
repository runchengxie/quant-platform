# Factor return and risk attribution

Language: English · [简体中文](factor-attribution.md)

`portfolio_backtester.factor_attribution` provides two calculation helpers:
`attribute_factor_return()` decomposes active return, and
`attribute_factor_risk()` decomposes active variance. Both use caller-supplied
weights, exposures, and factor inputs. They do not estimate those inputs.

## Return attribution

Let `w` be portfolio weights, `b` benchmark weights, `X` asset exposures, and
`f` factor returns:

```text
active_weights       = w - b
active_exposures     = X' active_weights
factor_contributions = active_exposures * f
active_return        = portfolio_return - benchmark_return
cost_contribution    = -transaction_cost
specific_return      = active_return - sum(factor_contributions) - cost_contribution
```

`portfolio_return` is the portfolio return after transaction costs;
`benchmark_return` must cover the same period. Pass `transaction_cost` as a
nonnegative return amount in the same units, such as `0.0005` for 5 bps. The
helper does not convert basis points or calculate returns and costs. The
specific return is the residual needed to reconcile the supplied net active
return with factor contributions and the separately reported cost drag.

The `factor_return_attribution.v1` receipt includes active exposures, factor
contributions, specific return, cost contribution, active return, and the
reconciled active return. The components sum to the supplied active return.

## Risk attribution

Let `F` be factor-return covariance and `s` the per-asset specific risk:

```text
factor_variance_contribution_i = e_i * (F e)_i
specific_variance              = sum((active_weight_j * s_j)^2)
active_variance                 = sum(factor_variance_contribution) + specific_variance
```

The helper requires `F` to be symmetric and positive semidefinite. It assumes
specific returns are independent across assets. Factor covariance and specific
risk must use compatible periods and units. The `factor_risk_attribution.v1`
receipt reports factor contributions, specific variance contribution, active
exposures, and active variance. It reports variance, not annualized risk.

## Input and scope limits

Portfolio weights, benchmark weights, and exposure rows must contain exactly
the same assets. Factor returns and both axes of the factor covariance must
match the exposure columns. Inputs must be finite; specific risk cannot be
negative. The helpers reject mismatched labels rather than aligning or filling
missing assets and factors silently.

These functions do not estimate exposures, factor returns, covariance, or
specific risk. They do not calculate Brinson allocation or selection effects.
Results are arithmetic decompositions of the supplied model inputs, not causal
claims about why a portfolio performed as it did.
