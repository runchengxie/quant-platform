"""Module alias preserving implementation identity during compatibility migration."""

import sys
from importlib import import_module
from typing import TYPE_CHECKING

__all__ = [
    "INCUMBENT_REQUALIFICATION_SCHEMA",
    "_INTERNAL_COLUMNS",
    "Any",
    "Collection",
    "Counter",
    "IncumbentRequalificationConfig",
    "IncumbentRequalificationPolicy",
    "IncumbentRequalificationReceipt",
    "IncumbentRequalificationResult",
    "Literal",
    "Mapping",
    "RankUniverse",
    "_Prepared",
    "_can_add",
    "_prepare",
    "_rank_eligibility",
    "_ranked_symbols",
    "_replaceable_incumbents",
    "_select_symbols",
    "_truthy",
    "annotations",
    "asdict",
    "cast",
    "dataclass",
    "select_incumbent_requalified_portfolio",
]

if TYPE_CHECKING:
    from quant_platform._portfolio.incumbent_requalification import (
        _INTERNAL_COLUMNS,
        INCUMBENT_REQUALIFICATION_SCHEMA,
        Any,
        Collection,
        Counter,
        IncumbentRequalificationConfig,
        IncumbentRequalificationPolicy,
        IncumbentRequalificationReceipt,
        IncumbentRequalificationResult,
        Literal,
        Mapping,
        RankUniverse,
        _can_add,
        _prepare,
        _Prepared,
        _rank_eligibility,
        _ranked_symbols,
        _replaceable_incumbents,
        _select_symbols,
        _truthy,
        annotations,
        asdict,
        cast,
        dataclass,
        select_incumbent_requalified_portfolio,
    )

sys.modules[__name__] = import_module("quant_platform._portfolio.incumbent_requalification")
