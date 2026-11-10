"""Engine alias: quant_backtest_core.daily.execution_sim.capacity."""

from __future__ import annotations

import sys
from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from quant_backtest_core.daily.execution_sim.capacity import (
        SELL_UNTIL_NEXT_REBALANCE as SELL_UNTIL_NEXT_REBALANCE,
    )
    from quant_backtest_core.daily.execution_sim.capacity import (
        DetailedTradeFeeModel as DetailedTradeFeeModel,
    )
    from quant_backtest_core.daily.execution_sim.capacity import (
        ExecutionSimConfig as ExecutionSimConfig,
    )
    from quant_backtest_core.daily.execution_sim.capacity import TradeFeeModel as TradeFeeModel
    from quant_backtest_core.daily.execution_sim.capacity import (
        _capacity_notional as _capacity_notional,
    )
    from quant_backtest_core.daily.execution_sim.capacity import (
        _capacity_weight as _capacity_weight,
    )
    from quant_backtest_core.daily.execution_sim.capacity import (
        _execution_window_dates as _execution_window_dates,
    )
    from quant_backtest_core.daily.execution_sim.capacity import _limit_down_at as _limit_down_at
    from quant_backtest_core.daily.execution_sim.capacity import _limit_up_at as _limit_up_at
    from quant_backtest_core.daily.execution_sim.capacity import (
        _listing_status_at as _listing_status_at,
    )
    from quant_backtest_core.daily.execution_sim.capacity import (
        _position_values_by_symbol as _position_values_by_symbol,
    )
    from quant_backtest_core.daily.execution_sim.capacity import (
        _positions_value as _positions_value,
    )
    from quant_backtest_core.daily.execution_sim.capacity import _price_at as _price_at
    from quant_backtest_core.daily.execution_sim.capacity import (
        _refresh_last_prices as _refresh_last_prices,
    )
    from quant_backtest_core.daily.execution_sim.capacity import _table_bool_at as _table_bool_at
    from quant_backtest_core.daily.execution_sim.capacity import _table_float_at as _table_float_at
    from quant_backtest_core.daily.execution_sim.capacity import (
        _valuation_price as _valuation_price,
    )
    from quant_backtest_core.daily.execution_sim.capacity import np as np
    from quant_backtest_core.daily.execution_sim.capacity import pd as pd

sys.modules[__name__] = import_module("quant_backtest_core.daily.execution_sim.capacity")
