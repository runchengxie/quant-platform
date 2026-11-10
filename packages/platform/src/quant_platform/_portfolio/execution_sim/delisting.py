"""Engine alias: quant_backtest_core.daily.execution_sim.delisting."""

from __future__ import annotations

import sys
from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from quant_backtest_core.daily.execution_sim.delisting import Mapping as Mapping
    from quant_backtest_core.daily.execution_sim.delisting import (
        _quantity_trades as _quantity_trades,
    )
    from quant_backtest_core.daily.execution_sim.delisting import (
        audit_delisting_exits as audit_delisting_exits,
    )
    from quant_backtest_core.daily.execution_sim.delisting import pd as pd

sys.modules[__name__] = import_module("quant_backtest_core.daily.execution_sim.delisting")
