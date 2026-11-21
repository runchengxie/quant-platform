"""Versioned, descriptive cross-sectional signal diagnostics.

Input labels are realized decimal returns. Scores need not be calibrated.
No function estimates execution costs, chooses optimal K or verifies PIT/OOS.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

import pandas as pd

from ._signal_reliability_common import BlockStatistics, SignalReliabilityResult
from ._signal_reliability_conditional import conditional_factor_profile
from ._signal_reliability_tail import compute_tail


def tail_return_profile(
    panel: pd.DataFrame,
    *,
    score_col: str,
    target_col: str,
    ks: Sequence[int],
    statistics: BlockStatistics,
    date_col: str = "trade_date",
    symbol_col: str = "symbol",
    ascending: bool = False,
    provenance: Mapping[str, Any] | None = None,
) -> SignalReliabilityResult:
    """Disjoint rank-band and cumulative Top K equal-weight label returns."""
    return compute_tail(
        panel,
        score_col=score_col,
        target_col=target_col,
        ks=ks,
        statistics=statistics,
        date_col=date_col,
        symbol_col=symbol_col,
        ascending=ascending,
        provenance=provenance,
    )


def marginal_alpha_profile(
    panel: pd.DataFrame,
    *,
    score_col: str,
    target_col: str,
    ks: Sequence[int],
    statistics: BlockStatistics,
    date_col: str = "trade_date",
    symbol_col: str = "symbol",
    ascending: bool = False,
    provenance: Mapping[str, Any] | None = None,
) -> SignalReliabilityResult:
    """Paired Top K minus Next K and Top K minus Top 2K label returns."""
    return compute_tail(
        panel,
        score_col=score_col,
        target_col=target_col,
        ks=ks,
        statistics=statistics,
        date_col=date_col,
        symbol_col=symbol_col,
        ascending=ascending,
        provenance=provenance,
        marginal=True,
    )


__all__ = [
    "BlockStatistics",
    "SignalReliabilityResult",
    "conditional_factor_profile",
    "marginal_alpha_profile",
    "tail_return_profile",
]
