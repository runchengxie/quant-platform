from __future__ import annotations

from pathlib import Path

import pytest

from quant_execution_engine.broker.base import (
    BrokerFillRecord,
)
from quant_execution_engine.execution import (
    ExecutionOrderTrace,
    ExecutionStateStore,
    OrderLifecycleService,
)
from quant_execution_engine.models import Order
from quant_execution_engine.renderers.table import (
    render_order_trace,
)
from quant_execution_engine.risk import RiskGateChain
from tests.execution._execution_foundation_fakes import (
    FakeAdapter,
    HistoryAdapter,
)

pytestmark = pytest.mark.unit


def test_get_order_trace_merges_local_attempts_and_broker_history(
    tmp_path: Path,
) -> None:
    adapter = HistoryAdapter()
    store = ExecutionStateStore(root_dir=tmp_path)
    service = OrderLifecycleService(
        adapter,
        state_store=store,
        risk_chain=RiskGateChain({}),
    )
    base_kwargs = {
        "account_label": "main",
        "dry_run": False,
        "target_source": "trace-test",
        "target_asof": "2026-04-19",
        "target_input_path": "outputs/targets/trace.json",
    }

    original = service.execute_orders(
        [
            Order(
                symbol="AAPL.US",
                quantity=10,
                side="BUY",
                price=10.0,
                order_type="LIMIT",
            )
        ],
        **base_kwargs,
    )[0]
    original_order_id = str(original.broker_order_id)
    adapter.fill_history[original_order_id] = [
        BrokerFillRecord(
            fill_id="fill-old",
            broker_order_id=original_order_id,
            symbol="AAPL.US",
            quantity=4.0,
            price=10.0,
            broker_name=adapter.backend_name,
            account_label="main",
            filled_at="2026-04-19T00:00:01+00:00",
        )
    ]

    repriced = service.reprice_order(
        account_label="main",
        order_ref=original_order_id,
        limit_price=9.5,
    )
    new_order_id = str(repriced.broker_order_id)
    adapter.fill_history[new_order_id] = [
        BrokerFillRecord(
            fill_id="fill-new",
            broker_order_id=new_order_id,
            symbol="AAPL.US",
            quantity=6.0,
            price=9.5,
            broker_name=adapter.backend_name,
            account_label="main",
            filled_at="2026-04-19T00:00:02+00:00",
        )
    ]

    trace = service.get_order_trace(account_label="main", order_ref=new_order_id)

    assert isinstance(trace, ExecutionOrderTrace)
    assert trace.parent is not None
    assert len(trace.child_orders) == 2
    assert [child.attempt for child in trace.child_orders] == [1, 2]
    assert {record.broker_order_id for record in trace.tracked_broker_orders} == {
        original_order_id,
        new_order_id,
    }
    assert {record.broker_order_id for record in trace.broker_history_orders} == {
        original_order_id,
        new_order_id,
    }
    assert {fill.fill_id for fill in trace.broker_history_fills} == {
        "fill-old",
        "fill-new",
    }
    assert trace.warnings == []

    rendered = render_order_trace(trace)

    assert "Local Child Attempts: 2" in rendered
    assert "Broker-side Order History: 2" in rendered
    assert "Broker-side Fill History: 2" in rendered
    assert original_order_id in rendered
    assert new_order_id in rendered


def test_get_order_trace_reports_unavailable_broker_history(tmp_path: Path) -> None:
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
        target_source="trace-test",
        target_asof="2026-04-19",
        target_input_path="outputs/targets/trace.json",
    )[0]

    trace = service.get_order_trace(account_label="main", order_ref=str(result.broker_order_id))

    assert any(
        "does not support broker-side order history" in warning for warning in trace.warnings
    )
    assert any("does not support broker-side fill history" in warning for warning in trace.warnings)


