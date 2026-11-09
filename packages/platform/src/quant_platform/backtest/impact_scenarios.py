"""Compatibility module for the Engine-owned quant_backtest_core.backtest.impact_scenarios."""

import sys
from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from quant_backtest_core.backtest.impact_scenarios import ImpactFill as ImpactFill
    from quant_backtest_core.backtest.impact_scenarios import ImpactScenario as ImpactScenario
    from quant_backtest_core.backtest.impact_scenarios import Sequence as Sequence
    from quant_backtest_core.backtest.impact_scenarios import dataclass as dataclass
    from quant_backtest_core.backtest.impact_scenarios import fsum as fsum
    from quant_backtest_core.backtest.impact_scenarios import isfinite as isfinite
    from quant_backtest_core.backtest.impact_scenarios import (
        linear_impact_scenario as linear_impact_scenario,
    )

sys.modules[__name__] = import_module("quant_backtest_core.backtest.impact_scenarios")
