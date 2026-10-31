"""Module alias preserving implementation identity during compatibility migration."""

import sys
from importlib import import_module
from typing import TYPE_CHECKING

__all__ = [
    "PORTFOLIO_POLICY_SCHEMA",
    "DailyWatch20PortfolioPolicy",
    "annotations",
    "asdict",
    "dataclass",
]

if TYPE_CHECKING:
    from quant_platform._portfolio.daily_watch20_policy import (
        PORTFOLIO_POLICY_SCHEMA,
        DailyWatch20PortfolioPolicy,
        annotations,
        asdict,
        dataclass,
    )

sys.modules[__name__] = import_module("quant_platform._portfolio.daily_watch20_policy")
