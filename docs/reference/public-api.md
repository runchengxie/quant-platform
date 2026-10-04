# Public API

Language: English · [简体中文](public-api.zh-CN.md)

The following objects are exported directly from `portfolio_backtester`:

| Category | Public exports |
| --- | --- |
| Score-driven backtests | `BacktestSpec`, `run_backtest`, `backtest_topk` |
| Strategy and position construction | `StrategySpec`, `GroupCap`, `strategy_from_config`, `construct_positions_from_strategy` |
| DailyWatch20 compatibility API | `DailyWatch20Config`, `DailyWatch20Receipt`, `DailyWatch20Result`, `DailyWatch20SelectionError`, `GuardFactorSpec`, `select_daily_watch20` |
| DailyWatch20 portfolio policy | `PORTFOLIO_POLICY_SCHEMA`, `DailyWatch20PortfolioPolicy` |
| Incumbent requalification portfolios | `INCUMBENT_REQUALIFICATION_SCHEMA`, `IncumbentRequalificationPolicy`, `IncumbentRequalificationConfig`, `IncumbentRequalificationResult`, `IncumbentRequalificationReceipt`, `select_incumbent_requalified_portfolio` |
| Staggered-cohort execution | `StaggeredCohortExecutionConfig`, `StaggeredCohortExecutionResult`, `simulate_staggered_cohort_execution` |
| Staggered-execution summaries | `EXECUTION_SUMMARY_SCHEMA`, `summarize_staggered_execution`, `execution_summary_frame` |
| Position backtests | `PositionBacktestConfig`, `PositionBacktestResult`, `run_position_backtest` |
| Research position replay | `positions_by_rebalance_from_targets`, `build_position_replay_periods`, `run_native_position_replay` |
| Canonical backtest evidence | `BACKTEST_BUNDLE_SCHEMA_VERSION`, `EXECUTION_AWARE_BUNDLE_FILES`, `BacktestEvidenceTier`, `BacktestBundleInventoryItem`, `BacktestBundleManifest`, `reconcile_unified_ledger`, `validate_execution_aware_bundle_inputs`, `write_backtest_bundle`, `read_backtest_bundle` |
| Delayed-fill diagnostics | `attribute_delayed_fills` |
| TCA cost calibration | `TCACalibrationReceipt`, `calibrate_cost_model` |
| Historical fill settlement | `settle_execution_fills` |
| Position benchmark evaluation | `PositionBacktestEvaluation`, `evaluate_position_backtest` |
| Position contracts | `POSITIONS_BY_REBALANCE_CONTRACT`, `PositionsByRebalanceFrameContract`, `validate_positions_by_rebalance_frame`, `assert_positions_by_rebalance_frame` |
| Backtest output contracts | `BACKTEST_PERIODS_CONTRACT`, `BACKTEST_RETURN_CONTRACT`, `TRADABLE_FLAGS_CONTRACT`, `BacktestPeriodsContract`, `BacktestReturnSeriesContract`, `TradableFlagsContract`, `build_backtest_periods_frame`, `build_backtest_return_frame`, `validate_backtest_periods_frame`, `validate_backtest_return_frame`, `validate_tradable_flags_frame`, `assert_backtest_periods_frame`, `assert_backtest_return_frame`, `assert_tradable_flags_frame` |
| Position artifact writing | `CANONICAL_POSITIONS_BY_REBALANCE_META_FILE`, `write_positions_by_rebalance_artifact`, `build_positions_envelope_v2` |
| Fees and slippage | `DetailedTradeFeeModel`, `l2_price_tiered_slippage` |
| Session-based rebalancing | `SessionRebalanceSchedule`, `get_session_interval_rebalance_dates` |
| Index-enhancement construction | `PortfolioConstructionVariant`, `build_target_weights` |
| Portfolio comparison and staggered rebalancing | `build_comparison_receipt`, `compare_portfolio_returns`, `get_rebalance_events` |
| Turnover and costs | `TurnoverBreakdown`, `RebalanceTurnoverReport`, `CostBreakdown`, `name_turnover`, `annualize_turnover`, `turnover_from_trade_weights`, `build_rebalance_turnover_report` |
| Trade accounting | `compute_trade_summary`, `drift_previous_weights` |
| Return summaries | `summarize_period_returns` |
| Signal-leg attribution | `leg_attribution_frame`, `summarize_leg_attribution` |
| Sharpe-ratio inference | `probabilistic_sharpe_ratio`, `probabilistic_sharpe_ratio_from_stats`, `deflated_sharpe_ratio`, `expected_max_sharpe`, `sharpe_standard_error`, `annualized_sharpe_to_periodic`, `annualized_variance_to_periodic` |
| Position sizing | `SizingConfig`, `average_active_bets`, `build_sized_weights`, `build_sizing_receipt`, `discretize_weights`, `probability_to_size` |
| Hierarchical risk parity | `HrpConfig`, `HrpResult`, `hierarchical_risk_parity`, `rolling_hrp_weights` |
| Portfolio optimization | `PORTFOLIO_OPTIMIZATION_RESULT_SCHEMA`, `PortfolioOptimizationRequest`, `PortfolioOptimizationResult`, `PortfolioOptimizerBackend`, `EqualWeightOptimizerBackend`, `HrpOptimizerBackend`, `InverseVolConfig`, `InverseVolOptimizerBackend`, `LinearExposureConstraint`, `OptimizerRegistry`, `PortfolioQpConfig`, `QpMinVarianceOptimizerBackend` |
| Economic rebalancing | `EconomicRebalanceResult`, `apply_no_trade_band` |
| Robust-uncertainty primitives | `conservative_score`, `add_conservative_score`, `box_worst_case_return` |
| Outcome distributions and path diagnostics | `OutcomeDistributionReport`, `summarize_outcome_distribution` |
| Industry-balanced sleeves | `SelectionSpec`, `select_industry_balanced`, `build_targets`, `combine_targets`, `attach_entry_dates`, `target_turnover`, `validate_targets` |
| Strategy risk | `StrategyRiskReport`, `implementation_shortfall_metrics`, `return_concentration`, `strategy_failure_probability`, `summarize_strategy_risk` |
| Evidence receipts | `build_portfolio_sizing_receipt`, `series_sha256`, `sha256_file`, `write_receipt` |
| Modeled USD next-open research | `USDModeledExecutionPrice`, `select_usd_modeled_execution_price` |

