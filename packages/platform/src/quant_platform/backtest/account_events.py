"""Compatibility alias for the Engine-owned quant_backtest_core.backtest.account_events."""

import sys
from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from quant_backtest_core.backtest.account_events import AccountEvent as AccountEvent
    from quant_backtest_core.backtest.account_events import (
        AccountEventAdapter as AccountEventAdapter,
    )
    from quant_backtest_core.backtest.account_events import EventAccountConfig as EventAccountConfig
    from quant_backtest_core.backtest.account_events import HouseMargin as HouseMargin
    from quant_backtest_core.backtest.account_events import Literal as Literal
    from quant_backtest_core.backtest.account_events import Observed as Observed
    from quant_backtest_core.backtest.account_events import PaperFill as PaperFill
    from quant_backtest_core.backtest.account_events import PaperState as PaperState
    from quant_backtest_core.backtest.account_events import _account_nav as _account_nav
    from quant_backtest_core.backtest.account_events import _AccountData as _AccountData
    from quant_backtest_core.backtest.account_events import _clock as _clock
    from quant_backtest_core.backtest.account_events import _digest as _digest
    from quant_backtest_core.backtest.account_events import _finite as _finite
    from quant_backtest_core.backtest.account_events import _integer as _integer
    from quant_backtest_core.backtest.account_events import _json as _json
    from quant_backtest_core.backtest.account_events import (
        _margin_diagnostics as _margin_diagnostics,
    )
    from quant_backtest_core.backtest.account_events import _name as _name
    from quant_backtest_core.backtest.account_events import _Order as _Order
    from quant_backtest_core.backtest.account_events import _receivables as _receivables
    from quant_backtest_core.backtest.account_events import _state as _state
    from quant_backtest_core.backtest.account_events import _StateWire as _StateWire
    from quant_backtest_core.backtest.account_events import _total as _total
    from quant_backtest_core.backtest.account_events import _validate_data as _validate_data
    from quant_backtest_core.backtest.account_events import _wire as _wire
    from quant_backtest_core.backtest.account_events import asdict as asdict
    from quant_backtest_core.backtest.account_events import dataclass as dataclass
    from quant_backtest_core.backtest.account_events import deepcopy as deepcopy
    from quant_backtest_core.backtest.account_events import field as field
    from quant_backtest_core.backtest.account_events import fsum as fsum
    from quant_backtest_core.backtest.account_events import isfinite as isfinite
    from quant_backtest_core.backtest.account_events import json as json
    from quant_backtest_core.backtest.account_events import pd as pd
    from quant_backtest_core.backtest.account_events import (
        project_paper_account as project_paper_account,
    )
    from quant_backtest_core.backtest.account_events import sha256 as sha256

sys.modules[__name__] = import_module("quant_backtest_core.backtest.account_events")
