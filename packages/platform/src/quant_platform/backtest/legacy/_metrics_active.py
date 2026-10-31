"""Module alias preserving implementation identity during compatibility migration."""

import sys
from importlib import import_module
from typing import TYPE_CHECKING

__all__ = [
    "_active_total_return",
    "_beta",
    "_empty_active_summary",
    "_tracking_stats",
    "annotations",
    "summarize_active_returns",
]

if TYPE_CHECKING:
    from quant_platform._portfolio._metrics_active import (
        _active_total_return,
        _beta,
        _empty_active_summary,
        _tracking_stats,
        annotations,
        summarize_active_returns,
    )

sys.modules[__name__] = import_module("quant_platform._portfolio._metrics_active")
