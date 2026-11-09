"""Compatibility module for the Engine-owned quant_backtest_core._minute.minute_execution."""

import sys
from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from quant_backtest_core._minute.minute_execution import (
        CAPITAL_FLOW_COLUMNS as CAPITAL_FLOW_COLUMNS,
    )
    from quant_backtest_core._minute.minute_execution import (
        VALUATION_LEDGER_COLUMNS as VALUATION_LEDGER_COLUMNS,
    )
    from quant_backtest_core._minute.minute_execution import CorporateAction as CorporateAction
    from quant_backtest_core._minute.minute_execution import Mapping as Mapping
    from quant_backtest_core._minute.minute_execution import MappingProxyType as MappingProxyType
    from quant_backtest_core._minute.minute_execution import (
        MinuteDecisionState as MinuteDecisionState,
    )
    from quant_backtest_core._minute.minute_execution import (
        MinuteExecutionConfig as MinuteExecutionConfig,
    )
    from quant_backtest_core._minute.minute_execution import (
        MinuteExecutionResult as MinuteExecutionResult,
    )
    from quant_backtest_core._minute.minute_execution import ValuationEvent as ValuationEvent
    from quant_backtest_core._minute.minute_execution import _MinuteSimulation as _MinuteSimulation
    from quant_backtest_core._minute.minute_execution import _validate as _validate
    from quant_backtest_core._minute.minute_execution import (
        _validate_bar_numbers as _validate_bar_numbers,
    )
    from quant_backtest_core._minute.minute_execution import (
        _validate_intervals as _validate_intervals,
    )
    from quant_backtest_core._minute.minute_execution import (
        _validate_target_weights as _validate_target_weights,
    )
    from quant_backtest_core._minute.minute_execution import annotations as annotations
    from quant_backtest_core._minute.minute_execution import (
        apply_capital_flows as apply_capital_flows,
    )
    from quant_backtest_core._minute.minute_execution import capital_daily as capital_daily
    from quant_backtest_core._minute.minute_execution import cast as cast
    from quant_backtest_core._minute.minute_execution import dataclass as dataclass
    from quant_backtest_core._minute.minute_execution import field as field
    from quant_backtest_core._minute.minute_execution import (
        initialize_capital as initialize_capital,
    )
    from quant_backtest_core._minute.minute_execution import math as math
    from quant_backtest_core._minute.minute_execution import (
        minute_valuation_provenance as minute_valuation_provenance,
    )
    from quant_backtest_core._minute.minute_execution import (
        normalize_corporate_actions as normalize_corporate_actions,
    )
    from quant_backtest_core._minute.minute_execution import (
        normalize_valuation_events as normalize_valuation_events,
    )
    from quant_backtest_core._minute.minute_execution import pd as pd
    from quant_backtest_core._minute.minute_execution import (
        simulate_minute_execution as simulate_minute_execution,
    )

sys.modules[__name__] = import_module("quant_backtest_core._minute.minute_execution")
