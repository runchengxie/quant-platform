"""Compatibility module for the Engine-owned quant_backtest_core._minute.corporate_actions."""

import sys
from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from quant_backtest_core._minute.corporate_actions import CorporateAction as CorporateAction
    from quant_backtest_core._minute.corporate_actions import Iterable as Iterable
    from quant_backtest_core._minute.corporate_actions import _action_date as _action_date
    from quant_backtest_core._minute.corporate_actions import (
        _validate_action_dates as _validate_action_dates,
    )
    from quant_backtest_core._minute.corporate_actions import (
        _validate_action_numbers as _validate_action_numbers,
    )
    from quant_backtest_core._minute.corporate_actions import annotations as annotations
    from quant_backtest_core._minute.corporate_actions import dataclass as dataclass
    from quant_backtest_core._minute.corporate_actions import date as date
    from quant_backtest_core._minute.corporate_actions import isfinite as isfinite
    from quant_backtest_core._minute.corporate_actions import (
        normalize_corporate_actions as normalize_corporate_actions,
    )
    from quant_backtest_core._minute.corporate_actions import pd as pd

sys.modules[__name__] = import_module("quant_backtest_core._minute.corporate_actions")
