"""Module alias preserving implementation identity during compatibility migration."""

import sys
from importlib import import_module
from typing import TYPE_CHECKING

__all__ = [
    "Any",
    "_normalize_settlement_inputs",
    "_settle_all_dates",
    "_settle_buy_fill",
    "_settle_date",
    "_settle_day_fills",
    "_settle_sell_fill",
    "_validate_settlement_inputs",
    "annotations",
    "cast",
    "settle_execution_fills",
]

if TYPE_CHECKING:
    from quant_platform._portfolio.execution_ledger import (
        Any,
        _normalize_settlement_inputs,
        _settle_all_dates,
        _settle_buy_fill,
        _settle_date,
        _settle_day_fills,
        _settle_sell_fill,
        _validate_settlement_inputs,
        annotations,
        cast,
        settle_execution_fills,
    )

sys.modules[__name__] = import_module("quant_platform._portfolio.execution_ledger")
