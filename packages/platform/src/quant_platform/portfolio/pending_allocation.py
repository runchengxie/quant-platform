"""Legacy pending allocation with full Platform research validation.

Execution values and reservation mathematics belong to Engine. The old entry
points retain the complete sparse request validator and original optimizer.
"""

from quant_backtest_core.planning import pending_allocation as _core
from quant_backtest_core.planning.pending_allocation import (
    PendingAllocationEnvelope as PendingAllocationEnvelope,
)
from quant_backtest_core.planning.pending_allocation import (
    PendingAllocationResult as PendingAllocationResult,
)
from quant_backtest_core.planning.pending_allocation import (
    PendingAllocationState as PendingAllocationState,
)
from quant_backtest_core.planning.pending_allocation import (
    PendingOrder as PendingOrder,
)

from .engine_pending_adapter import PlatformPendingOptimizer
from .sparse_signed_optimization import (
    SparseSignedOptimizationRequest,
    SparseSignedOptimizer,
    _validate,
)


def pending_allocation_envelope(
    r: SparseSignedOptimizationRequest,
    state: PendingAllocationState,
    *,
    net_band: tuple[float, float],
) -> PendingAllocationEnvelope:
    """Validate the original full research request before execution reservations."""
    _validate(r)
    return _core.pending_allocation_envelope(r, state, net_band=net_band)


def solve_pending_allocation(
    optimizer: SparseSignedOptimizer,
    r: SparseSignedOptimizationRequest,
    state: PendingAllocationState,
    *,
    net_band: tuple[float, float],
) -> PendingAllocationResult:
    """Preserve the old optimizer call and its original successful result object."""
    return _core.solve_pending_allocation(
        PlatformPendingOptimizer(optimizer), r, state, net_band=net_band
    )
