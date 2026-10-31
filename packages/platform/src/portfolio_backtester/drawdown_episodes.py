"""Module alias preserving implementation identity during compatibility migration."""

import sys
from importlib import import_module
from typing import TYPE_CHECKING

__all__ = ["_COLUMNS", "drawdown_episodes"]

if TYPE_CHECKING:
    from quant_platform._portfolio.drawdown_episodes import (
        _COLUMNS,
        drawdown_episodes,
    )

sys.modules[__name__] = import_module("quant_platform._portfolio.drawdown_episodes")
