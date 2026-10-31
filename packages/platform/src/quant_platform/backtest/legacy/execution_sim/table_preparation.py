"""Module alias preserving implementation identity during compatibility migration."""

import sys
from importlib import import_module
from typing import TYPE_CHECKING

__all__ = [
    "Any",
    "ExecutionSimConfig",
    "_ExecutionTables",
    "_build_execution_tables",
    "_build_tradable_table",
    "_prepare_execution_tables",
    "_prepare_long_only_execution_positions",
    "annotations",
    "prepare_execution_tables",
    "required_execution_sim_columns",
]

if TYPE_CHECKING:
    from quant_platform._portfolio.execution_sim.table_preparation import (
        Any,
        ExecutionSimConfig,
        _build_execution_tables,
        _build_tradable_table,
        _ExecutionTables,
        _prepare_execution_tables,
        _prepare_long_only_execution_positions,
        annotations,
        prepare_execution_tables,
        required_execution_sim_columns,
    )

sys.modules[__name__] = import_module("quant_platform._portfolio.execution_sim.table_preparation")
