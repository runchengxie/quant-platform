"""Execution simulation public surface."""

from __future__ import annotations

from ..corporate_actions import CorporateAction as CorporateAction
from .config import (
    SELL_UNTIL_NEXT_REBALANCE as SELL_UNTIL_NEXT_REBALANCE,
)
from .config import (
    ExecutionSimConfig as ExecutionSimConfig,
)
from .config import (
    build_execution_sim_config as build_execution_sim_config,
)
from .config import (
    describe_execution_sim_config as describe_execution_sim_config,
)
from .config import (
    required_execution_sim_columns as required_execution_sim_columns,
)
from .core import (
    prepare_execution_tables as prepare_execution_tables,
)
from .core import (
    simulate_capacity_execution as simulate_capacity_execution,
)
from .core import (
    simulate_execution_adjusted_nav as simulate_execution_adjusted_nav,
)
from .core import (
    simulate_ideal_daily_nav as simulate_ideal_daily_nav,
)
from .models import (
    PreparedExecutionTables as PreparedExecutionTables,
)
from .models import (
    TradeFeeModel as TradeFeeModel,
)
from .models import (
    describe_trade_fee_model as describe_trade_fee_model,
)
from .results import (
    ExecutionAdjustedNavResult as ExecutionAdjustedNavResult,
)
from .results import (
    ExecutionSimResult as ExecutionSimResult,
)
from .results import (
    UnifiedLedger as UnifiedLedger,
)
from .results import (
    to_unified_ledger as to_unified_ledger,
)

__all__ = [  # noqa: RUF022 - order is a compatibility contract
    "CorporateAction",
    "SELL_UNTIL_NEXT_REBALANCE",
    "ExecutionAdjustedNavResult",
    "ExecutionSimConfig",
    "ExecutionSimResult",
    "PreparedExecutionTables",
    "TradeFeeModel",
    "UnifiedLedger",
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
