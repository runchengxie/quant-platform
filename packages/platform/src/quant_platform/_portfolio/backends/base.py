"""Module alias preserving implementation identity during compatibility migration."""

import sys
from importlib import import_module

sys.modules[__name__] = import_module("quant_platform.backtest.contracts")
