"""Engine alias: quant_backtest_core.daily.execution_sim.config."""

from __future__ import annotations

import sys
from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from quant_backtest_core.daily.execution_sim.config import (
        SELL_UNTIL_NEXT_REBALANCE as SELL_UNTIL_NEXT_REBALANCE,
    )
    from quant_backtest_core.daily.execution_sim.config import Any as Any
    from quant_backtest_core.daily.execution_sim.config import (
        ExecutionSimConfig as ExecutionSimConfig,
    )
    from quant_backtest_core.daily.execution_sim.config import Mapping as Mapping
    from quant_backtest_core.daily.execution_sim.config import (
        _coerce_optional_str as _coerce_optional_str,
    )
    from quant_backtest_core.daily.execution_sim.config import (
        _coerce_positive_float as _coerce_positive_float,
    )
    from quant_backtest_core.daily.execution_sim.config import (
        _coerce_positive_int as _coerce_positive_int,
    )
    from quant_backtest_core.daily.execution_sim.config import (
        _MarketRuleConfig as _MarketRuleConfig,
    )
    from quant_backtest_core.daily.execution_sim.config import (
        _resolve_liquidity_cols as _resolve_liquidity_cols,
    )
    from quant_backtest_core.daily.execution_sim.config import (
        _resolve_market_rule_config as _resolve_market_rule_config,
    )
    from quant_backtest_core.daily.execution_sim.config import (
        _resolve_sell_max_days as _resolve_sell_max_days,
    )
    from quant_backtest_core.daily.execution_sim.config import (
        build_execution_sim_config as build_execution_sim_config,
    )
    from quant_backtest_core.daily.execution_sim.config import cast as cast
    from quant_backtest_core.daily.execution_sim.config import dataclass as dataclass
    from quant_backtest_core.daily.execution_sim.config import (
        describe_execution_sim_config as describe_execution_sim_config,
    )
    from quant_backtest_core.daily.execution_sim.config import np as np
    from quant_backtest_core.daily.execution_sim.config import (
        required_execution_sim_columns as required_execution_sim_columns,
    )

sys.modules[__name__] = import_module("quant_backtest_core.daily.execution_sim.config")
