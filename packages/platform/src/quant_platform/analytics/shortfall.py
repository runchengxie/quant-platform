"""Module alias preserving implementation identity during compatibility migration."""

import sys
from importlib import import_module
from typing import TYPE_CHECKING

__all__ = [
    "SHORTFALL_SCHEMA",
    "Fill",
    "Literal",
    "OrderCost",
    "_number",
    "annotations",
    "dataclass",
    "date",
    "datetime",
    "fsum",
    "isfinite",
    "order_shortfall",
]

if TYPE_CHECKING:
    from quant_platform._portfolio.shortfall import (
        SHORTFALL_SCHEMA,
        Fill,
        Literal,
        OrderCost,
        _number,
        annotations,
        dataclass,
        date,
        datetime,
        fsum,
        isfinite,
        order_shortfall,
    )

sys.modules[__name__] = import_module("quant_platform._portfolio.shortfall")
