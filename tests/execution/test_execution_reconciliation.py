from __future__ import annotations

from pathlib import Path

import pytest

from quant_execution_engine.execution import (
    ExecutionStateStore,
    OrderLifecycleService,
)
from quant_execution_engine.models import Order
from quant_execution_engine.risk import RiskGateChain
from tests.execution._execution_foundation_fakes import (
    ClosedFillAdapter,
    FillLookupErrorAdapter,
    PendingCancelRefreshAdapter,
    RefreshLookupErrorAdapter,
)

pytestmark = pytest.mark.unit


def test_manual_reconcile_recovers_fill_for_closed_tracked_order(
    tmp_path: Path,
) -> None:
    adapter = ClosedFillAdapter()
    store = ExecutionStateStore(root_dir=tmp_path)
    service = OrderLifecycleService(
        adapter,
        state_store=store,
        risk_chain=RiskGateChain({}),
    )
    base_kwargs = {
        "account_label": "main",
        "dry_run": False,
        "target_source": "unit",
        "target_asof": "2026-04-14",
        "target_input_path": "tests/targets.json",
    }

    service.execute_orders(
        [Order(symbol="AAPL.US", quantity=10, side="BUY", price=10.0)],
        **base_kwargs,
    )

    outcome = service.reconcile(account_label="main")
    state = store.load("fake", "main")

    assert outcome.new_fill_events == 1
    assert outcome.refreshed_orders == 1
    assert outcome.changed_orders[0].after_status == "FILLED"
    assert outcome.changed_orders[0].new_fill_events == 1
    assert state.fill_events[0].broker_order_id.startswith("fake-child_")
    assert state.parent_orders[0].status == "FILLED"
    assert state.parent_orders[0].remaining_quantity == 0.0
    assert any(order.status == "FILLED" for order in state.broker_orders)


def test_manual_reconcile_warns_and_preserves_state_when_tracked_order_refresh_fails(
    tmp_path: Path,
) -> None:
    adapter = RefreshLookupErrorAdapter()
    store = ExecutionStateStore(root_dir=tmp_path)
    service = OrderLifecycleService(
        adapter,
        state_store=store,
        risk_chain=RiskGateChain({}),
    )

    result = service.execute_orders(
        [Order(symbol="AAPL.US", quantity=10, side="BUY", price=10.0)],
        account_label="main",
        dry_run=False,
        target_source="unit",
        target_asof="2026-04-14",
        target_input_path="tests/targets.json",
    )[0]

    outcome = service.reconcile(account_label="main")
    state = store.load("fake", "main")

    assert outcome.refreshed_orders == 0
    assert outcome.new_fill_events == 0
    assert outcome.report.warnings == [
        f"failed to refresh tracked order {result.broker_order_id}: order refresh unavailable"
    ]
    assert state.broker_orders[0].broker_order_id == result.broker_order_id
    assert state.child_orders[0].broker_order_id == result.broker_order_id


def test_manual_reconcile_warns_and_preserves_state_when_fill_lookup_fails(
    tmp_path: Path,
) -> None:
    adapter = FillLookupErrorAdapter()
    store = ExecutionStateStore(root_dir=tmp_path)
    service = OrderLifecycleService(
        adapter,
        state_store=store,
        risk_chain=RiskGateChain({}),
    )

    result = service.execute_orders(
        [Order(symbol="AAPL.US", quantity=10, side="BUY", price=10.0)],
        account_label="main",
        dry_run=False,
        target_source="unit",
        target_asof="2026-04-14",
        target_input_path="tests/targets.json",
    )[0]

    outcome = service.reconcile(account_label="main")
    state = store.load("fake", "main")

    assert outcome.refreshed_orders == 0
    assert outcome.new_fill_events == 0
    assert outcome.report.warnings == [
        f"failed to load fills for tracked order {result.broker_order_id}: fill lookup unavailable"
    ]
    assert state.broker_orders[0].broker_order_id == result.broker_order_id
    assert state.fill_events == []


def test_submit_success_survives_fill_lookup_failure(tmp_path: Path) -> None:
    adapter = FillLookupErrorAdapter()
    service = OrderLifecycleService(
        adapter,
        state_store=ExecutionStateStore(root_dir=tmp_path),
        risk_chain=RiskGateChain({}),
    )

    results = service.execute_orders(
        [Order(symbol="AAPL.US", quantity=10, side="BUY", price=10.0)],
        account_label="main",
        dry_run=False,
        target_source="unit",
        target_asof="2026-04-14",
        target_input_path="tests/targets.json",
    )

    assert results[0].status == "SUCCESS"
    assert results[0].broker_order_id is not None


def test_cancel_order_records_pending_cancel_when_refresh_fails(tmp_path: Path) -> None:
    adapter = PendingCancelRefreshAdapter()
    store = ExecutionStateStore(root_dir=tmp_path)
    service = OrderLifecycleService(
        adapter,
        state_store=store,
        risk_chain=RiskGateChain({}),
    )

    result = service.execute_orders(
        [
            Order(
                symbol="AAPL.US",
                quantity=10,
                side="BUY",
                price=10.0,
                order_type="LIMIT",
            )
        ],
        account_label="main",
        dry_run=False,
        target_source="unit",
        target_asof="2026-04-14",
        target_input_path="tests/targets.json",
    )[0]

    outcome = service.cancel_order(
        account_label="main",
        order_ref=str(result.broker_order_id),
    )
    state = store.load("fake", "main")

    assert outcome.status == "PENDING_CANCEL"
    assert outcome.warnings == [
        "cancel submitted but post-cancel refresh failed: cancel refresh unavailable"
    ]
    assert state.broker_orders[0].status == "PENDING_CANCEL"
    assert state.child_orders[0].status == "PENDING_CANCEL"


def test_reprice_rejects_pending_cancel_order(tmp_path: Path) -> None:
    adapter = PendingCancelRefreshAdapter()
    store = ExecutionStateStore(root_dir=tmp_path)
    service = OrderLifecycleService(
        adapter,
        state_store=store,
        risk_chain=RiskGateChain({}),
    )

    result = service.execute_orders(
        [
            Order(
                symbol="AAPL.US",
                quantity=10,
                side="BUY",
                price=10.0,
                order_type="LIMIT",
            )
        ],
        account_label="main",
        dry_run=False,
        target_source="unit",
        target_asof="2026-04-14",
        target_input_path="tests/targets.json",
    )[0]
    service.cancel_order(
        account_label="main",
        order_ref=str(result.broker_order_id),
    )

    with pytest.raises(ValueError, match="pending cancel"):
        service.reprice_order(
            account_label="main",
            order_ref=str(result.broker_order_id),
            limit_price=9.5,
        )