def test_retry_stale_orders_only_retries_eligible_open_orders(tmp_path: Path) -> None:
    adapter = FakeAdapter()
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

    stale = service.execute_orders(
        [Order(symbol="AAPL.US", quantity=10, side="BUY", price=10.0)],
        **base_kwargs,
    )[0]
    fresh = service.execute_orders(
        [Order(symbol="MSFT.US", quantity=5, side="BUY", price=10.0)],
        **base_kwargs,
    )[0]
    state = store.load("fake", "main")
    for broker_order in state.broker_orders:
        if broker_order.broker_order_id == stale.broker_order_id:
            broker_order.updated_at = "2000-01-01T00:00:00+00:00"
            broker_order.submitted_at = "2000-01-01T00:00:00+00:00"
    store.save(state)

    outcome = service.retry_stale_orders(account_label="main", older_than_minutes=5)
    refreshed_state = store.load("fake", "main")

    assert outcome.targeted_orders == 1
    assert len(outcome.cancel_results) == 1
    assert len(outcome.retry_results) == 1
    assert outcome.cancel_results[0].broker_order_id == stale.broker_order_id
    assert outcome.retry_results[0].new_child_order_id.endswith("_2")
    assert adapter.cancel_calls.count(str(stale.broker_order_id)) == 1
    assert adapter.cancel_calls.count(str(fresh.broker_order_id)) == 0
    assert adapter.submit_calls == 3
    assert len(refreshed_state.child_orders) == 3


def test_retry_rejects_partially_filled_order(tmp_path: Path) -> None:
    adapter = FakeAdapter()
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

    result = service.execute_orders(
        [Order(symbol="AAPL.US", quantity=10, side="BUY", price=10.0)],
        **base_kwargs,
    )[0]
    state = store.load("fake", "main")
    state.parent_orders[0].filled_quantity = 1.0
    state.parent_orders[0].remaining_quantity = 9.0
    state.parent_orders[0].status = "CANCELED"
    state.child_orders[0].status = "CANCELED"
    state.broker_orders[0].filled_quantity = 1.0
    state.broker_orders[0].remaining_quantity = 9.0
    state.broker_orders[0].status = "CANCELED"
    store.save(state)

    with pytest.raises(ValueError, match="partially filled"):
        service.retry_order(
            account_label="main",
            order_ref=str(result.broker_order_id),
        )


def test_cancel_rest_on_partially_filled_open_order(tmp_path: Path) -> None:
    adapter = FakeAdapter()
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

    result = service.execute_orders(
        [Order(symbol="AAPL.US", quantity=10, side="BUY", price=10.0)],
        **base_kwargs,
    )[0]
    state = store.load("fake", "main")
    state.parent_orders[0].filled_quantity = 1.0
    state.parent_orders[0].remaining_quantity = 9.0
    state.parent_orders[0].status = "PARTIALLY_FILLED"
    state.child_orders[0].status = "PARTIALLY_FILLED"
    state.broker_orders[0].filled_quantity = 1.0
    state.broker_orders[0].remaining_quantity = 9.0
    state.broker_orders[0].status = "PARTIALLY_FILLED"
    store.save(state)
    adapter.orders[str(result.broker_order_id)].filled_quantity = 1.0
    adapter.orders[str(result.broker_order_id)].remaining_quantity = 9.0
    adapter.orders[str(result.broker_order_id)].status = "PARTIALLY_FILLED"

    outcome = service.cancel_remaining_order(
        account_label="main",
        order_ref=str(result.broker_order_id),
    )
    refreshed = store.load("fake", "main")

    assert outcome.status == "CANCELED"
    assert refreshed.broker_orders[0].status == "CANCELED"
    assert refreshed.parent_orders[0].status == "PARTIALLY_FILLED"


