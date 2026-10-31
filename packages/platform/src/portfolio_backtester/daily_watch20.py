"""Module alias preserving implementation identity during compatibility migration."""

import sys
from importlib import import_module
from typing import TYPE_CHECKING

__all__ = [
    "DailyWatch20Config",
    "DailyWatch20Receipt",
    "DailyWatch20Result",
    "DailyWatch20SelectionError",
    "FallbackMode",
    "GuardFactorSpec",
    "ReceiptStatus",
    "annotations",
    "select_daily_watch20",
]

if TYPE_CHECKING:
    from quant_platform._portfolio.daily_watch20 import (
        DailyWatch20Config,
        DailyWatch20Receipt,
        DailyWatch20Result,
        DailyWatch20SelectionError,
        FallbackMode,
        GuardFactorSpec,
        ReceiptStatus,
        annotations,
        select_daily_watch20,
    )

sys.modules[__name__] = import_module("quant_platform._portfolio.daily_watch20")
