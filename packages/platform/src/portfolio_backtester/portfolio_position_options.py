"""Module alias preserving implementation identity during compatibility migration."""

import sys
from importlib import import_module
from typing import TYPE_CHECKING

__all__ = [
    "MaxNewNamesShortfallPolicy",
    "PortfolioPositionOptions",
    "SelectionPricePolicy",
    "TargetWeightPolicy",
    "annotations",
    "controlled_selection_day",
    "dataclass",
    "validate_fixed_slot_configuration",
]

if TYPE_CHECKING:
    from quant_platform._portfolio.portfolio_position_options import (
        MaxNewNamesShortfallPolicy,
        PortfolioPositionOptions,
        SelectionPricePolicy,
        TargetWeightPolicy,
        annotations,
        controlled_selection_day,
        dataclass,
        validate_fixed_slot_configuration,
    )

sys.modules[__name__] = import_module("quant_platform._portfolio.portfolio_position_options")
