"""Immutable policy-visible minute account contract."""

from collections.abc import Mapping
from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True)
class MinuteDecisionState:
    """Synchronous delivered account, strictly before the decision-clock bar.

    No exchange-report delay is modeled. Raw marks may be stale: consumers must
    inspect mark_times. Pending orders remain live until entry supersession.
    """

    time: pd.Timestamp
    cash: float
    nav: float
    holdings: Mapping
    marks: Mapping
    mark_times: Mapping
    pending_orders: tuple
    cash_receivable: float
    stock_receivable_value: float
    locked_symbols: tuple[str, ...] = ()
    quantity_locks: tuple = ()
