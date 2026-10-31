"""Module alias preserving implementation identity during compatibility migration."""

import sys
from importlib import import_module
from typing import TYPE_CHECKING

__all__ = [
    "_REQUIRED_RAW_PRICING_COLUMNS",
    "_SHANGHAI",
    "Any",
    "StaggeredTarget",
    "_aware_timestamp",
    "_open_calendar_dates",
    "_prepare_signal_frame",
    "_validate_availability",
    "annotations",
    "build_execution_date_map",
    "cast",
    "dataclass",
    "prepare_staggered_pricing",
    "prepare_staggered_targets",
    "time",
]

if TYPE_CHECKING:
    from quant_platform._portfolio.staggered_cohort_inputs import (
        _REQUIRED_RAW_PRICING_COLUMNS,
        _SHANGHAI,
        Any,
        StaggeredTarget,
        _aware_timestamp,
        _open_calendar_dates,
        _prepare_signal_frame,
        _validate_availability,
        annotations,
        build_execution_date_map,
        cast,
        dataclass,
        prepare_staggered_pricing,
        prepare_staggered_targets,
        time,
    )

sys.modules[__name__] = import_module("quant_platform._portfolio.staggered_cohort_inputs")
