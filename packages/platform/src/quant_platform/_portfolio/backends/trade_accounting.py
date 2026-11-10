"""Compatibility alias for Core's backend trade-accounting financial API."""

from __future__ import annotations

import sys
from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from quant_backtest_core.daily.trade_accounting import (
        Mapping as Mapping,
    )
    from quant_backtest_core.daily.trade_accounting import (
        TradeAccounting as TradeAccounting,
    )
    from quant_backtest_core.daily.trade_accounting import (
        TradeCostConfig as TradeCostConfig,
    )
    from quant_backtest_core.daily.trade_accounting import (
        _clean_weights as _clean_weights,
    )
    from quant_backtest_core.daily.trade_accounting import (
        compute_trade_accounting as compute_trade_accounting,
    )
    from quant_backtest_core.daily.trade_accounting import (
        compute_trade_accounting_frame as compute_trade_accounting_frame,
    )
    from quant_backtest_core.daily.trade_accounting import (
        dataclass as dataclass,
    )
    from quant_backtest_core.daily.trade_accounting import (
        drift_weights as drift_weights,
    )
    from quant_backtest_core.daily.trade_accounting import (
        np as np,
    )
    from quant_backtest_core.daily.trade_accounting import (
        pd as pd,
    )

sys.modules[__name__] = import_module("quant_backtest_core.daily.trade_accounting")
