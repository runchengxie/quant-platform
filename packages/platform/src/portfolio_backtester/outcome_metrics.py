"""Module alias preserving implementation identity during compatibility migration."""

import sys
from importlib import import_module
from typing import TYPE_CHECKING

__all__ = [
    "OutcomeDistributionReport",
    "Sequence",
    "_finite_array",
    "_validate_path_semantics",
    "annotations",
    "asdict",
    "dataclass",
    "field",
    "summarize_outcome_distribution",
]

if TYPE_CHECKING:
    from quant_platform._portfolio.outcome_metrics import (
        OutcomeDistributionReport,
        Sequence,
        _finite_array,
        _validate_path_semantics,
        annotations,
        asdict,
        dataclass,
        field,
        summarize_outcome_distribution,
    )

sys.modules[__name__] = import_module("quant_platform._portfolio.outcome_metrics")
