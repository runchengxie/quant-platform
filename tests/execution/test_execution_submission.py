from __future__ import annotations

from pathlib import Path

import pytest

import quant_execution_engine.broker.factory as broker_factory
from quant_execution_engine.broker.base import (
    BrokerValidationError,
)
from quant_execution_engine.execution import (
    ExecutionState,
    ExecutionStateStore,
    OrderLifecycleService,
)
from quant_execution_engine.models import Order
from quant_execution_engine.risk import RiskGateChain
from tests.execution._execution_foundation_fakes import (
    FakeAdapter,
)

pytestmark = pytest.mark.unit


def test_execution_state_store_round_trip(tmp_path: Path) -> None:
    store = ExecutionStateStore(root_dir=tmp_path)
    state = ExecutionState(broker_name="fake", account_label="main")
    state.consecutive_failures = 2
    store.save(state)

    loaded = store.load("fake", "main")

    assert loaded.broker_name == "fake"
    assert loaded.account_label == "main"
    assert loaded.consecutive_failures == 2


def test_risk_gate_blocks_oversized_order(tmp_path: Path) -> None:
    adapter = FakeAdapter()
    store = ExecutionStateStore(root_dir=tmp_path)
    service = OrderLifecycleService(
        adapter,
        state_store=store,
        risk_chain=RiskGateChain({"max_qty_per_order": 5}),
    )
    order = Order(symbol="AAPL.US", quantity=10, side="BUY", price=10.0)

    results = service.execute_orders(
        [order],
        account_label="main",
        dry_run=False,
        target_source="unit",
        target_asof="2026-04-14",
        target_input_path="tests/targets.json",
    )

    assert results[0].status == "BLOCKED"
    assert "max_qty_per_order" in str(results[0].risk_decisions)
    assert adapter.submit_calls == 0
    state = store.load("fake", "main")
    assert state.child_orders[0].status == "BLOCKED"
    assert state.child_orders[0].message is not None
    assert state.parent_orders[0].status == "BLOCKED"


def test_cn_dry_run_never_submits_to_adapter(tmp_path: Path) -> None:
    adapter = FakeAdapter()
    service = OrderLifecycleService(
        adapter,
        state_store=ExecutionStateStore(root_dir=tmp_path),
        risk_chain=RiskGateChain({}),
    )

    results = service.execute_orders(
        [Order(symbol="600519.SH.CN", quantity=100, side="BUY", price=10.0)],
        account_label="main",
        dry_run=True,
        target_source="strategy-pipeline",
        target_asof="2026-05-29",
        target_input_path="outputs/targets/a_share_latest.json",
    )

    assert results[0].status == "DRY_RUN"
    assert results[0].order_id is not None
    assert results[0].order_id.startswith("dry_run_")
    assert adapter.submit_calls == 0


def test_idempotent_submission_reuses_existing_open_order(tmp_path: Path) -> None:
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
    )
    second = service.execute_orders(
        [Order(symbol="AAPL.US", quantity=10, side="BUY", price=10.0)],
        **base_kwargs,
    )

    assert first[0].broker_order_id == second[0].broker_order_id
    assert adapter.submit_calls == 1


def test_market_order_intent_ignores_preview_price_for_idempotency(
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
        [
            Order(
                symbol="AAPL.US",
                quantity=10,
                side="BUY",
                price=10.0,
                order_type="MARKET",
            )
        ],
        **base_kwargs,
    )
    second = service.execute_orders(
        [
            Order(
                symbol="AAPL.US",
                quantity=10,
                side="BUY",
                price=10.5,
                order_type="MARKET",
            )
        ],
        **base_kwargs,
    )
    state = store.load("fake", "main")

    assert first[0].broker_order_id == second[0].broker_order_id
    assert adapter.submit_calls == 1
    assert state.intents[0].limit_price is None


def test_resolve_broker_name_requires_explicit_or_configured_backend(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(broker_factory, "load_cfg", lambda: {})

    with pytest.raises(
        BrokerValidationError,
        match="broker backend is not configured",
    ):
        broker_factory.resolve_broker_name()
