"""Module alias preserving implementation identity during compatibility migration."""

import sys
from importlib import import_module
from typing import TYPE_CHECKING

__all__ = [
    "Ledger",
    "Position",
    "StaggeredTarget",
    "annotations",
    "append_buy_order",
    "append_sell_order",
    "raw_audit_fields",
]

if TYPE_CHECKING:
    from quant_platform._portfolio.staggered_cohort_execution_records import (
        Ledger,
        Position,
        StaggeredTarget,
        annotations,
        append_buy_order,
        append_sell_order,
        raw_audit_fields,
    )

sys.modules[__name__] = import_module(
    "quant_platform._portfolio.staggered_cohort_execution_records"
)
