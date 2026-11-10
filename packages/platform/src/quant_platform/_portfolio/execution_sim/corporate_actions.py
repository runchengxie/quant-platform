"""Engine alias: quant_backtest_core.daily.execution_sim.corporate_actions."""

from __future__ import annotations

import sys
from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from quant_backtest_core.daily.execution_sim.corporate_actions import (
        ACTION_COLUMNS as ACTION_COLUMNS,
    )
    from quant_backtest_core.daily.execution_sim.corporate_actions import (
        HOLDING_COLUMNS as HOLDING_COLUMNS,
    )
    from quant_backtest_core.daily.execution_sim.corporate_actions import (
        RECEIVABLE_COLUMNS as RECEIVABLE_COLUMNS,
    )
    from quant_backtest_core.daily.execution_sim.corporate_actions import (
        TYPE_CHECKING as TYPE_CHECKING,
    )
    from quant_backtest_core.daily.execution_sim.corporate_actions import Any as Any
    from quant_backtest_core.daily.execution_sim.corporate_actions import (
        CorporateAction as CorporateAction,
    )
    from quant_backtest_core.daily.execution_sim.corporate_actions import (
        _action_conventions as _action_conventions,
    )
    from quant_backtest_core.daily.execution_sim.corporate_actions import (
        _CorporateActionLedger as _CorporateActionLedger,
    )
    from quant_backtest_core.daily.execution_sim.corporate_actions import _price_at as _price_at
    from quant_backtest_core.daily.execution_sim.corporate_actions import _Right as _Right
    from quant_backtest_core.daily.execution_sim.corporate_actions import (
        _valuation_price as _valuation_price,
    )
    from quant_backtest_core.daily.execution_sim.corporate_actions import dataclass as dataclass
    from quant_backtest_core.daily.execution_sim.corporate_actions import field as field
    from quant_backtest_core.daily.execution_sim.corporate_actions import np as np
    from quant_backtest_core.daily.execution_sim.corporate_actions import pd as pd

sys.modules[__name__] = import_module("quant_backtest_core.daily.execution_sim.corporate_actions")
