"""Module alias preserving implementation identity during compatibility migration."""

import sys
from importlib import import_module
from typing import TYPE_CHECKING

__all__ = [
    "Any",
    "Mapping",
    "_benchmark_prices_by_period",
    "_benchmark_returns_by_period",
    "annotations",
    "build_benchmark_series",
    "cast",
    "warn_if_delay_exit_lag",
]

if TYPE_CHECKING:
    from quant_platform._portfolio.benchmarking import (
        Any,
        Mapping,
        _benchmark_prices_by_period,
        _benchmark_returns_by_period,
        annotations,
        build_benchmark_series,
        cast,
        warn_if_delay_exit_lag,
    )

sys.modules[__name__] = import_module("quant_platform._portfolio.benchmarking")
