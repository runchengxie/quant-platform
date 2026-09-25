"""Broker integrations."""

from typing import TYPE_CHECKING, Any

from .base import (
    BrokerAdapter,
    BrokerCapabilityMatrix,
    BrokerError,
    BrokerImportError,
    BrokerOrderRecord,
    BrokerOrderRequest,
    BrokerValidationError,
    ResolvedBrokerAccount,
)
from .factory import (
    get_account_config,
    get_broker_adapter,
    get_broker_capabilities,
    is_ibkr_broker,
    is_longport_broker,
    is_paper_broker,
    peek_broker_name,
    resolve_broker_name,
    resolve_default_account_label,
)

if TYPE_CHECKING:
    from .mock_sim import MockSimBrokerAdapter

__all__ = [
    "BrokerAdapter",
    "BrokerCapabilityMatrix",
    "BrokerError",
    "BrokerImportError",
    "BrokerOrderRecord",
    "BrokerOrderRequest",
    "BrokerValidationError",
    "MockSimBrokerAdapter",
    "ResolvedBrokerAccount",
    "get_account_config",
    "get_broker_adapter",
    "get_broker_capabilities",
    "is_ibkr_broker",
    "is_longport_broker",
    "is_paper_broker",
    "peek_broker_name",
    "resolve_broker_name",
    "resolve_default_account_label",
]


def __getattr__(name: str) -> Any:
    if name == "MockSimBrokerAdapter":
        from .mock_sim import MockSimBrokerAdapter

        return MockSimBrokerAdapter
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
