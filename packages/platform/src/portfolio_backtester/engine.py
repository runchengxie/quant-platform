"""Module alias preserving implementation identity during compatibility migration."""

import sys
from importlib import import_module
from typing import TYPE_CHECKING

__all__ = ["_compute_trade_summary", "_run_backtest_config", "annotations", "backtest_topk"]

if TYPE_CHECKING:
    from quant_platform._portfolio.engine import (
        _compute_trade_summary,
        _run_backtest_config,
        annotations,
        backtest_topk,
    )

sys.modules[__name__] = import_module("quant_platform._portfolio.engine")
