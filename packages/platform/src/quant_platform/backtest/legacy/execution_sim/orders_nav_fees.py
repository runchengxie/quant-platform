"""Module alias preserving implementation identity during compatibility migration."""

import sys
from importlib import import_module
from typing import TYPE_CHECKING

__all__ = [
    "DatedTradeFeeModel",
    "ExecutionSimConfig",
    "FeeQuoteContext",
    "SlippageModel",
    "SupportedTradeFeeModel",
    "TradeFeeModel",
    "_ExecutionTables",
    "_NavOrder",
    "_TradeFeeQuote",
    "_accrue_nav_fee_quote",
    "_nav_fee_group_id",
    "_nav_fee_order_id",
    "_nav_trade_fee",
    "_quote_trade_fee",
    "_slippage_pricing_row",
    "annotations",
]

if TYPE_CHECKING:
    from quant_platform._portfolio.execution_sim.orders_nav_fees import (
        DatedTradeFeeModel,
        ExecutionSimConfig,
        FeeQuoteContext,
        SlippageModel,
        SupportedTradeFeeModel,
        TradeFeeModel,
        _accrue_nav_fee_quote,
        _ExecutionTables,
        _nav_fee_group_id,
        _nav_fee_order_id,
        _nav_trade_fee,
        _NavOrder,
        _quote_trade_fee,
        _slippage_pricing_row,
        _TradeFeeQuote,
        annotations,
    )

sys.modules[__name__] = import_module("quant_platform._portfolio.execution_sim.orders_nav_fees")
