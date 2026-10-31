"""Module alias preserving implementation identity during compatibility migration."""

import sys
from importlib import import_module
from typing import TYPE_CHECKING

__all__ = [
    "MARKET_CALENDAR",
    "BpsCostModel",
    "BpsSlippageModel",
    "CostModel",
    "DetailedTradeFeeModel",
    "EntryPolicy",
    "ExecutionModel",
    "ExitFallbackPolicy",
    "ExitPolicy",
    "ExitPricePolicy",
    "Literal",
    "NoCostModel",
    "NoSlippageModel",
    "ParticipationSlippageModel",
    "Protocol",
    "SelectionConstraints",
    "SideBpsCostModel",
    "SlippageModel",
    "annotations",
    "dataclass",
]

if TYPE_CHECKING:
    from quant_platform._portfolio._execution_models import (
        MARKET_CALENDAR,
        BpsCostModel,
        BpsSlippageModel,
        CostModel,
        DetailedTradeFeeModel,
        EntryPolicy,
        ExecutionModel,
        ExitFallbackPolicy,
        ExitPolicy,
        ExitPricePolicy,
        Literal,
        NoCostModel,
        NoSlippageModel,
        ParticipationSlippageModel,
        Protocol,
        SelectionConstraints,
        SideBpsCostModel,
        SlippageModel,
        annotations,
        dataclass,
    )

sys.modules[__name__] = import_module("quant_platform._portfolio._execution_models")
