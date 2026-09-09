"""Deterministic order lifecycle transitions and invariants."""

from __future__ import annotations

from decimal import Decimal

from ._domain_enums import ExecutionEventType, OrderStatus


class OrderLifecycleError(ValueError):
    """Raised when an execution event violates the order state machine."""


_TRANSITIONS: dict[tuple[OrderStatus, ExecutionEventType], OrderStatus] = {
    (OrderStatus.PENDING, ExecutionEventType.ORDER_SUBMITTED): OrderStatus.PENDING_NEW,
    (OrderStatus.PENDING_NEW, ExecutionEventType.ORDER_ACKNOWLEDGED): OrderStatus.ACCEPTED,
    (OrderStatus.NEW, ExecutionEventType.ORDER_ACKNOWLEDGED): OrderStatus.ACCEPTED,
    (OrderStatus.ACCEPTED, ExecutionEventType.PARTIALLY_FILLED): OrderStatus.PARTIALLY_FILLED,
    (OrderStatus.PARTIALLY_FILLED, ExecutionEventType.PARTIALLY_FILLED): (
        OrderStatus.PARTIALLY_FILLED
    ),
    (OrderStatus.ACCEPTED, ExecutionEventType.FILLED): OrderStatus.FILLED,
    (OrderStatus.PARTIALLY_FILLED, ExecutionEventType.FILLED): OrderStatus.FILLED,
    (OrderStatus.ACCEPTED, ExecutionEventType.CANCELLED): OrderStatus.CANCELLED,
    (OrderStatus.PARTIALLY_FILLED, ExecutionEventType.CANCELLED): OrderStatus.CANCELLED,
    (OrderStatus.ACCEPTED, ExecutionEventType.EXPIRED): OrderStatus.EXPIRED,
    (OrderStatus.PARTIALLY_FILLED, ExecutionEventType.EXPIRED): OrderStatus.EXPIRED,
    (OrderStatus.PENDING_NEW, ExecutionEventType.REJECTED): OrderStatus.REJECTED,
    (OrderStatus.ACCEPTED, ExecutionEventType.REJECTED): OrderStatus.REJECTED,
}

_TERMINAL = frozenset(
    {
        OrderStatus.FILLED,
        OrderStatus.CANCELLED,
        OrderStatus.REJECTED,
        OrderStatus.EXPIRED,
        OrderStatus.FAILED,
    }
)


def validate_order_transition(
    current: OrderStatus,
    event: ExecutionEventType,
    *,
    filled_quantity: Decimal = Decimal("0"),
    order_quantity: Decimal | None = None,
) -> OrderStatus:
    """Return the next status after validating a broker event."""
    if not isinstance(current, OrderStatus) or not isinstance(event, ExecutionEventType):
        raise TypeError("current and event must use typed execution enums")
    if filled_quantity < 0:
        raise OrderLifecycleError("filled_quantity cannot be negative")
    if order_quantity is not None and (order_quantity <= 0 or filled_quantity > order_quantity):
        raise OrderLifecycleError("filled_quantity must be within order_quantity")
    if current in _TERMINAL:
        raise OrderLifecycleError(f"cannot apply {event.value} to terminal status {current.value}")
    try:
        return _TRANSITIONS[(current, event)]
    except KeyError as exc:
        raise OrderLifecycleError(
            f"invalid order transition: {current.value} + {event.value}"
        ) from exc
