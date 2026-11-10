"""Engine alias: quant_backtest_core.daily.execution_sim.cost_evidence."""

from __future__ import annotations

import sys
from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from quant_backtest_core.daily.execution_sim.cost_evidence import (
        _COMPONENT_COLUMNS as _COMPONENT_COLUMNS,
    )
    from quant_backtest_core.daily.execution_sim.cost_evidence import (
        CostComponents as CostComponents,
    )
    from quant_backtest_core.daily.execution_sim.cost_evidence import CostEvidence as CostEvidence
    from quant_backtest_core.daily.execution_sim.cost_evidence import CostGroup as CostGroup
    from quant_backtest_core.daily.execution_sim.cost_evidence import _fill_group as _fill_group
    from quant_backtest_core.daily.execution_sim.cost_evidence import (
        _optional_text as _optional_text,
    )
    from quant_backtest_core.daily.execution_sim.cost_evidence import pd as pd
    from quant_backtest_core.daily.execution_sim.cost_evidence import (
        simulator_cost_evidence as simulator_cost_evidence,
    )

sys.modules[__name__] = import_module("quant_backtest_core.daily.execution_sim.cost_evidence")
