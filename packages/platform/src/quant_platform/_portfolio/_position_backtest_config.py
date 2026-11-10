"""Compatibility alias for the Engine-owned quant_backtest_core.daily._position_backtest_config."""

from __future__ import annotations

import sys
from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from quant_backtest_core.daily._position_backtest_config import Any as Any
    from quant_backtest_core.daily._position_backtest_config import Literal as Literal
    from quant_backtest_core.daily._position_backtest_config import NaTType as NaTType
    from quant_backtest_core.daily._position_backtest_config import (
        PositionBacktestConfig as PositionBacktestConfig,
    )
    from quant_backtest_core.daily._position_backtest_config import (
        PositionBacktestResult as PositionBacktestResult,
    )
    from quant_backtest_core.daily._position_backtest_config import (
        PositionExitPolicy as PositionExitPolicy,
    )
    from quant_backtest_core.daily._position_backtest_config import _date_key as _date_key
    from quant_backtest_core.daily._position_backtest_config import _date_series as _date_series
    from quant_backtest_core.daily._position_backtest_config import _date_value as _date_value
    from quant_backtest_core.daily._position_backtest_config import (
        assert_positions_by_rebalance_frame as assert_positions_by_rebalance_frame,
    )
    from quant_backtest_core.daily._position_backtest_config import cast as cast
    from quant_backtest_core.daily._position_backtest_config import dataclass as dataclass
    from quant_backtest_core.daily._position_backtest_config import (
        normalize_position_backtest_periods as normalize_position_backtest_periods,
    )
    from quant_backtest_core.daily._position_backtest_config import (
        normalize_position_backtest_positions as normalize_position_backtest_positions,
    )
    from quant_backtest_core.daily._position_backtest_config import (
        normalize_position_backtest_pricing as normalize_position_backtest_pricing,
    )
    from quant_backtest_core.daily._position_backtest_config import pd as pd

sys.modules[__name__] = import_module("quant_backtest_core.daily._position_backtest_config")
