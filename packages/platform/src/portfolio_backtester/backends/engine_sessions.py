"""Compatibility alias for the platform canonical engine adapter."""

import sys
from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from quant_platform.backtest.engine_sessions import EngineClient as EngineClient
    from quant_platform.backtest.engine_sessions import EngineProtocolError as EngineProtocolError

sys.modules[__name__] = import_module("quant_platform.backtest.engine_sessions")
