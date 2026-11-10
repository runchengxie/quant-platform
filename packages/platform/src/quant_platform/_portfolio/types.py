from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field as field

import pandas as pd
from quant_backtest_core.daily.types import BacktestLegResult as BacktestLegResult
from quant_backtest_core.daily.types import BacktestPeriodResult as BacktestPeriodResult
from quant_backtest_core.daily.types import BacktestPositionState as BacktestPositionState
from quant_backtest_core.daily.types import CostBreakdown as CostBreakdown

from .execution import CostModel, EntryPolicy, ExitPolicy, SelectionConstraints, SlippageModel
from .turnover import TurnoverBreakdown as TurnoverBreakdown


@dataclass(frozen=True)
class BacktestExecutionContext:
    exit_policy: ExitPolicy
    cost_model: CostModel
    slippage_model: SlippageModel
    entry_policy: EntryPolicy
    selection_constraints: SelectionConstraints
    calendar: str
    open_dates: tuple
    closed_dates: tuple


@dataclass(frozen=True)
class BacktestPricingContext:
    trade_dates: list[pd.Timestamp]
    date_to_idx: dict[pd.Timestamp, int]
    entry_price_table: pd.DataFrame
    exit_price_table: pd.DataFrame
    day_groups: dict[pd.Timestamp, pd.DataFrame]
    tradable_table: pd.DataFrame | None
    amount_tables: dict[str, pd.DataFrame]


@dataclass(frozen=True)
class BacktestPeriodPlan:
    entry_idx: int
    planned_exit_idx: int
    entry_date: pd.Timestamp
    planned_exit_date: pd.Timestamp
