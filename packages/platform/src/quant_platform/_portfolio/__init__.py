"""Lazy public exports; importing a module does not load unrelated simulators."""

from importlib import import_module
from typing import TYPE_CHECKING

from ._public_exports import _EXPORTS

__all__ = [
    "BACKTEST_BUNDLE_SCHEMA_VERSION",
    "BACKTEST_PERIODS_CONTRACT",
    "BACKTEST_RETURN_CONTRACT",
    "CANONICAL_POSITIONS_BY_REBALANCE_META_FILE",
    "EXECUTION_AWARE_BUNDLE_FILES",
    "EXECUTION_SUMMARY_SCHEMA",
    "INCUMBENT_REQUALIFICATION_SCHEMA",
    "PORTFOLIO_OPTIMIZATION_RESULT_SCHEMA",
    "PORTFOLIO_POLICY_SCHEMA",
    "POSITIONS_BY_REBALANCE_CONTRACT",
    "TRADABLE_FLAGS_CONTRACT",
    "BacktestBundleInventoryItem",
    "BacktestBundleManifest",
    "BacktestEvidenceTier",
    "BacktestPeriodsContract",
    "BacktestReturnSeriesContract",
    "BacktestSpec",
    "CostBreakdown",
    "DailyWatch20Config",
    "DailyWatch20PortfolioPolicy",
    "DailyWatch20Receipt",
    "DailyWatch20Result",
    "DailyWatch20SelectionError",
    "DetailedTradeFeeModel",
    "EconomicRebalanceResult",
    "EqualWeightOptimizerBackend",
    "GroupCap",
    "GuardFactorSpec",
    "HrpConfig",
    "HrpOptimizerBackend",
    "HrpResult",
    "IncumbentRequalificationConfig",
    "IncumbentRequalificationPolicy",
    "IncumbentRequalificationReceipt",
    "IncumbentRequalificationResult",
    "InverseVolConfig",
    "InverseVolOptimizerBackend",
    "LinearExposureConstraint",
    "OptimizerRegistry",
    "OutcomeDistributionReport",
    "PortfolioConstructionVariant",
    "PortfolioOptimizationRequest",
    "PortfolioOptimizationResult",
    "PortfolioOptimizerBackend",
    "PortfolioQpConfig",
    "PositionBacktestConfig",
    "PositionBacktestEvaluation",
    "PositionBacktestResult",
    "PositionsByRebalanceFrameContract",
    "QpMinVarianceOptimizerBackend",
    "RebalanceTurnoverReport",
    "SelectionSpec",
    "SessionRebalanceSchedule",
    "SizingConfig",
    "StaggeredCohortExecutionConfig",
    "StaggeredCohortExecutionResult",
    "StrategyRiskReport",
    "StrategySpec",
    "TCACalibrationReceipt",
    "TradableFlagsContract",
    "TurnoverBreakdown",
    "USDModeledExecutionPrice",
    "add_conservative_score",
    "annualize_turnover",
    "annualized_sharpe_to_periodic",
    "annualized_variance_to_periodic",
    "apply_no_trade_band",
    "assert_backtest_periods_frame",
    "assert_backtest_return_frame",
    "assert_positions_by_rebalance_frame",
    "assert_tradable_flags_frame",
    "attach_entry_dates",
    "attribute_delayed_fills",
    "average_active_bets",
    "backtest_topk",
    "box_worst_case_return",
    "build_backtest_periods_frame",
    "build_backtest_return_frame",
    "build_comparison_receipt",
    "build_portfolio_sizing_receipt",
    "build_position_replay_periods",
    "build_positions_envelope_v2",
    "build_rebalance_turnover_report",
    "build_sized_weights",
    "build_sizing_receipt",
    "build_target_weights",
    "build_targets",
    "calibrate_cost_model",
    "combine_targets",
    "compare_portfolio_returns",
    "compute_trade_summary",
    "conservative_score",
    "construct_positions_from_strategy",
    "deflated_sharpe_ratio",
    "discretize_weights",
    "drift_previous_weights",
    "evaluate_position_backtest",
    "execution_summary_frame",
    "expected_max_sharpe",
    "get_rebalance_events",
    "get_session_interval_rebalance_dates",
    "hierarchical_risk_parity",
    "implementation_shortfall_metrics",
    "l2_price_tiered_slippage",
    "leg_attribution_frame",
    "name_turnover",
    "positions_by_rebalance_from_targets",
    "probabilistic_sharpe_ratio",
    "probabilistic_sharpe_ratio_from_stats",
    "probability_to_size",
    "read_backtest_bundle",
    "reconcile_unified_ledger",
    "return_concentration",
    "rolling_hrp_weights",
    "run_backtest",
    "run_native_position_replay",
    "run_position_backtest",
    "select_daily_watch20",
    "select_incumbent_requalified_portfolio",
    "select_industry_balanced",
    "select_usd_modeled_execution_price",
    "series_sha256",
    "settle_execution_fills",
    "sha256_file",
    "sharpe_standard_error",
    "simulate_staggered_cohort_execution",
    "strategy_failure_probability",
    "strategy_from_config",
    "summarize_leg_attribution",
    "summarize_outcome_distribution",
    "summarize_period_returns",
    "summarize_staggered_execution",
    "summarize_strategy_risk",
    "target_turnover",
    "turnover_from_trade_weights",
    "validate_backtest_periods_frame",
    "validate_backtest_return_frame",
    "validate_execution_aware_bundle_inputs",
    "validate_positions_by_rebalance_frame",
    "validate_targets",
    "validate_tradable_flags_frame",
    "write_backtest_bundle",
    "write_positions_by_rebalance_artifact",
    "write_receipt",
]


