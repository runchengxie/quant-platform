"""Module alias preserving implementation identity during compatibility migration."""

import sys
from importlib import import_module
from typing import TYPE_CHECKING

__all__ = [
    "Any",
    "ArtifactRef",
    "Decimal",
    "Mapping",
    "ResearchClock",
    "USDFXObservation",
    "USDInstrument",
    "USDModeledExecutionPrice",
    "USDPriceObservation",
    "USDRebalanceDecision",
    "USDReplayConfig",
    "USDReplayRequest",
    "USDReplayResult",
    "USDValidationError",
    "dataclass",
    "date",
    "datetime",
    "timedelta",
]

if TYPE_CHECKING:
    from quant_platform._portfolio.usd_ledger_models import (
        Any,
        ArtifactRef,
        Decimal,
        Mapping,
        ResearchClock,
        USDFXObservation,
        USDInstrument,
        USDModeledExecutionPrice,
        USDPriceObservation,
        USDRebalanceDecision,
        USDReplayConfig,
        USDReplayRequest,
        USDReplayResult,
        USDValidationError,
        dataclass,
        date,
        datetime,
        timedelta,
    )

sys.modules[__name__] = import_module("quant_platform._portfolio.usd_ledger_models")
