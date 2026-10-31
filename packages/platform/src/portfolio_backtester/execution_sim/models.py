"""Module alias preserving implementation identity during compatibility migration."""

import sys
from importlib import import_module
from typing import TYPE_CHECKING

__all__ = [
    "Any",
    "CostBreakdown",
    "DatedFeeQuote",
    "DatedTradeFeeModel",
    "DetailedTradeFeeModel",
    "ExecutionSimConfig",
    "FeeQuoteContext",
    "PreparedExecutionTables",
    "SlippageModel",
    "SupportedTradeFeeModel",
    "TradeFeeModel",
    "_AdjustedNavLedger",
    "_AdjustedNavPlan",
    "_CorporateActionLedger",
    "_ExecutionTables",
    "_MarketRules",
    "_NavOrder",
    "_OrderSink",
    "_TradeFeeQuote",
    "_add_breakdown",
    "_quote_trade_fee",
    "_trade_fee",
    "_with_dated_fee_context",
    "annotations",
    "dataclass",
    "date",
    "describe_trade_fee_model",
]

if TYPE_CHECKING:
    from quant_platform._portfolio.execution_sim.models import (
        Any,
        CostBreakdown,
        DatedFeeQuote,
        DatedTradeFeeModel,
        DetailedTradeFeeModel,
        ExecutionSimConfig,
        FeeQuoteContext,
        PreparedExecutionTables,
        SlippageModel,
        SupportedTradeFeeModel,
        TradeFeeModel,
        _add_breakdown,
        _AdjustedNavLedger,
        _AdjustedNavPlan,
        _CorporateActionLedger,
        _ExecutionTables,
        _MarketRules,
        _NavOrder,
        _OrderSink,
        _quote_trade_fee,
        _trade_fee,
        _TradeFeeQuote,
        _with_dated_fee_context,
        annotations,
        dataclass,
        date,
        describe_trade_fee_model,
    )

sys.modules[__name__] = import_module("quant_platform._portfolio.execution_sim.models")
