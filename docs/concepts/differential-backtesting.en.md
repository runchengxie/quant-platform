# Differential backtesting

Language: English · [简体中文](differential-backtesting.md)

External backtest engines can provide independent comparisons, but they do not become the platform's source of truth. An adapter first normalizes its output to `CanonicalBacktestResult`; `compare_backtest_results()` then compares it with a selected reference backend.

The report localizes differences across:

- Shared numeric performance fields, keyed by `period_end`.
- Position weights, keyed by `rebalance_date` and `symbol`.
- Shared daily-ledger values such as cash, position value, and NAV, keyed by `trade_date`.
- Row counts for each canonical result frame.
- Declared backend capabilities, including market-rule coverage.

The default numeric tolerance is `1e-8`. Missing comparison values and differences beyond that tolerance are reported. The comparison runs after normalization, so it does not depend on third-party object models.

This is the basis for the RQAlpha A-share differential adapter. Any future adapter should use fixed fixtures and explain remaining differences in terms of market rules, execution timing, fees, cash accounting, or unsupported capabilities. Framework-specific comparison logic does not belong in the shared platform.

Orders and fills are currently compared by row count only. Their normalized identifiers are backend-local, so the report does not claim that individual orders or fills match. A future semantic comparison needs stable matching keys before comparing trades one by one.
