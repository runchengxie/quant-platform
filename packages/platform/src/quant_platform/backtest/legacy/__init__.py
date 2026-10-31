"""Lazy public exports; importing a module does not load unrelated simulators."""

from importlib import import_module
from typing import TYPE_CHECKING

__all__ = [
    "BACKTEST_BUNDLE_SCHEMA_VERSION",
    "BACKTEST_PERIODS_CONTRACT",
    "BACKTEST_RETURN_CONTRACT",
    "CANONICAL_POSITIONS_BY_REBALANCE_META_FILE",
    "EXECUTION_AWARE_BUNDLE_FILES",
    "INCUMBENT_REQUALIFICATION_SCHEMA",
    "PORTFOLIO_POLICY_SCHEMA",
    "TRADABLE_FLAGS_CONTRACT",
    "BacktestBundleInventoryItem",
    "BacktestBundleManifest",
    "BacktestEvidenceTier",
    "BacktestPeriodsContract",
    "BacktestReturnSeriesContract",
    "BacktestSpec",
    "DailyWatch20Config",
    "DailyWatch20PortfolioPolicy",
    "DailyWatch20Receipt",
    "DailyWatch20Result",
    "DailyWatch20SelectionError",
    "DetailedTradeFeeModel",
    "GuardFactorSpec",
    "IncumbentRequalificationConfig",
    "IncumbentRequalificationPolicy",
    "IncumbentRequalificationReceipt",
    "IncumbentRequalificationResult",
    "OutcomeDistributionReport",
    "PortfolioConstructionVariant",
    "PositionBacktestConfig",
    "PositionBacktestResult",
    "SelectionSpec",
    "StaggeredCohortExecutionConfig",
    "StaggeredCohortExecutionResult",
    "TradableFlagsContract",
    "USDModeledExecutionPrice",
    "add_conservative_score",
    "assert_backtest_periods_frame",
    "assert_backtest_return_frame",
    "assert_tradable_flags_frame",
    "attach_entry_dates",
    "backtest_topk",
    "box_worst_case_return",
    "build_backtest_periods_frame",
    "build_backtest_return_frame",
    "build_portfolio_sizing_receipt",
    "build_position_replay_periods",
    "build_positions_envelope_v2",
    "build_target_weights",
    "build_targets",
    "combine_targets",
    "compute_trade_summary",
    "conservative_score",
    "drift_previous_weights",
    "l2_price_tiered_slippage",
    "positions_by_rebalance_from_targets",
    "read_backtest_bundle",
    "reconcile_unified_ledger",
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
    "simulate_staggered_cohort_execution",
    "summarize_outcome_distribution",
    "target_turnover",
    "validate_backtest_periods_frame",
    "validate_backtest_return_frame",
    "validate_execution_aware_bundle_inputs",
    "validate_targets",
    "validate_tradable_flags_frame",
    "write_backtest_bundle",
    "write_positions_by_rebalance_artifact",
    "write_receipt",
]

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
    "INCUMBENT_REQUALIFICATION_SCHEMA": (
        "quant_platform._portfolio.incumbent_requalification",
        "INCUMBENT_REQUALIFICATION_SCHEMA",
    ),
    "PORTFOLIO_POLICY_SCHEMA": (
        "quant_platform._portfolio.daily_watch20_policy",
        "PORTFOLIO_POLICY_SCHEMA",
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
    "GuardFactorSpec": ("quant_platform._portfolio.daily_watch20", "GuardFactorSpec"),
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
    "OutcomeDistributionReport": (
        "quant_platform._portfolio.outcome_metrics",
        "OutcomeDistributionReport",
    ),
    "PortfolioConstructionVariant": (
        "quant_platform._portfolio.benchmark_enhancement",
        "PortfolioConstructionVariant",
    ),
    "PositionBacktestConfig": (
        "quant_platform._portfolio.position_backtest",
        "PositionBacktestConfig",
    ),
    "PositionBacktestResult": (
        "quant_platform._portfolio.position_backtest",
        "PositionBacktestResult",
    ),
    "SelectionSpec": ("quant_platform._portfolio.industry_sleeves", "SelectionSpec"),
    "StaggeredCohortExecutionConfig": (
        "quant_platform._portfolio.staggered_cohort_execution",
        "StaggeredCohortExecutionConfig",
    ),
    "StaggeredCohortExecutionResult": (
        "quant_platform._portfolio.staggered_cohort_execution",
        "StaggeredCohortExecutionResult",
    ),
    "TradableFlagsContract": (
        "quant_platform._portfolio.backtest_contracts",
        "TradableFlagsContract",
    ),
    "USDModeledExecutionPrice": (
        "quant_platform._portfolio.usd_ledger_models",
        "USDModeledExecutionPrice",
    ),
    "add_conservative_score": (
        "quant_platform._portfolio.robust_uncertainty",
        "add_conservative_score",
    ),
    "assert_backtest_periods_frame": (
        "quant_platform._portfolio.backtest_contracts",
        "assert_backtest_periods_frame",
    ),
    "assert_backtest_return_frame": (
        "quant_platform._portfolio.backtest_contracts",
        "assert_backtest_return_frame",
    ),
    "assert_tradable_flags_frame": (
        "quant_platform._portfolio.backtest_contracts",
        "assert_tradable_flags_frame",
    ),
    "attach_entry_dates": ("quant_platform._portfolio.industry_sleeves", "attach_entry_dates"),
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
    "build_target_weights": (
        "quant_platform._portfolio.benchmark_enhancement",
        "build_target_weights",
    ),
    "build_targets": ("quant_platform._portfolio.industry_sleeves", "build_targets"),
    "combine_targets": ("quant_platform._portfolio.industry_sleeves", "combine_targets"),
    "compute_trade_summary": (
        "quant_platform._portfolio.trade_accounting",
        "compute_trade_summary",
    ),
    "conservative_score": ("quant_platform._portfolio.robust_uncertainty", "conservative_score"),
    "drift_previous_weights": (
        "quant_platform._portfolio.trade_accounting",
        "drift_previous_weights",
    ),
    "l2_price_tiered_slippage": ("quant_platform._portfolio.execution", "l2_price_tiered_slippage"),
    "positions_by_rebalance_from_targets": (
        "quant_platform._portfolio.position_inputs",
        "positions_by_rebalance_from_targets",
    ),
    "read_backtest_bundle": (
        "quant_platform._portfolio.backtest_bundle_io",
        "read_backtest_bundle",
    ),
    "reconcile_unified_ledger": (
        "quant_platform._portfolio.backtest_bundle",
        "reconcile_unified_ledger",
    ),
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
    "simulate_staggered_cohort_execution": (
        "quant_platform._portfolio.staggered_cohort_execution",
        "simulate_staggered_cohort_execution",
    ),
    "summarize_outcome_distribution": (
        "quant_platform._portfolio.outcome_metrics",
        "summarize_outcome_distribution",
    ),
    "target_turnover": ("quant_platform._portfolio.industry_sleeves", "target_turnover"),
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
    from quant_platform._portfolio.benchmark_enhancement import (
        PortfolioConstructionVariant as PortfolioConstructionVariant,
    )
    from quant_platform._portfolio.benchmark_enhancement import (
        build_target_weights as build_target_weights,
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
    from quant_platform._portfolio.execution_ledger import (
        settle_execution_fills as settle_execution_fills,
    )
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
    from quant_platform._portfolio.robust_uncertainty import (
        add_conservative_score as add_conservative_score,
    )
    from quant_platform._portfolio.robust_uncertainty import (
        box_worst_case_return as box_worst_case_return,
    )
    from quant_platform._portfolio.robust_uncertainty import (
        conservative_score as conservative_score,
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
    from quant_platform._portfolio.trade_accounting import (
        compute_trade_summary as compute_trade_summary,
    )
    from quant_platform._portfolio.trade_accounting import (
        drift_previous_weights as drift_previous_weights,
    )
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
