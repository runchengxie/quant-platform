"""Compatibility alias for the Engine-owned quant_backtest_core.planning.sleeve_allocation."""

import sys
from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from quant_backtest_core.planning.sleeve_allocation import Decimal as Decimal
    from quant_backtest_core.planning.sleeve_allocation import ExternalOrder as ExternalOrder
    from quant_backtest_core.planning.sleeve_allocation import RecordedFill as RecordedFill
    from quant_backtest_core.planning.sleeve_allocation import SleeveAllocation as SleeveAllocation
    from quant_backtest_core.planning.sleeve_allocation import SleeveDelta as SleeveDelta
    from quant_backtest_core.planning.sleeve_allocation import SleeveDemand as SleeveDemand
    from quant_backtest_core.planning.sleeve_allocation import SleeveNetPlan as SleeveNetPlan
    from quant_backtest_core.planning.sleeve_allocation import _batch_inputs as _batch_inputs
    from quant_backtest_core.planning.sleeve_allocation import _clock as _clock
    from quant_backtest_core.planning.sleeve_allocation import _decimal as _decimal
    from quant_backtest_core.planning.sleeve_allocation import _demand as _demand
    from quant_backtest_core.planning.sleeve_allocation import _exact as _exact
    from quant_backtest_core.planning.sleeve_allocation import _fee as _fee
    from quant_backtest_core.planning.sleeve_allocation import _integer as _integer
    from quant_backtest_core.planning.sleeve_allocation import _name as _name
    from quant_backtest_core.planning.sleeve_allocation import _pro_rata as _pro_rata
    from quant_backtest_core.planning.sleeve_allocation import _recorded_fills as _recorded_fills
    from quant_backtest_core.planning.sleeve_allocation import (
        allocate_external_fills as allocate_external_fills,
    )
    from quant_backtest_core.planning.sleeve_allocation import dataclass as dataclass
    from quant_backtest_core.planning.sleeve_allocation import defaultdict as defaultdict
    from quant_backtest_core.planning.sleeve_allocation import (
        net_sleeve_demands as net_sleeve_demands,
    )
    from quant_backtest_core.planning.sleeve_allocation import replace as replace

sys.modules[__name__] = import_module("quant_backtest_core.planning.sleeve_allocation")
