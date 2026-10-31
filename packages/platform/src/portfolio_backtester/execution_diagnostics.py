"""Module alias preserving implementation identity during compatibility migration."""

import sys
from importlib import import_module
from typing import TYPE_CHECKING

__all__ = ["annotations", "attribute_delayed_fills"]

if TYPE_CHECKING:
    from quant_platform._portfolio.execution_diagnostics import (
        annotations,
        attribute_delayed_fills,
    )

sys.modules[__name__] = import_module("quant_platform._portfolio.execution_diagnostics")
