"""Module alias preserving implementation identity during compatibility migration."""

import sys
from importlib import import_module
from typing import TYPE_CHECKING

__all__ = [
    "MaxNewNamesShortfallPolicy",
    "SelectionConstraints",
    "_blocked_by_group_cap",
    "_carry_previous_holdings",
    "_new_name_budget_exhausted",
    "_passes_entry_constraints",
    "_record_group_selection",
    "_resolve_selection_shortfall",
    "_select_ranked_holdings",
    "annotations",
    "filter_entry_eligible_symbols",
    "select_candidate_holdings",
]

if TYPE_CHECKING:
    from quant_platform._portfolio.holding_selection import (
        MaxNewNamesShortfallPolicy,
        SelectionConstraints,
        _blocked_by_group_cap,
        _carry_previous_holdings,
        _new_name_budget_exhausted,
        _passes_entry_constraints,
        _record_group_selection,
        _resolve_selection_shortfall,
        _select_ranked_holdings,
        annotations,
        filter_entry_eligible_symbols,
        select_candidate_holdings,
    )

sys.modules[__name__] = import_module("quant_platform._portfolio.holding_selection")
