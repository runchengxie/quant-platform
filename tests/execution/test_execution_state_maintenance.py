from __future__ import annotations

from pathlib import Path

import pytest

from quant_execution_engine.broker.base import (
    BrokerOrderRecord,
)
from quant_execution_engine.execution import (
    ExecutionFillEvent,
    ExecutionState,
    ExecutionStateStore,
    OrderLifecycleService,
)
from quant_execution_engine.models import Order
from quant_execution_engine.risk import RiskGateChain
from quant_execution_engine.state_tools import StateMaintenanceService
from tests.execution._execution_foundation_fakes import (
    FailingSubmitAdapter,
    FakeAdapter,
)

pytestmark = pytest.mark.unit


def test_state_doctor_reports_duplicate_fill_and_orphan_broker_order(
    tmp_path: Path,
) -> None:
    store = ExecutionStateStore(root_dir=tmp_path)
    state = ExecutionState(broker_name="fake", account_label="main")
    state.broker_orders = [
        BrokerOrderRecord(
            broker_order_id="orphan-broker-order",
            symbol="AAPL.US",
            side="BUY",
            quantity=1,
            status="CANCELED",
            broker_name="fake",
            account_label="main",
        )
    ]
    state.fill_events = [
        ExecutionFillEvent(
            fill_id="fill-1",
            intent_id="intent-1",
            parent_order_id="parent-1",
            broker_order_id="missing-broker-order",
            symbol="AAPL.US",
            quantity=1,
            price=10.0,
            broker_name="fake",
            account_label="main",
        ),
        ExecutionFillEvent(
            fill_id="fill-1",
            intent_id="intent-1",
            parent_order_id="parent-1",
            broker_order_id="missing-broker-order",
            symbol="AAPL.US",
            quantity=1,
            price=10.0,
            broker_name="fake",
            account_label="main",
        ),
    ]
    store.save(state)

    result = StateMaintenanceService(state_store=store).doctor(
        broker_name="fake",
        account_label="main",
    )

    codes = {issue.code for issue in result.issues}
    assert "ORPHAN_TERMINAL_BROKER_ORDER" in codes
    assert "DUPLICATE_FILL_ID" in codes
    assert "ORPHAN_FILL_EVENT" in codes


def test_state_doctor_reports_parent_aggregate_mismatch(tmp_path: Path) -> None:
    adapter = FakeAdapter()
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
    state = store.load("fake", "main")
    state.parent_orders[0].filled_quantity = 0.0
    state.parent_orders[0].remaining_quantity = 10.0
    state.parent_orders[0].status = "PENDING"
    state.broker_orders[0].filled_quantity = 4.0
    state.broker_orders[0].remaining_quantity = 6.0
    state.broker_orders[0].status = "PARTIALLY_FILLED"
    state.child_orders[0].status = "PARTIALLY_FILLED"
    store.save(state)
    adapter.orders[str(result.broker_order_id)].filled_quantity = 4.0
    adapter.orders[str(result.broker_order_id)].remaining_quantity = 6.0
    adapter.orders[str(result.broker_order_id)].status = "PARTIALLY_FILLED"

    diagnosis = StateMaintenanceService(state_store=store).doctor(
        broker_name="fake",
        account_label="main",
    )

    codes = {issue.code for issue in diagnosis.issues}
    assert "PARENT_AGGREGATE_MISMATCH" in codes
    assert "PARENT_STATUS_MISMATCH" in codes


def test_state_prune_previews_and_applies_old_terminal_records(tmp_path: Path) -> None:
    adapter = FakeAdapter()
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
    service.cancel_order(account_label="main", order_ref=str(result.broker_order_id))
    state = store.load("fake", "main")
    state.parent_orders[0].updated_at = "2000-01-01T00:00:00+00:00"
    store.save(state)

    preview = StateMaintenanceService(state_store=store).prune(
        broker_name="fake",
        account_label="main",
        older_than_days=30,
        apply=False,
    )
    applied = StateMaintenanceService(state_store=store).prune(
        broker_name="fake",
        account_label="main",
        older_than_days=30,
        apply=True,
    )
    refreshed = store.load("fake", "main")

    assert preview.parent_orders_removed == 1
    assert applied.parent_orders_removed == 1
    assert refreshed.parent_orders == []
    assert refreshed.child_orders == []


