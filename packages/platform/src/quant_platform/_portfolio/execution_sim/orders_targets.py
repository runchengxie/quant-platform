"""Engine alias: quant_backtest_core.daily.execution_sim.orders_targets."""

from __future__ import annotations

import sys
from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from quant_backtest_core.daily.execution_sim.orders_targets import Any as Any
    from quant_backtest_core.daily.execution_sim.orders_targets import (
        DetailedTradeFeeModel as DetailedTradeFeeModel,
    )
    from quant_backtest_core.daily.execution_sim.orders_targets import Mapping as Mapping
    from quant_backtest_core.daily.execution_sim.orders_targets import (
        TradeFeeModel as TradeFeeModel,
    )
    from quant_backtest_core.daily.execution_sim.orders_targets import (
        _build_targets_by_rebalance as _build_targets_by_rebalance,
    )
    from quant_backtest_core.daily.execution_sim.orders_targets import (
        _cash_weight_breakdown as _cash_weight_breakdown,
    )
    from quant_backtest_core.daily.execution_sim.orders_targets import (
        _cost_adjusted_target_notional as _cost_adjusted_target_notional,
    )
    from quant_backtest_core.daily.execution_sim.orders_targets import (
        _target_cash_notional as _target_cash_notional,
    )
    from quant_backtest_core.daily.execution_sim.orders_targets import cast as cast
    from quant_backtest_core.daily.execution_sim.orders_targets import np as np
    from quant_backtest_core.daily.execution_sim.orders_targets import pd as pd

sys.modules[__name__] = import_module("quant_backtest_core.daily.execution_sim.orders_targets")
