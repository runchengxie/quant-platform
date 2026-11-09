"""Compatibility module for the Engine-owned quant_backtest_core.backtest.market_paths."""

import sys
from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from quant_backtest_core.backtest.market_paths import _FIELDS as _FIELDS
    from quant_backtest_core.backtest.market_paths import _SCOPE as _SCOPE
    from quant_backtest_core.backtest.market_paths import _UNITS as _UNITS
    from quant_backtest_core.backtest.market_paths import _VERSION as _VERSION
    from quant_backtest_core.backtest.market_paths import FrozenPathModel as FrozenPathModel
    from quant_backtest_core.backtest.market_paths import Mapping as Mapping
    from quant_backtest_core.backtest.market_paths import MarketPathSpec as MarketPathSpec
    from quant_backtest_core.backtest.market_paths import Sequence as Sequence
    from quant_backtest_core.backtest.market_paths import _clock as _clock
    from quant_backtest_core.backtest.market_paths import _digest as _digest
    from quant_backtest_core.backtest.market_paths import _generate_one as _generate_one
    from quant_backtest_core.backtest.market_paths import _validate_bar as _validate_bar
    from quant_backtest_core.backtest.market_paths import _validate_vwap as _validate_vwap
    from quant_backtest_core.backtest.market_paths import annotations as annotations
    from quant_backtest_core.backtest.market_paths import asdict as asdict
    from quant_backtest_core.backtest.market_paths import dataclass as dataclass
    from quant_backtest_core.backtest.market_paths import fit_market_paths as fit_market_paths
    from quant_backtest_core.backtest.market_paths import (
        generate_market_paths as generate_market_paths,
    )
    from quant_backtest_core.backtest.market_paths import hashlib as hashlib
    from quant_backtest_core.backtest.market_paths import itertools as itertools
    from quant_backtest_core.backtest.market_paths import json as json
    from quant_backtest_core.backtest.market_paths import math as math
    from quant_backtest_core.backtest.market_paths import pd as pd

sys.modules[__name__] = import_module("quant_backtest_core.backtest.market_paths")
