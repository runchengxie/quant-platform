"""Module alias preserving implementation identity during compatibility migration."""

import sys
from importlib import import_module
from typing import TYPE_CHECKING

__all__ = [
    "Mapping",
    "TradeAccounting",
    "TradeCostConfig",
    "_clean_weights",
    "annotations",
    "compute_trade_accounting",
    "compute_trade_accounting_frame",
    "dataclass",
    "drift_weights",
]

if TYPE_CHECKING:
    from quant_platform._portfolio.backends.trade_accounting import (
        Mapping,
        TradeAccounting,
        TradeCostConfig,
        _clean_weights,
        annotations,
        compute_trade_accounting,
        compute_trade_accounting_frame,
        dataclass,
        drift_weights,
    )

sys.modules[__name__] = import_module("quant_platform._portfolio.backends.trade_accounting")
