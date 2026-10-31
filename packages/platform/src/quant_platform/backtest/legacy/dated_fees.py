"""Module alias preserving implementation identity during compatibility migration."""

import sys
from importlib import import_module
from typing import TYPE_CHECKING

__all__ = [
    "Any",
    "DatedFeeQuote",
    "DatedFeeSchedule",
    "DatedTradeFeeModel",
    "FeeQuoteContext",
    "FeeSchedulePeriod",
    "Literal",
    "Mapping",
    "MappingProxyType",
    "Side",
    "_as_date",
    "_non_negative_finite",
    "annotations",
    "dataclass",
    "date",
    "datetime",
    "pairwise",
]

if TYPE_CHECKING:
    from quant_platform._portfolio.dated_fees import (
        Any,
        DatedFeeQuote,
        DatedFeeSchedule,
        DatedTradeFeeModel,
        FeeQuoteContext,
        FeeSchedulePeriod,
        Literal,
        Mapping,
        MappingProxyType,
        Side,
        _as_date,
        _non_negative_finite,
        annotations,
        dataclass,
        date,
        datetime,
        pairwise,
    )

sys.modules[__name__] = import_module("quant_platform._portfolio.dated_fees")
