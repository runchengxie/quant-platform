"""Module alias preserving implementation identity during compatibility migration."""

import sys
from importlib import import_module
from typing import TYPE_CHECKING

__all__ = ["volatility_exposure"]

if TYPE_CHECKING:
    from quant_platform._portfolio.volatility_exposure import (
        volatility_exposure,
    )

sys.modules[__name__] = import_module("quant_platform._portfolio.volatility_exposure")
