# Formation-date style-factor cross-sections

Language: English · [简体中文](style-factor-cross-sections.md)

`alpha_research.style_factors` computes style factors from DataFrames. Pass `formation_universe` to recalculate cross-sectional factors for a specified set of securities on each formation date without shortening their historical rolling windows.

## Formation universe

`formation_universe` contains unique `trade_date` and `symbol` keys. It expresses membership only. The caller must define any ST, suspension, market-cap, listing-age, index-constituent, or other eligibility rules; the package does not infer them. Duplicate date/symbol keys fail closed.

The computation order is:

1. Calculate rolling features such as momentum, volatility, and beta from the full daily history.
2. Select formation dates and align valuation and PIT fundamentals.
3. Filter rows using `formation_universe`.
4. Recompute cross-sectional quality measures and other formation-date factors on the filtered rows.
5. Apply PIT industry demeaning and final cross-sectional z-scores.

Thus the universe filter does not truncate retained securities' history, while cross-sectional transforms use the selected universe.

## Standardize an existing panel

`standardize_factor_panel` applies, by default, 1st/99th percentile winsorization within each `trade_date`, then industry demeaning when `industry_l1` is available, then a date-level z-score. A zero-variance cross-section returns `NaN`.

```python
from alpha_research.style_factors import standardize_factor_panel

standardized = standardize_factor_panel(
    raw_factor_panel,
    factor_columns=("factor_size", "factor_value"),
)
```

This helper does not select a universe, read files, or access the data platform. Callers can explicitly configure the date column, industry column, and winsorization quantiles. Without `formation_universe`, `compute_factors` retains its existing full-cross-section behavior.
