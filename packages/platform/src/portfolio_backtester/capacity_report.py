"""Module alias preserving implementation identity during compatibility migration."""

import sys
from importlib import import_module
from typing import TYPE_CHECKING

__all__ = [
    "DEFAULT_PARTICIPATION_RATES",
    "DEFAULT_PORTFOLIO_VALUES",
    "DEFAULT_PRIMARY_PARTICIPATION_RATE",
    "THRESHOLD_PROFILES",
    "CapacityThresholds",
    "add_capacity_report_args",
    "annotations",
    "build_capacity_report",
    "run",
]

if TYPE_CHECKING:
    from quant_platform._portfolio.capacity_report import (
        DEFAULT_PARTICIPATION_RATES,
        DEFAULT_PORTFOLIO_VALUES,
        DEFAULT_PRIMARY_PARTICIPATION_RATE,
        THRESHOLD_PROFILES,
        CapacityThresholds,
        add_capacity_report_args,
        annotations,
        build_capacity_report,
        run,
    )

sys.modules[__name__] = import_module("quant_platform._portfolio.capacity_report")
