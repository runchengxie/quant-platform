"""Module alias preserving implementation identity during compatibility migration."""

import sys
from importlib import import_module
from typing import TYPE_CHECKING

__all__ = [
    "ACTION_COLUMNS",
    "HOLDING_COLUMNS",
    "RECEIVABLE_COLUMNS",
    "TYPE_CHECKING",
    "Any",
    "CorporateAction",
    "_CorporateActionLedger",
    "_Right",
    "_action_conventions",
    "_price_at",
    "_valuation_price",
    "annotations",
    "dataclass",
    "field",
]

if TYPE_CHECKING:
    from quant_platform._portfolio.execution_sim.corporate_actions import (
        ACTION_COLUMNS,
        HOLDING_COLUMNS,
        RECEIVABLE_COLUMNS,
        TYPE_CHECKING,
        Any,
        CorporateAction,
        _action_conventions,
        _CorporateActionLedger,
        _price_at,
        _Right,
        _valuation_price,
        annotations,
        dataclass,
        field,
    )

sys.modules[__name__] = import_module("quant_platform._portfolio.execution_sim.corporate_actions")
