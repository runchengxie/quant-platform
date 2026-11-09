"""Bridge Engine reservations to the Platform-owned sparse research optimizer."""

from dataclasses import replace
from typing import cast

import numpy as np
from quant_backtest_core.planning.pending_allocation import PendingAllocationEnvelope
from quant_backtest_core.planning.pending_protocol import PendingRequest

from quant_platform._portfolio.signed_optimization import SignedOptimizationResult

from .sparse_signed_optimization import (
    SparseSignedOptimizationRequest,
    SparseSignedOptimizer,
    _validate,
)


class PlatformPendingOptimizer:
    """Retain full risk validation, solver reuse and the actual optimizer result."""

    def __init__(self, optimizer: SparseSignedOptimizer) -> None:
        self.optimizer = optimizer

    def validate(self, request: PendingRequest) -> None:
        _validate(cast(SparseSignedOptimizationRequest, request))

    def solve_pending(
        self,
        request: PendingRequest,
        *,
        envelope: PendingAllocationEnvelope,
        cash_limit: tuple[float, np.ndarray],
    ) -> SignedOptimizationResult:
        tightened = replace(
            cast(SparseSignedOptimizationRequest, request),
            gross_limit=envelope.gross_limit,
            lower_bounds=envelope.lower_bounds,
            upper_bounds=envelope.upper_bounds,
            factor_bounds=envelope.factor_bounds,
        )
        return self.optimizer._solve(tightened, cash_limit=cash_limit)