if TYPE_CHECKING:
    from quant_platform._portfolio.api import backtest_topk as backtest_topk
    from quant_platform._portfolio.api import run_backtest as run_backtest
    from quant_platform._portfolio.backtest_bundle import (
        BACKTEST_BUNDLE_SCHEMA_VERSION as BACKTEST_BUNDLE_SCHEMA_VERSION,
    )
    from quant_platform._portfolio.backtest_bundle import (
        EXECUTION_AWARE_BUNDLE_FILES as EXECUTION_AWARE_BUNDLE_FILES,
    )
    from quant_platform._portfolio.backtest_bundle import (
        BacktestBundleInventoryItem as BacktestBundleInventoryItem,
    )
    from quant_platform._portfolio.backtest_bundle import (
        BacktestBundleManifest as BacktestBundleManifest,
    )
    from quant_platform._portfolio.backtest_bundle import (
        BacktestEvidenceTier as BacktestEvidenceTier,
    )
    from quant_platform._portfolio.backtest_bundle import (
        reconcile_unified_ledger as reconcile_unified_ledger,
    )
    from quant_platform._portfolio.backtest_bundle import (
        validate_execution_aware_bundle_inputs as validate_execution_aware_bundle_inputs,
    )
    from quant_platform._portfolio.backtest_bundle_io import (
        read_backtest_bundle as read_backtest_bundle,
    )
    from quant_platform._portfolio.backtest_bundle_io import (
        write_backtest_bundle as write_backtest_bundle,
    )
    from quant_platform._portfolio.backtest_contracts import (
        BACKTEST_PERIODS_CONTRACT as BACKTEST_PERIODS_CONTRACT,
    )
    from quant_platform._portfolio.backtest_contracts import (
        BACKTEST_RETURN_CONTRACT as BACKTEST_RETURN_CONTRACT,
    )
    from quant_platform._portfolio.backtest_contracts import (
        TRADABLE_FLAGS_CONTRACT as TRADABLE_FLAGS_CONTRACT,
    )
    from quant_platform._portfolio.backtest_contracts import (
        BacktestPeriodsContract as BacktestPeriodsContract,
    )
    from quant_platform._portfolio.backtest_contracts import (
        BacktestReturnSeriesContract as BacktestReturnSeriesContract,
    )
    from quant_platform._portfolio.backtest_contracts import (
        TradableFlagsContract as TradableFlagsContract,
    )
    from quant_platform._portfolio.backtest_contracts import (
        assert_backtest_periods_frame as assert_backtest_periods_frame,
    )
    from quant_platform._portfolio.backtest_contracts import (
        assert_backtest_return_frame as assert_backtest_return_frame,
    )
    from quant_platform._portfolio.backtest_contracts import (
        assert_tradable_flags_frame as assert_tradable_flags_frame,
    )
    from quant_platform._portfolio.backtest_contracts import (
        build_backtest_periods_frame as build_backtest_periods_frame,
    )
    from quant_platform._portfolio.backtest_contracts import (
        build_backtest_return_frame as build_backtest_return_frame,
    )
    from quant_platform._portfolio.backtest_contracts import (
        validate_backtest_periods_frame as validate_backtest_periods_frame,
    )
    from quant_platform._portfolio.backtest_contracts import (
        validate_backtest_return_frame as validate_backtest_return_frame,
    )
    from quant_platform._portfolio.backtest_contracts import (
        validate_tradable_flags_frame as validate_tradable_flags_frame,
    )
    from quant_platform._portfolio.backtest_spec import BacktestSpec as BacktestSpec
    from quant_platform._portfolio.benchmark_comparison import (
        build_comparison_receipt as build_comparison_receipt,
    )
    from quant_platform._portfolio.benchmark_comparison import (
        compare_portfolio_returns as compare_portfolio_returns,
    )
    from quant_platform._portfolio.benchmark_enhancement import (
        PortfolioConstructionVariant as PortfolioConstructionVariant,
    )
    from quant_platform._portfolio.benchmark_enhancement import (
        build_target_weights as build_target_weights,
    )
    from quant_platform._portfolio.bet_sizing import SizingConfig as SizingConfig
    from quant_platform._portfolio.bet_sizing import average_active_bets as average_active_bets
    from quant_platform._portfolio.bet_sizing import build_sized_weights as build_sized_weights
    from quant_platform._portfolio.bet_sizing import build_sizing_receipt as build_sizing_receipt
    from quant_platform._portfolio.bet_sizing import discretize_weights as discretize_weights
    from quant_platform._portfolio.bet_sizing import probability_to_size as probability_to_size
    from quant_platform._portfolio.contracts import (
        POSITIONS_BY_REBALANCE_CONTRACT as POSITIONS_BY_REBALANCE_CONTRACT,
    )
    from quant_platform._portfolio.contracts import GroupCap as GroupCap
    from quant_platform._portfolio.contracts import (
        PositionsByRebalanceFrameContract as PositionsByRebalanceFrameContract,
    )
    from quant_platform._portfolio.contracts import StrategySpec as StrategySpec
    from quant_platform._portfolio.contracts import (
        assert_positions_by_rebalance_frame as assert_positions_by_rebalance_frame,
    )
    from quant_platform._portfolio.contracts import (
        validate_positions_by_rebalance_frame as validate_positions_by_rebalance_frame,
    )
    from quant_platform._portfolio.daily_watch20 import DailyWatch20Config as DailyWatch20Config
    from quant_platform._portfolio.daily_watch20 import DailyWatch20Receipt as DailyWatch20Receipt
    from quant_platform._portfolio.daily_watch20 import DailyWatch20Result as DailyWatch20Result
    from quant_platform._portfolio.daily_watch20 import (
        DailyWatch20SelectionError as DailyWatch20SelectionError,
    )
    from quant_platform._portfolio.daily_watch20 import GuardFactorSpec as GuardFactorSpec
    from quant_platform._portfolio.daily_watch20 import select_daily_watch20 as select_daily_watch20
    from quant_platform._portfolio.daily_watch20_policy import (
        PORTFOLIO_POLICY_SCHEMA as PORTFOLIO_POLICY_SCHEMA,
    )
    from quant_platform._portfolio.daily_watch20_policy import (
        DailyWatch20PortfolioPolicy as DailyWatch20PortfolioPolicy,
    )
    from quant_platform._portfolio.economic_rebalance import (
        EconomicRebalanceResult as EconomicRebalanceResult,
    )
    from quant_platform._portfolio.economic_rebalance import (
        apply_no_trade_band as apply_no_trade_band,
    )
    from quant_platform._portfolio.evidence_receipts import (
        build_portfolio_sizing_receipt as build_portfolio_sizing_receipt,
    )
    from quant_platform._portfolio.evidence_receipts import series_sha256 as series_sha256
    from quant_platform._portfolio.evidence_receipts import sha256_file as sha256_file
    from quant_platform._portfolio.evidence_receipts import write_receipt as write_receipt
    from quant_platform._portfolio.execution import DetailedTradeFeeModel as DetailedTradeFeeModel
    from quant_platform._portfolio.execution import (
        l2_price_tiered_slippage as l2_price_tiered_slippage,
    )
    from quant_platform._portfolio.execution_diagnostics import (
        attribute_delayed_fills as attribute_delayed_fills,
    )
    from quant_platform._portfolio.execution_ledger import (
        settle_execution_fills as settle_execution_fills,
    )
    from quant_platform._portfolio.execution_summary import (
        EXECUTION_SUMMARY_SCHEMA as EXECUTION_SUMMARY_SCHEMA,
    )
    from quant_platform._portfolio.execution_summary import (
        execution_summary_frame as execution_summary_frame,
    )
    from quant_platform._portfolio.execution_summary import (
        summarize_staggered_execution as summarize_staggered_execution,
    )
    from quant_platform._portfolio.hrp import HrpConfig as HrpConfig
    from quant_platform._portfolio.hrp import HrpResult as HrpResult
    from quant_platform._portfolio.hrp import hierarchical_risk_parity as hierarchical_risk_parity
    from quant_platform._portfolio.hrp import rolling_hrp_weights as rolling_hrp_weights
    from quant_platform._portfolio.incumbent_requalification import (
        INCUMBENT_REQUALIFICATION_SCHEMA as INCUMBENT_REQUALIFICATION_SCHEMA,
    )
    from quant_platform._portfolio.incumbent_requalification import (
        IncumbentRequalificationConfig as IncumbentRequalificationConfig,
    )
    from quant_platform._portfolio.incumbent_requalification import (
        IncumbentRequalificationPolicy as IncumbentRequalificationPolicy,
    )
    from quant_platform._portfolio.incumbent_requalification import (
        IncumbentRequalificationReceipt as IncumbentRequalificationReceipt,
    )
    from quant_platform._portfolio.incumbent_requalification import (
        IncumbentRequalificationResult as IncumbentRequalificationResult,
    )
    from quant_platform._portfolio.incumbent_requalification import (
        select_incumbent_requalified_portfolio as select_incumbent_requalified_portfolio,
    )
    from quant_platform._portfolio.industry_sleeves import SelectionSpec as SelectionSpec
    from quant_platform._portfolio.industry_sleeves import attach_entry_dates as attach_entry_dates
    from quant_platform._portfolio.industry_sleeves import build_targets as build_targets
    from quant_platform._portfolio.industry_sleeves import combine_targets as combine_targets
    from quant_platform._portfolio.industry_sleeves import (
        select_industry_balanced as select_industry_balanced,
    )
    from quant_platform._portfolio.industry_sleeves import target_turnover as target_turnover
    from quant_platform._portfolio.industry_sleeves import validate_targets as validate_targets
    from quant_platform._portfolio.metrics import leg_attribution_frame as leg_attribution_frame
    from quant_platform._portfolio.metrics import (
        summarize_leg_attribution as summarize_leg_attribution,
    )
    from quant_platform._portfolio.metrics import (
        summarize_period_returns as summarize_period_returns,
    )
    from quant_platform._portfolio.optimization import (
        PORTFOLIO_OPTIMIZATION_RESULT_SCHEMA as PORTFOLIO_OPTIMIZATION_RESULT_SCHEMA,
    )
    from quant_platform._portfolio.optimization import (
        EqualWeightOptimizerBackend as EqualWeightOptimizerBackend,
    )
    from quant_platform._portfolio.optimization import HrpOptimizerBackend as HrpOptimizerBackend
    from quant_platform._portfolio.optimization import InverseVolConfig as InverseVolConfig
    from quant_platform._portfolio.optimization import (
        InverseVolOptimizerBackend as InverseVolOptimizerBackend,
    )
    from quant_platform._portfolio.optimization import (
        LinearExposureConstraint as LinearExposureConstraint,
    )
    from quant_platform._portfolio.optimization import OptimizerRegistry as OptimizerRegistry
    from quant_platform._portfolio.optimization import (
        PortfolioOptimizationRequest as PortfolioOptimizationRequest,
    )
    from quant_platform._portfolio.optimization import (
        PortfolioOptimizationResult as PortfolioOptimizationResult,
    )
    from quant_platform._portfolio.optimization import (
        PortfolioOptimizerBackend as PortfolioOptimizerBackend,
    )
    from quant_platform._portfolio.optimization import PortfolioQpConfig as PortfolioQpConfig
    from quant_platform._portfolio.optimization import (
        QpMinVarianceOptimizerBackend as QpMinVarianceOptimizerBackend,
    )
    from quant_platform._portfolio.outcome_metrics import (
        OutcomeDistributionReport as OutcomeDistributionReport,
    )
    from quant_platform._portfolio.outcome_metrics import (
        summarize_outcome_distribution as summarize_outcome_distribution,
    )
    from quant_platform._portfolio.position_backtest import (
        PositionBacktestConfig as PositionBacktestConfig,
    )
    from quant_platform._portfolio.position_backtest import (
        PositionBacktestResult as PositionBacktestResult,
    )
    from quant_platform._portfolio.position_backtest import (
        run_position_backtest as run_position_backtest,
    )
    from quant_platform._portfolio.position_evaluation import (
        PositionBacktestEvaluation as PositionBacktestEvaluation,
    )
    from quant_platform._portfolio.position_evaluation import (
        evaluate_position_backtest as evaluate_position_backtest,
    )
    from quant_platform._portfolio.position_inputs import (
        positions_by_rebalance_from_targets as positions_by_rebalance_from_targets,
    )
    from quant_platform._portfolio.position_replay import (
        build_position_replay_periods as build_position_replay_periods,
    )
    from quant_platform._portfolio.position_replay import (
        run_native_position_replay as run_native_position_replay,
    )
    from quant_platform._portfolio.positions_artifact import (
        CANONICAL_POSITIONS_BY_REBALANCE_META_FILE as CANONICAL_POSITIONS_BY_REBALANCE_META_FILE,
    )
    from quant_platform._portfolio.positions_artifact import (
        build_positions_envelope_v2 as build_positions_envelope_v2,
    )
    from quant_platform._portfolio.positions_artifact import (
        write_positions_by_rebalance_artifact as write_positions_by_rebalance_artifact,
    )
    from quant_platform._portfolio.rebalance import (
        SessionRebalanceSchedule as SessionRebalanceSchedule,
    )
    from quant_platform._portfolio.rebalance import get_rebalance_events as get_rebalance_events
    from quant_platform._portfolio.rebalance import (
        get_session_interval_rebalance_dates as get_session_interval_rebalance_dates,
    )
    from quant_platform._portfolio.robust_uncertainty import (
        add_conservative_score as add_conservative_score,
    )
    from quant_platform._portfolio.robust_uncertainty import (
        box_worst_case_return as box_worst_case_return,
    )
    from quant_platform._portfolio.robust_uncertainty import (
        conservative_score as conservative_score,
    )
    from quant_platform._portfolio.sharpe_inference import (
        annualized_sharpe_to_periodic as annualized_sharpe_to_periodic,
    )
    from quant_platform._portfolio.sharpe_inference import (
        annualized_variance_to_periodic as annualized_variance_to_periodic,
    )
    from quant_platform._portfolio.sharpe_inference import (
        deflated_sharpe_ratio as deflated_sharpe_ratio,
    )
    from quant_platform._portfolio.sharpe_inference import (
        expected_max_sharpe as expected_max_sharpe,
    )
    from quant_platform._portfolio.sharpe_inference import (
        probabilistic_sharpe_ratio as probabilistic_sharpe_ratio_from_stats,
    )
    from quant_platform._portfolio.sharpe_inference import (
        sharpe_standard_error as sharpe_standard_error,
    )
    from quant_platform._portfolio.staggered_cohort_execution import (
        StaggeredCohortExecutionConfig as StaggeredCohortExecutionConfig,
    )
    from quant_platform._portfolio.staggered_cohort_execution import (
        StaggeredCohortExecutionResult as StaggeredCohortExecutionResult,
    )
    from quant_platform._portfolio.staggered_cohort_execution import (
        simulate_staggered_cohort_execution as simulate_staggered_cohort_execution,
    )
    from quant_platform._portfolio.strategy import (
        construct_positions_from_strategy as construct_positions_from_strategy,
    )
    from quant_platform._portfolio.strategy import strategy_from_config as strategy_from_config
    from quant_platform._portfolio.strategy_risk import StrategyRiskReport as StrategyRiskReport
    from quant_platform._portfolio.strategy_risk import (
        implementation_shortfall_metrics as implementation_shortfall_metrics,
    )
    from quant_platform._portfolio.strategy_risk import (
        probabilistic_sharpe_ratio as probabilistic_sharpe_ratio,
    )
    from quant_platform._portfolio.strategy_risk import return_concentration as return_concentration
    from quant_platform._portfolio.strategy_risk import (
        strategy_failure_probability as strategy_failure_probability,
    )
    from quant_platform._portfolio.strategy_risk import (
        summarize_strategy_risk as summarize_strategy_risk,
    )
    from quant_platform._portfolio.tca_calibration import (
        TCACalibrationReceipt as TCACalibrationReceipt,
    )
    from quant_platform._portfolio.tca_calibration import (
        calibrate_cost_model as calibrate_cost_model,
    )
    from quant_platform._portfolio.trade_accounting import (
        compute_trade_summary as compute_trade_summary,
    )
    from quant_platform._portfolio.trade_accounting import (
        drift_previous_weights as drift_previous_weights,
    )
    from quant_platform._portfolio.turnover import (
        RebalanceTurnoverReport as RebalanceTurnoverReport,
    )
    from quant_platform._portfolio.turnover import TurnoverBreakdown as TurnoverBreakdown
    from quant_platform._portfolio.turnover import annualize_turnover as annualize_turnover
    from quant_platform._portfolio.turnover import (
        build_rebalance_turnover_report as build_rebalance_turnover_report,
    )
    from quant_platform._portfolio.turnover import name_turnover as name_turnover
    from quant_platform._portfolio.turnover import (
        turnover_from_trade_weights as turnover_from_trade_weights,
    )
    from quant_platform._portfolio.types import CostBreakdown as CostBreakdown
    from quant_platform._portfolio.usd_ledger_inputs import (
        select_usd_modeled_execution_price as select_usd_modeled_execution_price,
    )
    from quant_platform._portfolio.usd_ledger_models import (
        USDModeledExecutionPrice as USDModeledExecutionPrice,
    )


def __getattr__(name):
    if name not in _EXPORTS:
        raise AttributeError(name)
    module, symbol = _EXPORTS[name]
    value = getattr(import_module(module), symbol)
    globals()[name] = value
    return value
