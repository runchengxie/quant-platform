"""Module alias preserving implementation identity during compatibility migration."""

import sys
from importlib import import_module
from typing import TYPE_CHECKING

__all__ = [
    "Any",
    "Mapping",
    "_copy_target_frame",
    "_target_frame_from_mapping",
    "annotations",
    "assert_positions_by_rebalance_frame",
    "positions_by_rebalance_from_targets",
]

if TYPE_CHECKING:
    from quant_platform._portfolio.position_inputs import (
        Any,
        Mapping,
        _copy_target_frame,
        _target_frame_from_mapping,
        annotations,
        assert_positions_by_rebalance_frame,
        positions_by_rebalance_from_targets,
    )

sys.modules[__name__] = import_module("quant_platform._portfolio.position_inputs")
