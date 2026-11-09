"""Consumer contracts for Engine provider A; financial kernels are tested by Engine."""

import importlib
import json
from importlib.metadata import version
from pathlib import Path

import pandas as pd
import pytest
from engine_core_fixtures import Policy, bars, fills, parents, targets

PROVIDER_MODULES = {
    "quant_platform.backtest.market_paths": "quant_backtest_core.backtest.market_paths",
    "quant_platform.backtest.stress": "quant_backtest_core.backtest.stress",
    "quant_platform.backtest.costs": "quant_backtest_core.backtest.costs",
    "quant_platform.backtest.impact": "quant_backtest_core.backtest.impact",
    "quant_platform.backtest.impact_scenarios": "quant_backtest_core.backtest.impact_scenarios",
    "quant_platform.analytics.execution_integrity": (
        "quant_backtest_core.evidence.execution_integrity"
    ),
    "quant_platform.analytics.transaction_costs": "quant_backtest_core.evidence.transaction_costs",
    "quant_platform.analytics.cost_scope": "quant_backtest_core.evidence.cost_scope",
    "quant_platform.analytics.capital_returns": "quant_backtest_core.evidence.capital_returns",
    "quant_platform.backtest.minute": "quant_backtest_core.backtest.minute",
    "quant_platform.backtest.minute_session": "quant_backtest_core.backtest.minute_session",
    "quant_platform.backtest._minute_checkpoint": "quant_backtest_core.backtest._minute_checkpoint",
    "quant_platform.backtest.quantity_locks": "quant_backtest_core.backtest.quantity_locks",
    "quant_platform._portfolio.minute_execution": "quant_backtest_core._minute.minute_execution",
    "quant_platform._portfolio._minute_state": "quant_backtest_core._minute._minute_state",
    "quant_platform._portfolio._minute_validation": (
        "quant_backtest_core._minute._minute_validation"
    ),
    "quant_platform._portfolio.capital_flows": "quant_backtest_core._minute.capital_flows",
    "quant_platform._portfolio.corporate_actions": "quant_backtest_core._minute.corporate_actions",
    "quant_platform._portfolio.valuation_events": "quant_backtest_core._minute.valuation_events",
}


@pytest.mark.parametrize("old,new", PROVIDER_MODULES.items())
def test_provider_module_and_class_identity(old, new):
    facade = importlib.import_module(old)
    provider = importlib.import_module(new)
    assert facade is provider
    for name, value in vars(provider).items():
        if isinstance(value, type) or callable(value):
            assert getattr(facade, name) is value


def test_provider_dependency_versions():
    assert version("quant-platform") == "0.2.0"
    assert version("quant-backtest-core") == "0.2.0"
    assert version("quant-backtest-engine-client") == "0.3.0"


def test_independent_caller_result_and_actions_match_platform():
    platform = importlib.import_module("quant_platform.backtest.minute")
    core = importlib.import_module("quant_backtest_core.backtest.minute")

    def run(api):
        impact = importlib.import_module(api.__name__.rsplit(".", 1)[0] + ".impact")
        return api.simulate_minute_execution(
            targets(),
            bars(),
            api.MinuteExecutionConfig(10000, 0.1, 3, 8),
            impact_model=impact.LinearImpact(permanent=0.0001),
        )

    left, right = run(platform), run(core)
    for name, value in vars(left).items():
        other = getattr(right, name)
        if isinstance(value, pd.DataFrame):
            pd.testing.assert_frame_equal(value, other)
        else:
            assert value == other
    for name in ("CapitalFlow", "CorporateAction", "ValuationEvent"):
        assert getattr(platform, name) is getattr(core, name)


def test_cost_result_frames_preserve_all_columns():
    platform = importlib.import_module("quant_platform.analytics.transaction_costs")
    core = importlib.import_module("quant_backtest_core.evidence.transaction_costs")
    kwargs = {"billing": "parent", "commission_bps": 3, "minimum_commission": 5, "sell_tax_bps": 10}
    left = platform.audit_transaction_costs(parents(), fills(), **kwargs)
    right = core.audit_transaction_costs(parents(), fills(), **kwargs)
    for name, value in vars(left).items():
        other = getattr(right, name)
        if isinstance(value, pd.DataFrame):
            pd.testing.assert_frame_equal(value, other)
        else:
            assert value == other


def test_legacy_aliases_share_engine_event_classes():
    for name in ("corporate_actions", "valuation_events", "minute_execution"):
        old = importlib.import_module("portfolio_backtester." + name)
        public = importlib.import_module("quant_platform.backtest.legacy." + name)
        core = importlib.import_module("quant_backtest_core._minute." + name)
        assert old is public is core


def test_historical_v2_requires_original_full_release():
    from quant_platform.backtest.minute import MinuteExecutionConfig
    from quant_platform.backtest.minute_session import MinuteSession

    wire = json.loads((Path(__file__).parent / "fixtures/engine-core-legacy-v2.json").read_text())
    assert wire["schema"] == "minute-session.v2"
    with pytest.raises(ValueError, match="original pinned sources"):
        MinuteSession.restore(
            targets(), bars(), MinuteExecutionConfig(10000, 0.1, 3, 8), wire, policy=Policy()
        )


def test_migration_routes_preserve_locales_anchors_and_history():
    root = Path(__file__).resolve().parents[1]
    manifest = json.loads((root / "docs/migration/engine-provider-a.json").read_text())
    assert manifest["provider_revision"] == "19a2ae714b567fc1a46cf996fa5a86a90138bc44"
    assert manifest["modules"] == PROVIDER_MODULES
    for row in manifest["routes"]:
        source = (root / row["source"]).read_text()
        assert row["destination"] in source
        assert (".zh-CN/" in row["destination"]) == (row["locale"] == "zh-CN")
        for anchor in row["anchors"]:
            assert f'id="{anchor}"' in source
        if row["old_url"]:
            assert "blob/7a618bddd8fdeee5dbe37fe5b54a9698e0de5355/" in source


def test_provider_sources_do_not_depend_on_platform():
    import ast

    for name in PROVIDER_MODULES.values():
        module = importlib.import_module(name)
        tree = ast.parse(Path(module.__file__).read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports = [alias.name for alias in node.names]
            elif isinstance(node, ast.ImportFrom):
                imports = [node.module or ""]
            else:
                continue
            assert not any(
                name.startswith(
                    ("quant_platform", "portfolio_backtester", "quant_backtest_runtime")
                )
                for name in imports
            )


def test_pooled_targets_use_one_owner_through_existing_platform_api():
    from quant_backtest_core.backtest.minute import simulate_minute_execution as core_simulate

    from portfolio_backtester.minute_execution import (
        MinuteExecutionConfig,
        simulate_minute_execution,
    )
    from quant_platform.portfolio.sleeves import pool_sleeves

    assert simulate_minute_execution is core_simulate
    pooled = pool_sleeves({"one": targets(), "two": targets()}, {"one": 0.5, "two": 0.5})
    result = simulate_minute_execution(
        pooled, bars(volume=10000), MinuteExecutionConfig(10000, 1, 0, 0)
    )
    # One pooled financial owner receives the original total account cash.
    assert len(result.orders) == 1
    assert result.fills.quantity.sum() == 1000
    assert result.daily.cash.iloc[-1] == 0
