from __future__ import annotations

from quant_execution_engine.broker.base import (
    BrokerAdapter,
    BrokerCapabilityMatrix,
    BrokerFillRecord,
    BrokerOrderRecord,
    BrokerOrderRequest,
    BrokerReconcileReport,
    ResolvedBrokerAccount,
)
from quant_execution_engine.models import Quote


class FakeAdapter(BrokerAdapter):
    backend_name = "fake"
    capabilities = BrokerCapabilityMatrix(
        name="fake",
        supports_live_submit=True,
        supports_cancel=True,
        supports_order_query=True,
        supports_open_order_listing=True,
        supports_reconcile=True,
    )

    def __init__(self) -> None:
        self.submit_calls = 0
        self.cancel_calls: list[str] = []
        self.orders: dict[str, BrokerOrderRecord] = {}

    def resolve_account(self, account_label: str | None = None) -> ResolvedBrokerAccount:
        label = account_label or "main"
        return ResolvedBrokerAccount(label=label)

    def get_quotes(self, symbols: list[str], *, include_depth: bool = False) -> dict[str, Quote]:
        return {
            symbol: Quote(
                symbol=symbol,
                price=10.0,
                timestamp="2026-04-14T00:00:00Z",
                bid=9.99 if include_depth else None,
                ask=10.01 if include_depth else None,
                daily_volume=100000.0,
            )
            for symbol in symbols
        }

    def submit_order(self, request: BrokerOrderRequest) -> BrokerOrderRecord:
        self.submit_calls += 1
        record = BrokerOrderRecord(
            broker_order_id=f"fake-{request.client_order_id}",
            symbol=request.symbol,
            side=request.side,
            quantity=request.quantity,
            status="NEW",
            broker_name=self.backend_name,
            account_label=request.account.label if request.account else "main",
            client_order_id=request.client_order_id,
        )
        self.orders[record.broker_order_id] = record
        return record

    def list_open_orders(
        self,
        account: ResolvedBrokerAccount | None = None,
    ) -> list[BrokerOrderRecord]:
        return list(self.orders.values())

    def get_order(
        self,
        broker_order_id: str,
        account: ResolvedBrokerAccount | None = None,
    ) -> BrokerOrderRecord:
        return self.orders[broker_order_id]

    def cancel_order(
        self,
        broker_order_id: str,
        account: ResolvedBrokerAccount | None = None,
    ) -> None:
        self.cancel_calls.append(broker_order_id)
        self.orders[broker_order_id].status = "CANCELED"

    def reconcile(
        self,
        account: ResolvedBrokerAccount | None = None,
    ) -> BrokerReconcileReport:
        resolved = account or self.resolve_account()
        return BrokerReconcileReport(
            broker_name=self.backend_name,
            account_label=resolved.label,
            open_orders=self.list_open_orders(resolved),
            fills=[],
        )


class FailingSubmitAdapter(FakeAdapter):
    def submit_order(self, request: BrokerOrderRequest) -> BrokerOrderRecord:
        raise RuntimeError("submit rejected by broker")


class HistoryAdapter(FakeAdapter):
    capabilities = BrokerCapabilityMatrix(
        name="history-fake",
        supports_live_submit=True,
        supports_cancel=True,
        supports_order_query=True,
        supports_open_order_listing=True,
        supports_order_history=True,
        supports_fill_history=True,
        supports_reconcile=True,
    )

    def __init__(self) -> None:
        super().__init__()
        self.fill_history: dict[str, list[BrokerFillRecord]] = {}

    def list_order_history(
        self,
        account: ResolvedBrokerAccount | None = None,
        *,
        symbol: str | None = None,
        broker_order_id: str | None = None,
    ) -> list[BrokerOrderRecord]:
        if broker_order_id is not None:
            record = self.orders.get(broker_order_id)
            return [record] if record is not None else []
        return list(self.orders.values())

    def list_fill_history(
        self,
        account: ResolvedBrokerAccount | None = None,
        *,
        symbol: str | None = None,
        broker_order_id: str | None = None,
    ) -> list[BrokerFillRecord]:
        if broker_order_id is not None:
            return list(self.fill_history.get(broker_order_id, []))
        records: list[BrokerFillRecord] = []
        for fills in self.fill_history.values():
            records.extend(fills)
        return records


