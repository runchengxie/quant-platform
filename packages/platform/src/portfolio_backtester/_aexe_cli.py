"""Module alias preserving implementation identity during compatibility migration."""

import sys
from importlib import import_module
from typing import TYPE_CHECKING

__all__ = [
    "Any",
    "Path",
    "_add_trade_fee_args",
    "_parse_bool",
    "_parse_optional_float",
    "_parse_top_ks",
    "_set_trade_fee_args",
    "_write_executable_outputs",
    "annotations",
    "load_positions",
    "load_prices",
    "main",
]

if TYPE_CHECKING:
    from quant_platform._portfolio._aexe_cli import (
        Any,
        Path,
        _add_trade_fee_args,
        _parse_bool,
        _parse_optional_float,
        _parse_top_ks,
        _set_trade_fee_args,
        _write_executable_outputs,
        annotations,
        load_positions,
        load_prices,
        main,
    )

sys.modules[__name__] = import_module("quant_platform._portfolio._aexe_cli")