def test_state_repair_clears_kill_switch_and_dedupes_fills(tmp_path: Path) -> None:
    store = ExecutionStateStore(root_dir=tmp_path)
    state = ExecutionState(broker_name="fake", account_label="main")
    state.kill_switch_active = True
    state.kill_switch_reason = "manual test"
    state.consecutive_failures = 2
    state.broker_orders = [
        BrokerOrderRecord(
            broker_order_id="orphan-broker-order",
            symbol="AAPL.US",
            side="BUY",
            quantity=1,
            status="CANCELED",
            broker_name="fake",
            account_label="main",
        )
    ]
    state.fill_events = [
        ExecutionFillEvent(
            fill_id="fill-1",
            intent_id="intent-1",
            parent_order_id="parent-1",
            broker_order_id="missing-broker-order",
            symbol="AAPL.US",
            quantity=1,
            price=10.0,
            broker_name="fake",
            account_label="main",
        ),
        ExecutionFillEvent(
            fill_id="fill-1",
            intent_id="intent-1",
            parent_order_id="parent-1",
            broker_order_id="missing-broker-order",
            symbol="AAPL.US",
            quantity=1,
            price=10.0,
            broker_name="fake",
            account_label="main",
        ),
    ]
    store.save(state)

    result = StateMaintenanceService(state_store=store).repair(
        broker_name="fake",
        account_label="main",
        clear_kill_switch=True,
        dedupe_fills=True,
        drop_orphan_fills=True,
        drop_orphan_terminal_broker_orders=True,
        recompute_parent_aggregates=False,
    )
    refreshed = store.load("fake", "main")

    assert result.cleared_kill_switch is True
    assert result.duplicate_fills_removed == 1
    assert result.orphan_fills_removed == 1
    assert result.orphan_terminal_broker_orders_removed == 1
    assert refreshed.kill_switch_active is False
    assert refreshed.fill_events == []
    assert refreshed.broker_orders == []


def test_state_repair_recomputes_parent_aggregates(tmp_path: Path) -> None:
    adapter = FakeAdapter()
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
    state = store.load("fake", "main")
    state.parent_orders[0].filled_quantity = 0.0
    state.parent_orders[0].remaining_quantity = 10.0
    state.parent_orders[0].status = "PENDING"
    state.broker_orders[0].filled_quantity = 4.0
    state.broker_orders[0].remaining_quantity = 6.0
    state.broker_orders[0].status = "PARTIALLY_FILLED"
    state.child_orders[0].status = "PARTIALLY_FILLED"
    store.save(state)
    adapter.orders[str(result.broker_order_id)].filled_quantity = 4.0
    adapter.orders[str(result.broker_order_id)].remaining_quantity = 6.0
    adapter.orders[str(result.broker_order_id)].status = "PARTIALLY_FILLED"

    repaired = StateMaintenanceService(state_store=store).repair(
        broker_name="fake",
        account_label="main",
        clear_kill_switch=False,
        dedupe_fills=False,
        drop_orphan_fills=False,
        drop_orphan_terminal_broker_orders=False,
        recompute_parent_aggregates=True,
    )
    refreshed = store.load("fake", "main")

    assert repaired.parent_aggregates_recomputed == 1
    assert refreshed.parent_orders[0].filled_quantity == 4.0
    assert refreshed.parent_orders[0].remaining_quantity == 6.0
    assert refreshed.parent_orders[0].status == "PARTIALLY_FILLED"


def test_list_exception_orders_includes_local_blocked_and_failed(
    tmp_path: Path,
) -> None:
    store = ExecutionStateStore(root_dir=tmp_path)
    blocked_service = OrderLifecycleService(
        FakeAdapter(),
        state_store=store,
        risk_chain=RiskGateChain({"max_qty_per_order": 5}),
    )
    failed_service = OrderLifecycleService(
        FailingSubmitAdapter(),
        state_store=store,
        risk_chain=RiskGateChain({}),
    )

    blocked_service.execute_orders(
        [Order(symbol="AAPL.US", quantity=10, side="BUY", price=10.0)],
        account_label="main",
        dry_run=False,
        target_source="unit",
        target_asof="2026-04-14",
        target_input_path="tests/targets.json",
    )
    failed_service.execute_orders(
        [Order(symbol="MSFT.US", quantity=5, side="BUY", price=10.0)],
        account_label="main",
        dry_run=False,
        target_source="unit-submit-failure",
        target_asof="2026-04-14",
        target_input_path="tests/targets-submit-failure.json",
    )

    records = failed_service.list_exception_orders(account_label="main")

    assert {record.status for record in records} >= {"BLOCKED", "FAILED"}
    blocked = next(record for record in records if record.status == "BLOCKED")
    failed = next(record for record in records if record.status == "FAILED")
    assert blocked.source == "local"
    assert blocked.message is not None
    assert failed.source == "local"
    assert failed.message == "submit rejected by broker"