def test_resume_remaining_order_creates_new_child_attempt(tmp_path: Path) -> None:
    adapter = FakeAdapter()
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

    result = service.execute_orders(
        [Order(symbol="AAPL.US", quantity=10, side="BUY", price=10.0)],
        **base_kwargs,
    )[0]
    state = store.load("fake", "main")
    state.parent_orders[0].filled_quantity = 1.0
    state.parent_orders[0].remaining_quantity = 9.0
    state.parent_orders[0].status = "PARTIALLY_FILLED"
    state.child_orders[0].status = "CANCELED"
    state.broker_orders[0].filled_quantity = 1.0
    state.broker_orders[0].remaining_quantity = 9.0
    state.broker_orders[0].status = "CANCELED"
    store.save(state)
    adapter.orders[str(result.broker_order_id)].filled_quantity = 1.0
    adapter.orders[str(result.broker_order_id)].remaining_quantity = 9.0
    adapter.orders[str(result.broker_order_id)].status = "CANCELED"

    outcome = service.resume_remaining_order(
        account_label="main",
        order_ref=str(result.broker_order_id),
    )
    refreshed = store.load("fake", "main")

    assert outcome.submitted_quantity == 9.0
    assert outcome.new_child_order_id.endswith("_2")
    assert outcome.broker_status == "NEW"
    assert adapter.submit_calls == 2
    assert refreshed.child_orders[-1].quantity == 9.0


def test_resume_remaining_rejects_stale_child_reference_when_newer_attempt_exists(
    tmp_path: Path,
) -> None:
    adapter = FakeAdapter()
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

    result = service.execute_orders(
        [Order(symbol="AAPL.US", quantity=10, side="BUY", price=10.0)],
        **base_kwargs,
    )[0]
    state = store.load("fake", "main")
    state.parent_orders[0].filled_quantity = 1.0
    state.parent_orders[0].remaining_quantity = 9.0
    state.parent_orders[0].status = "PARTIALLY_FILLED"
    state.child_orders[0].status = "CANCELED"
    state.broker_orders[0].filled_quantity = 1.0
    state.broker_orders[0].remaining_quantity = 9.0
    state.broker_orders[0].status = "CANCELED"
    store.save(state)
    adapter.orders[str(result.broker_order_id)].filled_quantity = 1.0
    adapter.orders[str(result.broker_order_id)].remaining_quantity = 9.0
    adapter.orders[str(result.broker_order_id)].status = "CANCELED"

    resumed = service.resume_remaining_order(
        account_label="main",
        order_ref=str(result.broker_order_id),
    )

    with pytest.raises(ValueError, match="latest tracked child attempt"):
        service.resume_remaining_order(
            account_label="main",
            order_ref=str(result.broker_order_id),
        )

    assert resumed.new_child_order_id.endswith("_2")


def test_accept_partial_fill_marks_parent_complete_locally(tmp_path: Path) -> None:
    adapter = FakeAdapter()
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

    result = service.execute_orders(
        [Order(symbol="AAPL.US", quantity=10, side="BUY", price=10.0)],
        **base_kwargs,
    )[0]
    state = store.load("fake", "main")
    state.parent_orders[0].filled_quantity = 1.0
    state.parent_orders[0].remaining_quantity = 9.0
    state.parent_orders[0].status = "PARTIALLY_FILLED"
    state.child_orders[0].status = "CANCELED"
    state.broker_orders[0].filled_quantity = 1.0
    state.broker_orders[0].remaining_quantity = 9.0
    state.broker_orders[0].status = "CANCELED"
    store.save(state)
    adapter.orders[str(result.broker_order_id)].filled_quantity = 1.0
    adapter.orders[str(result.broker_order_id)].remaining_quantity = 9.0
    adapter.orders[str(result.broker_order_id)].status = "CANCELED"

    outcome = service.accept_partial_fill(
        account_label="main",
        order_ref=str(result.broker_order_id),
    )
    refreshed = store.load("fake", "main")

    assert outcome.accepted_filled_quantity == 1.0
    assert outcome.abandoned_remaining_quantity == 9.0
    assert refreshed.parent_orders[0].status == "ACCEPTED_PARTIAL"
    assert refreshed.parent_orders[0].metadata["manual_resolution"] == "accepted_partial"
