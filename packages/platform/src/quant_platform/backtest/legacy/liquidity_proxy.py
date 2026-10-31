"""Module alias preserving implementation identity during compatibility migration."""

import sys
from importlib import import_module
from typing import TYPE_CHECKING

__all__ = [
    "EXECUTION_LIQUIDITY_PROXY_PATTERN",
    "_derive_execution_liquidity_proxy_columns",
    "_parse_execution_liquidity_proxy_column",
    "annotations",
    "derive_execution_liquidity_proxy_columns",
    "logger",
    "parse_execution_liquidity_proxy_column",
]

if TYPE_CHECKING:
    from quant_platform._portfolio.liquidity_proxy import (
        EXECUTION_LIQUIDITY_PROXY_PATTERN,
        _derive_execution_liquidity_proxy_columns,
        _parse_execution_liquidity_proxy_column,
        annotations,
        derive_execution_liquidity_proxy_columns,
        logger,
        parse_execution_liquidity_proxy_column,
    )

sys.modules[__name__] = import_module("quant_platform._portfolio.liquidity_proxy")
