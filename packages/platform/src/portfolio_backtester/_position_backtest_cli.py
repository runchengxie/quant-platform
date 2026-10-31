"""Module alias preserving implementation identity during compatibility migration."""

import sys
from importlib import import_module
from typing import TYPE_CHECKING

__all__ = [
    "Any",
    "PositionBacktestConfig",
    "add_position_backtest_args",
    "annotations",
    "run",
    "run_position_backtest",
]

if TYPE_CHECKING:
    from quant_platform._portfolio._position_backtest_cli import (
        Any,
        PositionBacktestConfig,
        add_position_backtest_args,
        annotations,
        run,
        run_position_backtest,
    )

sys.modules[__name__] = import_module("quant_platform._portfolio._position_backtest_cli")
