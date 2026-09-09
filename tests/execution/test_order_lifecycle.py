from decimal import Decimal

import pytest

from quant_execution_engine.domain import (
    ExecutionEventType,
    OrderLifecycleError,
    OrderStatus,
    validate_order_transition,
)


def test_order_lifecycle_accepts_partial_then_fill() -> None:
    status = validate_order_transition(OrderStatus.PENDING, ExecutionEventType.ORDER_SUBMITTED)
    status = validate_order_transition(status, ExecutionEventType.ORDER_ACKNOWLEDGED)
    status = validate_order_transition(
        status,
        ExecutionEventType.PARTIALLY_FILLED,
        filled_quantity=Decimal("4"),
        order_quantity=Decimal("10"),
    )
    assert validate_order_transition(
        status,
        ExecutionEventType.FILLED,
        filled_quantity=Decimal("10"),
        order_quantity=Decimal("10"),
    ) is OrderStatus.FILLED


def test_order_lifecycle_rejects_terminal_and_overfill() -> None:
    with pytest.raises(OrderLifecycleError):
        validate_order_transition(OrderStatus.FILLED, ExecutionEventType.CANCELLED)
    with pytest.raises(OrderLifecycleError, match="within order_quantity"):
        validate_order_transition(
            OrderStatus.ACCEPTED,
            ExecutionEventType.FILLED,
            filled_quantity=Decimal("11"),
            order_quantity=Decimal("10"),
        )
