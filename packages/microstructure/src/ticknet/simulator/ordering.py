"""Compatibility alias for the Engine-owned quant_backtest_core.microstructure.ordering."""

import sys
from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from quant_backtest_core.microstructure.ordering import CHANNEL_COLUMNS as CHANNEL_COLUMNS
    from quant_backtest_core.microstructure.ordering import SEQUENCE_COLUMNS as SEQUENCE_COLUMNS
    from quant_backtest_core.microstructure.ordering import Any as Any
    from quant_backtest_core.microstructure.ordering import Iterable as Iterable
    from quant_backtest_core.microstructure.ordering import _first_present as _first_present
    from quant_backtest_core.microstructure.ordering import (
        _sequence_integrity as _sequence_integrity,
    )
    from quant_backtest_core.microstructure.ordering import _timestamp_bucket as _timestamp_bucket
    from quant_backtest_core.microstructure.ordering import defaultdict as defaultdict
    from quant_backtest_core.microstructure.ordering import (
        detect_ordering_columns as detect_ordering_columns,
    )
    from quant_backtest_core.microstructure.ordering import (
        ordering_provenance as ordering_provenance,
    )
    from quant_backtest_core.microstructure.ordering import pairwise as pairwise
    from quant_backtest_core.microstructure.ordering import (
        sort_simulator_events as sort_simulator_events,
    )

sys.modules[__name__] = import_module("quant_backtest_core.microstructure.ordering")
