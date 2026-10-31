"""Module alias preserving implementation identity during compatibility migration."""

import sys
from importlib import import_module
from typing import TYPE_CHECKING

__all__ = [
    "Mapping",
    "PointInTimeDataView",
    "PointInTimeTable",
    "Real",
    "ResearchClock",
    "Sequence",
    "_BoundDataView",
    "_aware_timestamp",
    "annotations",
    "dataclass",
    "datetime",
    "field",
    "isfinite",
    "validate_research_clock",
]

if TYPE_CHECKING:
    from quant_platform._portfolio.point_in_time import (
        Mapping,
        PointInTimeDataView,
        PointInTimeTable,
        Real,
        ResearchClock,
        Sequence,
        _aware_timestamp,
        _BoundDataView,
        annotations,
        dataclass,
        datetime,
        field,
        isfinite,
        validate_research_clock,
    )

sys.modules[__name__] = import_module("quant_platform._portfolio.point_in_time")
