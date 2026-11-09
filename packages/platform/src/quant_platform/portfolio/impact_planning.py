"""Compatibility alias for the Engine-owned quant_backtest_core.planning.impact_planning."""

import sys
from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from quant_backtest_core.planning.impact_planning import Bounds as Bounds
    from quant_backtest_core.planning.impact_planning import ImpactPlan as ImpactPlan
    from quant_backtest_core.planning.impact_planning import (
        ImpactPlanningRequest as ImpactPlanningRequest,
    )
    from quant_backtest_core.planning.impact_planning import LinearConstraint as LinearConstraint
    from quant_backtest_core.planning.impact_planning import LinearImpact as LinearImpact
    from quant_backtest_core.planning.impact_planning import _array as _array
    from quant_backtest_core.planning.impact_planning import _inputs as _inputs
    from quant_backtest_core.planning.impact_planning import _parameters as _parameters
    from quant_backtest_core.planning.impact_planning import _quadratic as _quadratic
    from quant_backtest_core.planning.impact_planning import _replay as _replay
    from quant_backtest_core.planning.impact_planning import _request_digest as _request_digest
    from quant_backtest_core.planning.impact_planning import asdict as asdict
    from quant_backtest_core.planning.impact_planning import dataclass as dataclass
    from quant_backtest_core.planning.impact_planning import hashlib as hashlib
    from quant_backtest_core.planning.impact_planning import json as json
    from quant_backtest_core.planning.impact_planning import minimize as minimize
    from quant_backtest_core.planning.impact_planning import np as np
    from quant_backtest_core.planning.impact_planning import plan_with_impact as plan_with_impact

sys.modules[__name__] = import_module("quant_backtest_core.planning.impact_planning")
