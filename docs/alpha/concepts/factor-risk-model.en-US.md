# Factor Risk Model Boundary

Language: English · [简体中文](factor-risk-model.md)

`quant-market-research` maintains a lightweight, framework-neutral factor-risk capability. It converts precomputed factor-return and asset-specific-return histories into a point-in-time risk estimate.

## Model

For exposure matrix `X`, factor covariance `F`, and diagonal specific variance `D`, asset covariance is projected as:

```text
Sigma_asset = X F X' + D
```

The implementation does not estimate factor returns from stock returns. Factor construction is a research assumption supplied explicitly by the caller. This function validates and summarizes historical inputs already produced by the research layer.

## Inputs

- Current or as-of asset-by-factor exposures
- Historical factor returns
- Historical asset-specific returns
- An explicit `as_of` timestamp
- A covariance estimate with shrinkage toward the factor-variance diagonal
- A minimum number of common observations

Every return observation must be on or before `as_of`; future rows are rejected.

## Output

`FactorRiskModelEstimate` contains:

- Factor covariance
- Specific risk for each asset
- Asset exposures
- History start/end and observation count
- Estimator configuration
- An `asset_covariance()` projection
- Versioned receipt metadata

The covariance projection uses specific variance, computed by squaring the stored specific-risk values.

## Future work

- Evaluate industry/style factor sets and estimation windows.
- Add estimator comparisons and stability diagnostics.
- Publish risk-model evidence through research artifacts.
- Integrate an authoritative estimate into `portfolio_backtester` optimization requests.
- Compare against licensed RQData risk-model outputs when authorized data is available.

Third-party risk-model objects must remain inside adapters. Promotion evidence must distinguish estimator quality from optimizer quality.