class ClosedFillAdapter(FakeAdapter):
    def __init__(self) -> None:
        super().__init__()
        self.fill_available = False

    def submit_order(self, request: BrokerOrderRequest) -> BrokerOrderRecord:
        record = super().submit_order(request)
        record.status = "NEW"
        self.orders[record.broker_order_id] = record
        return record

    def get_order(
        self,
        broker_order_id: str,
        account: ResolvedBrokerAccount | None = None,
    ) -> BrokerOrderRecord:
        record = self.orders[broker_order_id]
        self.fill_available = True
        return BrokerOrderRecord(
            broker_order_id=record.broker_order_id,
            symbol=record.symbol,
            side=record.side,
            quantity=record.quantity,
            filled_quantity=record.quantity,
            remaining_quantity=0.0,
            status="FILLED",
            broker_name=record.broker_name,
            account_label=record.account_label,
            client_order_id=record.client_order_id,
            avg_fill_price=10.25,
        )

    def list_open_orders(
        self,
        account: ResolvedBrokerAccount | None = None,
    ) -> list[BrokerOrderRecord]:
        return []

    def list_fills(
        self,
        account: ResolvedBrokerAccount | None = None,
        *,
        broker_order_id: str | None = None,
    ) -> list[BrokerFillRecord]:
        assert broker_order_id is not None
        if not self.fill_available:
            return []
        record = self.orders[broker_order_id]
        return [
            BrokerFillRecord(
                fill_id=f"{broker_order_id}-fill",
                broker_order_id=broker_order_id,
                symbol=record.symbol,
                quantity=record.quantity,
                price=10.25,
                broker_name=self.backend_name,
                account_label=record.account_label,
                filled_at="2026-04-14T00:05:00Z",
            )
        ]

    def reconcile(
        self,
        account: ResolvedBrokerAccount | None = None,
    ) -> BrokerReconcileReport:
        resolved = account or self.resolve_account()
        return BrokerReconcileReport(
            broker_name=self.backend_name,
            account_label=resolved.label,
            open_orders=[],
            fills=[],
        )


class FillLookupErrorAdapter(FakeAdapter):
    def list_fills(
        self,
        account: ResolvedBrokerAccount | None = None,
        *,
        broker_order_id: str | None = None,
    ) -> list[BrokerFillRecord]:
        raise RuntimeError("fill lookup unavailable")


class RefreshLookupErrorAdapter(FakeAdapter):
    def list_open_orders(
        self,
        account: ResolvedBrokerAccount | None = None,
    ) -> list[BrokerOrderRecord]:
        return []

    def get_order(
        self,
        broker_order_id: str,
        account: ResolvedBrokerAccount | None = None,
    ) -> BrokerOrderRecord:
        raise RuntimeError("order refresh unavailable")


class PendingCancelRefreshAdapter(FakeAdapter):
    def __init__(self) -> None:
        super().__init__()
        self.pending_cancel_ids: set[str] = set()

    def cancel_order(
        self,
        broker_order_id: str,
        account: ResolvedBrokerAccount | None = None,
    ) -> None:
        self.cancel_calls.append(broker_order_id)
        self.pending_cancel_ids.add(broker_order_id)

    def get_order(
        self,
        broker_order_id: str,
        account: ResolvedBrokerAccount | None = None,
    ) -> BrokerOrderRecord:
        if broker_order_id in self.pending_cancel_ids:
            raise RuntimeError("cancel refresh unavailable")
        return super().get_order(broker_order_id, account)
