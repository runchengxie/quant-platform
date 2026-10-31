"""Module alias preserving implementation identity during compatibility migration."""

import sys
from importlib import import_module
from typing import TYPE_CHECKING

__all__ = [
    "SELL_UNTIL_NEXT_REBALANCE",
    "DetailedTradeFeeModel",
    "ExecutionSimConfig",
    "TradeFeeModel",
    "_capacity_notional",
    "_capacity_weight",
    "_execution_window_dates",
    "_limit_down_at",
    "_limit_up_at",
    "_listing_status_at",
    "_position_values_by_symbol",
    "_positions_value",
    "_price_at",
    "_refresh_last_prices",
    "_table_bool_at",
    "_table_float_at",
    "_valuation_price",
    "annotations",
]

if TYPE_CHECKING:
    from quant_platform._portfolio.execution_sim.capacity import (
        SELL_UNTIL_NEXT_REBALANCE,
        DetailedTradeFeeModel,
        ExecutionSimConfig,
        TradeFeeModel,
        _capacity_notional,
        _capacity_weight,
        _execution_window_dates,
        _limit_down_at,
        _limit_up_at,
        _listing_status_at,
        _position_values_by_symbol,
        _positions_value,
        _price_at,
        _refresh_last_prices,
        _table_bool_at,
        _table_float_at,
        _valuation_price,
        annotations,
    )

sys.modules[__name__] = import_module("quant_platform._portfolio.execution_sim.capacity")
