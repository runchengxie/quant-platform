"""Explicit historical export map for lazy compatibility loading."""

_EXPORTS = {
    "BACKTEST_BUNDLE_SCHEMA_VERSION": (
        "quant_platform._portfolio.backtest_bundle",
        "BACKTEST_BUNDLE_SCHEMA_VERSION",
    ),
    "BACKTEST_PERIODS_CONTRACT": (
        "quant_platform._portfolio.backtest_contracts",
        "BACKTEST_PERIODS_CONTRACT",
    ),
    "BACKTEST_RETURN_CONTRACT": (
        "quant_platform._portfolio.backtest_contracts",
        "BACKTEST_RETURN_CONTRACT",
    ),
    "CANONICAL_POSITIONS_BY_REBALANCE_META_FILE": (
        "quant_platform._portfolio.positions_artifact",
        "CANONICAL_POSITIONS_BY_REBALANCE_META_FILE",
    ),
    "EXECUTION_AWARE_BUNDLE_FILES": (
        "quant_platform._portfolio.backtest_bundle",
        "EXECUTION_AWARE_BUNDLE_FILES",
    ),
    "EXECUTION_SUMMARY_SCHEMA": (
        "quant_platform._portfolio.execution_summary",
        "EXECUTION_SUMMARY_SCHEMA",
    ),
    "INCUMBENT_REQUALIFICATION_SCHEMA": (
        "quant_platform._portfolio.incumbent_requalification",
        "INCUMBENT_REQUALIFICATION_SCHEMA",
    ),
    "PORTFOLIO_OPTIMIZATION_RESULT_SCHEMA": (
        "quant_platform._portfolio.optimization",
        "PORTFOLIO_OPTIMIZATION_RESULT_SCHEMA",
    ),
    "PORTFOLIO_POLICY_SCHEMA": (
        "quant_platform._portfolio.daily_watch20_policy",
        "PORTFOLIO_POLICY_SCHEMA",
    ),
    "POSITIONS_BY_REBALANCE_CONTRACT": (
        "quant_platform._portfolio.contracts",
        "POSITIONS_BY_REBALANCE_CONTRACT",
    ),
    "TRADABLE_FLAGS_CONTRACT": (
        "quant_platform._portfolio.backtest_contracts",
        "TRADABLE_FLAGS_CONTRACT",
    ),
    "BacktestBundleInventoryItem": (
        "quant_platform._portfolio.backtest_bundle",
        "BacktestBundleInventoryItem",
    ),
    "BacktestBundleManifest": (
        "quant_platform._portfolio.backtest_bundle",
        "BacktestBundleManifest",
    ),
    "BacktestEvidenceTier": ("quant_platform._portfolio.backtest_bundle", "BacktestEvidenceTier"),
    "BacktestPeriodsContract": (
        "quant_platform._portfolio.backtest_contracts",
        "BacktestPeriodsContract",
    ),
    "BacktestReturnSeriesContract": (
        "quant_platform._portfolio.backtest_contracts",
        "BacktestReturnSeriesContract",
    ),
    "BacktestSpec": ("quant_platform._portfolio.backtest_spec", "BacktestSpec"),
    "CostBreakdown": ("quant_platform._portfolio.types", "CostBreakdown"),
    "DailyWatch20Config": ("quant_platform._portfolio.daily_watch20", "DailyWatch20Config"),
    "DailyWatch20PortfolioPolicy": (
        "quant_platform._portfolio.daily_watch20_policy",
        "DailyWatch20PortfolioPolicy",
    ),
    "DailyWatch20Receipt": ("quant_platform._portfolio.daily_watch20", "DailyWatch20Receipt"),
    "DailyWatch20Result": ("quant_platform._portfolio.daily_watch20", "DailyWatch20Result"),
    "DailyWatch20SelectionError": (
        "quant_platform._portfolio.daily_watch20",
        "DailyWatch20SelectionError",
    ),
    "DetailedTradeFeeModel": ("quant_platform._portfolio.execution", "DetailedTradeFeeModel"),
    "EconomicRebalanceResult": (
        "quant_platform._portfolio.economic_rebalance",
        "EconomicRebalanceResult",
    ),
    "EqualWeightOptimizerBackend": (
        "quant_platform._portfolio.optimization",
        "EqualWeightOptimizerBackend",
    ),
    "GroupCap": ("quant_platform._portfolio.contracts", "GroupCap"),
    "GuardFactorSpec": ("quant_platform._portfolio.daily_watch20", "GuardFactorSpec"),
    "HrpConfig": ("quant_platform._portfolio.hrp", "HrpConfig"),
    "HrpOptimizerBackend": ("quant_platform._portfolio.optimization", "HrpOptimizerBackend"),
    "HrpResult": ("quant_platform._portfolio.hrp", "HrpResult"),
    "IncumbentRequalificationConfig": (
        "quant_platform._portfolio.incumbent_requalification",
        "IncumbentRequalificationConfig",
    ),
    "IncumbentRequalificationPolicy": (
        "quant_platform._portfolio.incumbent_requalification",
        "IncumbentRequalificationPolicy",
    ),
    "IncumbentRequalificationReceipt": (
        "quant_platform._portfolio.incumbent_requalification",
        "IncumbentRequalificationReceipt",
    ),
    "IncumbentRequalificationResult": (
        "quant_platform._portfolio.incumbent_requalification",
        "IncumbentRequalificationResult",
    ),
    "InverseVolConfig": ("quant_platform._portfolio.optimization", "InverseVolConfig"),
    "InverseVolOptimizerBackend": (
        "quant_platform._portfolio.optimization",
        "InverseVolOptimizerBackend",
    ),
    "LinearExposureConstraint": (
        "quant_platform._portfolio.optimization",
        "LinearExposureConstraint",
    ),
    "OptimizerRegistry": ("quant_platform._portfolio.optimization", "OptimizerRegistry"),
    "OutcomeDistributionReport": (
        "quant_platform._portfolio.outcome_metrics",
        "OutcomeDistributionReport",
    ),
    "PortfolioConstructionVariant": (
        "quant_platform._portfolio.benchmark_enhancement",
        "PortfolioConstructionVariant",
    ),
    "PortfolioOptimizationRequest": (
        "quant_platform._portfolio.optimization",
        "PortfolioOptimizationRequest",
    ),
    "PortfolioOptimizationResult": (
        "quant_platform._portfolio.optimization",
        "PortfolioOptimizationResult",
    ),
    "PortfolioOptimizerBackend": (
        "quant_platform._portfolio.optimization",
        "PortfolioOptimizerBackend",
    ),
    "PortfolioQpConfig": ("quant_platform._portfolio.optimization", "PortfolioQpConfig"),
    "PositionBacktestConfig": (
        "quant_platform._portfolio.position_backtest",
        "PositionBacktestConfig",
    ),
    "PositionBacktestEvaluation": (
        "quant_platform._portfolio.position_evaluation",
        "PositionBacktestEvaluation",
    ),
    "PositionBacktestResult": (
        "quant_platform._portfolio.position_backtest",
        "PositionBacktestResult",
    ),
    "PositionsByRebalanceFrameContract": (
        "quant_platform._portfolio.contracts",
        "PositionsByRebalanceFrameContract",
    ),
    "QpMinVarianceOptimizerBackend": (
        "quant_platform._portfolio.optimization",
        "QpMinVarianceOptimizerBackend",
    ),
    "RebalanceTurnoverReport": ("quant_platform._portfolio.turnover", "RebalanceTurnoverReport"),
    "SelectionSpec": ("quant_platform._portfolio.industry_sleeves", "SelectionSpec"),
    "SessionRebalanceSchedule": ("quant_platform._portfolio.rebalance", "SessionRebalanceSchedule"),
    "SizingConfig": ("quant_platform._portfolio.bet_sizing", "SizingConfig"),
    "StaggeredCohortExecutionConfig": (
        "quant_platform._portfolio.staggered_cohort_execution",
        "StaggeredCohortExecutionConfig",
    ),
    "StaggeredCohortExecutionResult": (
        "quant_platform._portfolio.staggered_cohort_execution",
        "StaggeredCohortExecutionResult",
    ),
    "StrategyRiskReport": ("quant_platform._portfolio.strategy_risk", "StrategyRiskReport"),
    "StrategySpec": ("quant_platform._portfolio.contracts", "StrategySpec"),
    "TCACalibrationReceipt": ("quant_platform._portfolio.tca_calibration", "TCACalibrationReceipt"),
    "TradableFlagsContract": (
        "quant_platform._portfolio.backtest_contracts",
        "TradableFlagsContract",
    ),
    "TurnoverBreakdown": ("quant_platform._portfolio.turnover", "TurnoverBreakdown"),
    "USDModeledExecutionPrice": (
        "quant_platform._portfolio.usd_ledger_models",
        "USDModeledExecutionPrice",
    ),
    "add_conservative_score": (
        "quant_platform._portfolio.robust_uncertainty",
        "add_conservative_score",
    ),
    "annualize_turnover": ("quant_platform._portfolio.turnover", "annualize_turnover"),
    "annualized_sharpe_to_periodic": (
        "quant_platform._portfolio.sharpe_inference",
        "annualized_sharpe_to_periodic",
    ),
    "annualized_variance_to_periodic": (
        "quant_platform._portfolio.sharpe_inference",
        "annualized_variance_to_periodic",
    ),
    "apply_no_trade_band": ("quant_platform._portfolio.economic_rebalance", "apply_no_trade_band"),
    "assert_backtest_periods_frame": (
        "quant_platform._portfolio.backtest_contracts",
        "assert_backtest_periods_frame",
    ),
    "assert_backtest_return_frame": (
        "quant_platform._portfolio.backtest_contracts",
        "assert_backtest_return_frame",
    ),
    "assert_positions_by_rebalance_frame": (
        "quant_platform._portfolio.contracts",
        "assert_positions_by_rebalance_frame",
    ),
    "assert_tradable_flags_frame": (
        "quant_platform._portfolio.backtest_contracts",
        "assert_tradable_flags_frame",
    ),
    "attach_entry_dates": ("quant_platform._portfolio.industry_sleeves", "attach_entry_dates"),
    "attribute_delayed_fills": (
        "quant_platform._portfolio.execution_diagnostics",
        "attribute_delayed_fills",
    ),
    "average_active_bets": ("quant_platform._portfolio.bet_sizing", "average_active_bets"),
    "backtest_topk": ("quant_platform._portfolio.api", "backtest_topk"),
    "box_worst_case_return": (
        "quant_platform._portfolio.robust_uncertainty",
        "box_worst_case_return",
    ),
    "build_backtest_periods_frame": (
        "quant_platform._portfolio.backtest_contracts",
        "build_backtest_periods_frame",
    ),
    "build_backtest_return_frame": (
        "quant_platform._portfolio.backtest_contracts",
        "build_backtest_return_frame",
    ),
    "build_comparison_receipt": (
        "quant_platform._portfolio.benchmark_comparison",
        "build_comparison_receipt",
    ),
    "build_portfolio_sizing_receipt": (
        "quant_platform._portfolio.evidence_receipts",
        "build_portfolio_sizing_receipt",
    ),
    "build_position_replay_periods": (
        "quant_platform._portfolio.position_replay",
        "build_position_replay_periods",
    ),
    "build_positions_envelope_v2": (
        "quant_platform._portfolio.positions_artifact",
        "build_positions_envelope_v2",
    ),
    "build_rebalance_turnover_report": (
        "quant_platform._portfolio.turnover",
        "build_rebalance_turnover_report",
    ),
    "build_sized_weights": ("quant_platform._portfolio.bet_sizing", "build_sized_weights"),
    "build_sizing_receipt": ("quant_platform._portfolio.bet_sizing", "build_sizing_receipt"),
    "build_target_weights": (
        "quant_platform._portfolio.benchmark_enhancement",
        "build_target_weights",
    ),
    "build_targets": ("quant_platform._portfolio.industry_sleeves", "build_targets"),
    "calibrate_cost_model": ("quant_platform._portfolio.tca_calibration", "calibrate_cost_model"),
    "combine_targets": ("quant_platform._portfolio.industry_sleeves", "combine_targets"),
    "compare_portfolio_returns": (
        "quant_platform._portfolio.benchmark_comparison",
        "compare_portfolio_returns",
    ),
    "compute_trade_summary": (
        "quant_platform._portfolio.trade_accounting",
        "compute_trade_summary",
    ),
    "conservative_score": ("quant_platform._portfolio.robust_uncertainty", "conservative_score"),
    "construct_positions_from_strategy": (
        "quant_platform._portfolio.strategy",
        "construct_positions_from_strategy",
    ),
    "deflated_sharpe_ratio": (
        "quant_platform._portfolio.sharpe_inference",
        "deflated_sharpe_ratio",
    ),
    "discretize_weights": ("quant_platform._portfolio.bet_sizing", "discretize_weights"),
    "drift_previous_weights": (
        "quant_platform._portfolio.trade_accounting",
        "drift_previous_weights",
    ),
    "evaluate_position_backtest": (
        "quant_platform._portfolio.position_evaluation",
        "evaluate_position_backtest",
    ),
    "execution_summary_frame": (
        "quant_platform._portfolio.execution_summary",
        "execution_summary_frame",
    ),
    "expected_max_sharpe": ("quant_platform._portfolio.sharpe_inference", "expected_max_sharpe"),
    "get_rebalance_events": ("quant_platform._portfolio.rebalance", "get_rebalance_events"),
    "get_session_interval_rebalance_dates": (
        "quant_platform._portfolio.rebalance",
        "get_session_interval_rebalance_dates",
    ),
    "hierarchical_risk_parity": ("quant_platform._portfolio.hrp", "hierarchical_risk_parity"),
    "implementation_shortfall_metrics": (
        "quant_platform._portfolio.strategy_risk",
        "implementation_shortfall_metrics",
    ),
    "l2_price_tiered_slippage": ("quant_platform._portfolio.execution", "l2_price_tiered_slippage"),
    "leg_attribution_frame": ("quant_platform._portfolio.metrics", "leg_attribution_frame"),
    "name_turnover": ("quant_platform._portfolio.turnover", "name_turnover"),
    "positions_by_rebalance_from_targets": (
        "quant_platform._portfolio.position_inputs",
        "positions_by_rebalance_from_targets",
    ),
    "probabilistic_sharpe_ratio": (
        "quant_platform._portfolio.strategy_risk",
        "probabilistic_sharpe_ratio",
    ),
    "probabilistic_sharpe_ratio_from_stats": (
        "quant_platform._portfolio.sharpe_inference",
        "probabilistic_sharpe_ratio",
    ),
    "probability_to_size": ("quant_platform._portfolio.bet_sizing", "probability_to_size"),
    "read_backtest_bundle": (
        "quant_platform._portfolio.backtest_bundle_io",
        "read_backtest_bundle",
    ),
    "reconcile_unified_ledger": (
        "quant_platform._portfolio.backtest_bundle",
        "reconcile_unified_ledger",
    ),
    "return_concentration": ("quant_platform._portfolio.strategy_risk", "return_concentration"),
    "rolling_hrp_weights": ("quant_platform._portfolio.hrp", "rolling_hrp_weights"),
    "run_backtest": ("quant_platform._portfolio.api", "run_backtest"),
    "run_native_position_replay": (
        "quant_platform._portfolio.position_replay",
        "run_native_position_replay",
    ),
    "run_position_backtest": (
        "quant_platform._portfolio.position_backtest",
        "run_position_backtest",
    ),
    "select_daily_watch20": ("quant_platform._portfolio.daily_watch20", "select_daily_watch20"),
    "select_incumbent_requalified_portfolio": (
        "quant_platform._portfolio.incumbent_requalification",
        "select_incumbent_requalified_portfolio",
    ),
    "select_industry_balanced": (
        "quant_platform._portfolio.industry_sleeves",
        "select_industry_balanced",
    ),
    "select_usd_modeled_execution_price": (
        "quant_platform._portfolio.usd_ledger_inputs",
        "select_usd_modeled_execution_price",
    ),
    "series_sha256": ("quant_platform._portfolio.evidence_receipts", "series_sha256"),
    "settle_execution_fills": (
        "quant_platform._portfolio.execution_ledger",
        "settle_execution_fills",
    ),
    "sha256_file": ("quant_platform._portfolio.evidence_receipts", "sha256_file"),
    "sharpe_standard_error": (
        "quant_platform._portfolio.sharpe_inference",
        "sharpe_standard_error",
    ),
    "simulate_staggered_cohort_execution": (
        "quant_platform._portfolio.staggered_cohort_execution",
        "simulate_staggered_cohort_execution",
    ),
    "strategy_failure_probability": (
        "quant_platform._portfolio.strategy_risk",
        "strategy_failure_probability",
    ),
    "strategy_from_config": ("quant_platform._portfolio.strategy", "strategy_from_config"),
    "summarize_leg_attribution": ("quant_platform._portfolio.metrics", "summarize_leg_attribution"),
    "summarize_outcome_distribution": (
        "quant_platform._portfolio.outcome_metrics",
        "summarize_outcome_distribution",
    ),
    "summarize_period_returns": ("quant_platform._portfolio.metrics", "summarize_period_returns"),
    "summarize_staggered_execution": (
        "quant_platform._portfolio.execution_summary",
        "summarize_staggered_execution",
    ),
    "summarize_strategy_risk": (
        "quant_platform._portfolio.strategy_risk",
        "summarize_strategy_risk",
    ),
    "target_turnover": ("quant_platform._portfolio.industry_sleeves", "target_turnover"),
    "turnover_from_trade_weights": (
        "quant_platform._portfolio.turnover",
        "turnover_from_trade_weights",
    ),
    "validate_backtest_periods_frame": (
        "quant_platform._portfolio.backtest_contracts",
        "validate_backtest_periods_frame",
    ),
    "validate_backtest_return_frame": (
        "quant_platform._portfolio.backtest_contracts",
        "validate_backtest_return_frame",
    ),
    "validate_execution_aware_bundle_inputs": (
        "quant_platform._portfolio.backtest_bundle",
        "validate_execution_aware_bundle_inputs",
    ),
    "validate_positions_by_rebalance_frame": (
        "quant_platform._portfolio.contracts",
        "validate_positions_by_rebalance_frame",
    ),
    "validate_targets": ("quant_platform._portfolio.industry_sleeves", "validate_targets"),
    "validate_tradable_flags_frame": (
        "quant_platform._portfolio.backtest_contracts",
        "validate_tradable_flags_frame",
    ),
    "write_backtest_bundle": (
        "quant_platform._portfolio.backtest_bundle_io",
        "write_backtest_bundle",
    ),
    "write_positions_by_rebalance_artifact": (
        "quant_platform._portfolio.positions_artifact",
        "write_positions_by_rebalance_artifact",
    ),
    "write_receipt": ("quant_platform._portfolio.evidence_receipts", "write_receipt"),
}
