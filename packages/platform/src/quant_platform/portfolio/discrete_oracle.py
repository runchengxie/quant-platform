"""Compatibility alias for the Engine-owned quant_backtest_core.planning.discrete_oracle."""

import sys
from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from quant_backtest_core.planning.discrete_oracle import Fraction as Fraction
    from quant_backtest_core.planning.discrete_oracle import LotOracleResult as LotOracleResult
    from quant_backtest_core.planning.discrete_oracle import Sequence as Sequence
    from quant_backtest_core.planning.discrete_oracle import _validate as _validate
    from quant_backtest_core.planning.discrete_oracle import dataclass as dataclass
    from quant_backtest_core.planning.discrete_oracle import (
        enumerate_lot_portfolios as enumerate_lot_portfolios,
    )
    from quant_backtest_core.planning.discrete_oracle import isfinite as isfinite
    from quant_backtest_core.planning.discrete_oracle import prod as prod
    from quant_backtest_core.planning.discrete_oracle import product as product

sys.modules[__name__] = import_module("quant_backtest_core.planning.discrete_oracle")
