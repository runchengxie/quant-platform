from __future__ import annotations

from pathlib import Path

import pytest

from quant_execution_engine.execution import (
    ExecutionStateStore,
    OrderLifecycleService,
)
from quant_execution_engine.models import Order
from quant_execution_engine.renderers.table import (
    render_tracked_order_detail,
)
from quant_execution_engine.risk import RiskGateChain
from tests.execution._execution_foundation_fakes import (
    FakeAdapter,
)

pytestmark = pytest.mark.unit


def test_cancel_tracked_order_updates_state(tmp_path: Path) -> None:
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

    outcome = service.cancel_order(
        account_label="main",
        order_ref=str(result.broker_order_id),
    )
    state = store.load("fake", "main")

    assert outcome.status == "CANCELED"
    assert state.broker_orders[0].status == "CANCELED"
    assert state.child_orders[0].status == "CANCELED"
    assert state.parent_orders[0].status == "CANCELED"


def test_cancel_accepts_child_order_id_reference(tmp_path: Path) -> None:
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

    outcome = service.cancel_order(
        account_label="main",
        order_ref=str(result.child_order_id),
    )

    assert outcome.broker_order_id == result.broker_order_id
    assert outcome.status == "CANCELED"


def test_get_tracked_order_returns_lifecycle_details(tmp_path: Path) -> None:
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

    tracked = service.get_tracked_order(
        account_label="main",
        order_ref=str(result.broker_order_id),
    )

    assert tracked.intent is not None
    assert tracked.parent is not None
    assert tracked.child is not None
    assert tracked.broker_order is not None
    assert tracked.intent.limit_price is None
    assert tracked.child.child_order_id == result.child_order_id
    assert tracked.broker_order.broker_order_id == result.broker_order_id


def test_cancel_all_open_orders_only_targets_tracked_open_orders(
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

    first = service.execute_orders(
        [Order(symbol="AAPL.US", quantity=10, side="BUY", price=10.0)],
        **base_kwargs,
    )[0]
    second = service.execute_orders(
        [Order(symbol="MSFT.US", quantity=5, side="BUY", price=10.0)],
        **base_kwargs,
    )[0]
    third = service.execute_orders(
        [Order(symbol="TSLA.US", quantity=3, side="BUY", price=10.0)],
        **base_kwargs,
    )[0]
    service.cancel_order(account_label="main", order_ref=str(third.broker_order_id))

    outcome = service.cancel_all_open_orders(account_label="main")
    state = store.load("fake", "main")

    assert outcome.targeted_orders == 2
    assert {result.broker_order_id for result in outcome.results} == {
        str(first.broker_order_id),
        str(second.broker_order_id),
    }
    assert adapter.cancel_calls.count(str(first.broker_order_id)) == 1
    assert adapter.cancel_calls.count(str(second.broker_order_id)) == 1
    assert adapter.cancel_calls.count(str(third.broker_order_id)) == 1
    assert all(record.status == "CANCELED" for record in state.broker_orders)


def test_retry_canceled_zero_fill_order_creates_new_attempt(tmp_path: Path) -> None:
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
    service.cancel_order(account_label="main", order_ref=str(result.broker_order_id))

    outcome = service.retry_order(
        account_label="main",
        order_ref=str(result.broker_order_id),
    )
    state = store.load("fake", "main")

    assert outcome.new_child_order_id.endswith("_2")
    assert outcome.broker_order_id is not None
    assert outcome.broker_status == "NEW"
    assert len(state.child_orders) == 2
    assert state.child_orders[-1].attempt == 2
    assert state.parent_orders[0].status == "PENDING"
    assert adapter.submit_calls == 2


def test_reprice_open_limit_order_creates_new_attempt(tmp_path: Path) -> None:
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

    outcome = service.reprice_order(
        account_label="main",
        order_ref=str(original.broker_order_id),
        limit_price=9.5,
    )
    state = store.load("fake", "main")

    assert outcome.cancel_status == "CANCELED"
    assert outcome.new_child_order_id is not None
    assert outcome.new_child_order_id.endswith("_2")
    assert outcome.broker_order_id is not None
    assert outcome.broker_status == "NEW"
    assert adapter.cancel_calls.count(str(original.broker_order_id)) == 1
    assert adapter.submit_calls == 2
    assert len(state.child_orders) == 2
    assert state.parent_orders[0].status == "PENDING"
    assert state.intents[0].limit_price == 9.5


def test_reprice_rejects_non_limit_order(tmp_path: Path) -> None:
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

    original = service.execute_orders(
        [Order(symbol="AAPL.US", quantity=10, side="BUY", price=10.0)],
        **base_kwargs,
    )[0]

    with pytest.raises(ValueError, match="LIMIT"):
        service.reprice_order(
            account_label="main",
            order_ref=str(original.broker_order_id),
            limit_price=9.5,
        )


def test_render_tracked_order_detail_includes_target_context_and_reprice_metadata(
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
        "target_source": "smoke-signal",
        "target_asof": "2026-04-14",
        "target_input_path": "outputs/targets/smoke.json",
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
    repriced = service.reprice_order(
        account_label="main",
        order_ref=str(original.broker_order_id),
        limit_price=9.5,
    )
    tracked = service.get_tracked_order(
        account_label="main",
        order_ref=str(repriced.broker_order_id),
    )

    rendered = render_tracked_order_detail(tracked)

    assert "Target Source: smoke-signal" in rendered
    assert "Target Asof: 2026-04-14" in rendered
    assert "Target Input: outputs/targets/smoke.json" in rendered
    assert "Intent Limit Price: 9.5" in rendered
    assert "Last Reprice At:" in rendered
    assert "Last Reprice From Limit: 10.0" in rendered
