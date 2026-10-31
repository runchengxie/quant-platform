"""Module alias preserving implementation identity during compatibility migration."""

import sys
from importlib import import_module
from typing import TYPE_CHECKING

__all__ = ["Mapping", "_quantity_trades", "annotations", "audit_delisting_exits"]

if TYPE_CHECKING:
    from quant_platform._portfolio.execution_sim.delisting import (
        Mapping,
        _quantity_trades,
        annotations,
        audit_delisting_exits,
    )

sys.modules[__name__] = import_module("quant_platform._portfolio.execution_sim.delisting")
