"""Module alias preserving implementation identity during compatibility migration."""

import sys
from importlib import import_module
from typing import TYPE_CHECKING

__all__ = [
    "Any",
    "Path",
    "PositionBacktestConfig",
    "PositionBacktestResult",
    "_config_from_run",
    "_read_frame",
    "_read_yaml",
    "_relative_to_run",
    "_resolve_path",
    "_update_run_summary",
    "_write_result",
    "add_position_backtest_args",
    "annotations",
    "run",
    "run_position_backtest",
]

if TYPE_CHECKING:
    from quant_platform._portfolio.position_backtest_cli import (
        Any,
        Path,
        PositionBacktestConfig,
        PositionBacktestResult,
        _config_from_run,
        _read_frame,
        _read_yaml,
        _relative_to_run,
        _resolve_path,
        _update_run_summary,
        _write_result,
        add_position_backtest_args,
        annotations,
        run,
        run_position_backtest,
    )

sys.modules[__name__] = import_module("quant_platform._portfolio.position_backtest_cli")
