"""Compatibility alias for the Engine-owned quant_backtest_core.planning.discrete_inventory."""

import sys
from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from quant_backtest_core.planning.discrete_inventory import Decimal as Decimal
    from quant_backtest_core.planning.discrete_inventory import (
        DiscreteInventoryPlan as DiscreteInventoryPlan,
    )
    from quant_backtest_core.planning.discrete_inventory import (
        DiscreteInventoryRequest as DiscreteInventoryRequest,
    )
    from quant_backtest_core.planning.discrete_inventory import (
        DiscreteInventoryResult as DiscreteInventoryResult,
    )
    from quant_backtest_core.planning.discrete_inventory import Fraction as Fraction
    from quant_backtest_core.planning.discrete_inventory import Scalar as Scalar
    from quant_backtest_core.planning.discrete_inventory import _domains as _domains
    from quant_backtest_core.planning.discrete_inventory import _Exact as _Exact
    from quant_backtest_core.planning.discrete_inventory import _heuristic as _heuristic
    from quant_backtest_core.planning.discrete_inventory import _key as _key
    from quant_backtest_core.planning.discrete_inventory import _number as _number
    from quant_backtest_core.planning.discrete_inventory import _plan as _plan
    from quant_backtest_core.planning.discrete_inventory import _validate as _validate
    from quant_backtest_core.planning.discrete_inventory import _validate_exact as _validate_exact
    from quant_backtest_core.planning.discrete_inventory import _vector as _vector
    from quant_backtest_core.planning.discrete_inventory import dataclass as dataclass
    from quant_backtest_core.planning.discrete_inventory import prod as prod
    from quant_backtest_core.planning.discrete_inventory import product as product
    from quant_backtest_core.planning.discrete_inventory import (
        solve_discrete_inventory as solve_discrete_inventory,
    )

sys.modules[__name__] = import_module("quant_backtest_core.planning.discrete_inventory")
