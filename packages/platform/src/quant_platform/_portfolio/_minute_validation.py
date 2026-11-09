"""Compatibility module for the Engine-owned quant_backtest_core._minute._minute_validation."""

import sys
from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from quant_backtest_core._minute._minute_validation import _validate as _validate
    from quant_backtest_core._minute._minute_validation import (
        _validate_bar_numbers as _validate_bar_numbers,
    )
    from quant_backtest_core._minute._minute_validation import (
        _validate_intervals as _validate_intervals,
    )
    from quant_backtest_core._minute._minute_validation import (
        _validate_mark_provenance as _validate_mark_provenance,
    )
    from quant_backtest_core._minute._minute_validation import (
        _validate_target_weights as _validate_target_weights,
    )
    from quant_backtest_core._minute._minute_validation import math as math
    from quant_backtest_core._minute._minute_validation import pd as pd

sys.modules[__name__] = import_module("quant_backtest_core._minute._minute_validation")
