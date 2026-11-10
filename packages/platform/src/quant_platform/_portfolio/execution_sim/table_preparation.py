"""Engine alias: quant_backtest_core.daily.execution_sim.table_preparation."""

from __future__ import annotations

import sys
from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from quant_backtest_core.daily.execution_sim.table_preparation import Any as Any
    from quant_backtest_core.daily.execution_sim.table_preparation import (
        ExecutionSimConfig as ExecutionSimConfig,
    )
    from quant_backtest_core.daily.execution_sim.table_preparation import (
        _build_execution_tables as _build_execution_tables,
    )
    from quant_backtest_core.daily.execution_sim.table_preparation import (
        _build_tradable_table as _build_tradable_table,
    )
    from quant_backtest_core.daily.execution_sim.table_preparation import (
        _ExecutionTables as _ExecutionTables,
    )
    from quant_backtest_core.daily.execution_sim.table_preparation import (
        _prepare_execution_tables as _prepare_execution_tables,
    )
    from quant_backtest_core.daily.execution_sim.table_preparation import (
        _prepare_long_only_execution_positions as _prepare_long_only_execution_positions,
    )
    from quant_backtest_core.daily.execution_sim.table_preparation import pd as pd
    from quant_backtest_core.daily.execution_sim.table_preparation import (
        prepare_execution_tables as prepare_execution_tables,
    )
    from quant_backtest_core.daily.execution_sim.table_preparation import (
        required_execution_sim_columns as required_execution_sim_columns,
    )

sys.modules[__name__] = import_module("quant_backtest_core.daily.execution_sim.table_preparation")
