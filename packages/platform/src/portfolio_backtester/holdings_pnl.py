"""Module alias preserving implementation identity during compatibility migration."""

import sys
from importlib import import_module
from typing import TYPE_CHECKING

__all__ = ["holding_pnl"]

if TYPE_CHECKING:
    from quant_platform._portfolio.holdings_pnl import (
        holding_pnl,
    )

sys.modules[__name__] = import_module("quant_platform._portfolio.holdings_pnl")