The canonical backtest bundle uses the existing `UnifiedLedger` as its sole ledger source. It does not reimplement order, fill, or cash models. The `diagnostic` evidence tier may omit executable evidence. The `execution_aware` tier requires a backend that explicitly supports order lifecycles and a daily ledger, a complete `research.clock.v1` execution window, and account reconciliation satisfying `nav = cash + positions_value`. `write_backtest_bundle` writes Parquet and JSON files to a temporary sibling directory, creates a SHA-256 inventory, and atomically switches to the final directory. `read_backtest_bundle` validates the inventory against file hashes by default. See [Canonical backtest bundles](../concepts/canonical-backtest-bundle.md) for the full semantics.

`USDModeledExecutionPrice` and `select_usd_modeled_execution_price` support an
explicit opt-in diagnostic path for caller-supplied next-open references. They
preserve model and source lineage and never create broker orders or fills. See
[USD price ledger](usd-price-ledger.md) for the opt-in, timestamp, and FX rules.

`probabilistic_sharpe_ratio` accepts a return series. `probabilistic_sharpe_ratio_from_stats` accepts an already-computed periodic Sharpe ratio, skewness, and excess kurtosis.

The robust-uncertainty functions apply only box-uncertainty transformations explicitly supplied by the caller. `conservative_score` computes `score - aversion * uncertainty`; `box_worst_case_return` computes the linear worst-case return for fixed weights. They do not infer uncertainty from alpha scores and do not implement DRO, MILP, or portfolio optimization. For formal research, `uncertainty` and `uncertainty_radius` should come from strict out-of-sample evidence and preserve point-in-time semantics at each rebalance.

Outcome-distribution functions summarize realized trade or position results. `summarize_outcome_distribution` accepts realized return, MFE, MAE, peak giveback, and holding period, then returns return quantiles, loss probability, 5% CVaR, and path/holding-period summaries. It rejects empty inputs, non-finite values, inconsistent lengths, and data that violate path semantics. It does not forecast future outcomes or determine whether a target outcome is theoretically achievable.

`DailyWatch20` is a compatibility exception used by existing callers. New research assumptions, features, and promotion rules belong to the research and orchestration layers.

Staggered-cohort execution creates `horizon_days` independent cohorts and initially allocates `1 / horizon_days` of portfolio capital to each cohort. H1 has one cohort and therefore uses all initial capital. The summary `total_return` is the cumulative return of the entire ledger, not a single-cohort return divided again by the holding period. By default, the number of signal candidates must be at least `top_n`. Fewer candidates are allowed only when `allow_cash_shortfall=True`; unfilled fixed slots then remain in cash instead of being reallocated to selected stocks.

Execution capacity and daily-NAV simulation are imported from `portfolio_backtester.execution_sim`; see [Execution simulation](../guides/execution-simulation.md). AFML sizing and risk APIs are documented in [AFML sizing, hierarchical risk parity (HRP), and strategy risk](../concepts/afml-sizing-and-risk.md).

The decision-time data-clock view is imported from `portfolio_backtester.point_in_time`. See [Reading research inputs as of a decision time](../guides/point-in-time-data.md) for its use and input-publication requirements.

The unified execution replay for multiple rebalances imports `SequencedExecutionBackend` and `SequencedExecutionRequest` from `portfolio_backtester.backends`. See [Unified execution replay for multiple decisions](../guides/sequenced-execution.md) for input clocks and evidence boundaries.

Modules not listed among the top-level exports may still be used internally, but their interfaces have lower stability guarantees than the public exports above.

The complete export list is maintained in `packages/portfolio-backtester/src/portfolio_backtester/__init__.py`.
