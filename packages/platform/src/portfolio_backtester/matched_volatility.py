"""Module alias preserving implementation identity during compatibility migration."""

import sys
from importlib import import_module
from typing import TYPE_CHECKING

__all__ = ["match_realized_volatility"]

if TYPE_CHECKING:
    from quant_platform._portfolio.matched_volatility import (
        match_realized_volatility,
    )

sys.modules[__name__] = import_module("quant_platform._portfolio.matched_volatility")
