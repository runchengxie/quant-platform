"""Compatibility package; implementation and public owners are recorded in the module map."""

from importlib import import_module

__all__ = [  # noqa: RUF022 - preserve historical star-import ordering
    "CorporateAction",
    "SELL_UNTIL_NEXT_REBALANCE",
    "ExecutionAdjustedNavResult",
    "ExecutionSimConfig",
    "ExecutionSimResult",
    "PreparedExecutionTables",
    "TradeFeeModel",
    "UnifiedLedger",
    "audit_delisting_exits",
    "build_execution_sim_config",
    "describe_execution_sim_config",
    "describe_trade_fee_model",
    "prepare_execution_tables",
    "required_execution_sim_columns",
    "simulate_capacity_execution",
    "simulate_execution_adjusted_nav",
    "simulate_ideal_daily_nav",
    "to_unified_ledger",
]


def __getattr__(name):
    return getattr(import_module("quant_platform._portfolio.execution_sim"), name)
