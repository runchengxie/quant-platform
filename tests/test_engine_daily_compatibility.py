"""Platform research adapters around the single Engine daily owner."""

from importlib import import_module

import pandas as pd
import pytest
from pandas.testing import assert_frame_equal


@pytest.mark.parametrize(
    "module,names",
    [
        ("execution", ["DetailedTradeFeeModel", "EntryPolicy", "ExitPolicy"]),
        ("_position_backtest_config", ["PositionBacktestConfig", "PositionBacktestResult"]),
        ("execution_sim.config", ["ExecutionSimConfig"]),
        ("execution_sim.results", ["ExecutionAdjustedNavResult", "ExecutionSimResult"]),
        ("types", ["CostBreakdown", "BacktestPositionState", "BacktestLegResult"]),
    ],
)
def test_moved_value_identity(module, names):
    old = import_module("quant_platform._portfolio." + module)
    owner = import_module("quant_backtest_core.daily." + module)
    for name in names:
        assert getattr(old, name) is getattr(owner, name)
        assert getattr(import_module("portfolio_backtester." + module), name) is getattr(
            owner, name
        )


def fixture_frames():
    positions = pd.DataFrame(
        {
            "rebalance_date": ["20250102"],
            "entry_date": ["20250103"],
            "symbol": ["A"],
            "weight": [1.0],
            "side": ["long"],
        }
    )
    pricing = pd.DataFrame(
        {
            "trade_date": ["20250103", "20250106"],
            "symbol": ["A", "A"],
            "close": [10.0, 11.0],
            "amount": [100000.0, 100000.0],
        }
    )
    return positions, pricing


@pytest.mark.parametrize(
    "entrypoint", ["simulate_ideal_daily_nav", "simulate_execution_adjusted_nav"]
)
def test_legacy_daily_complete_tables_and_research(entrypoint):
    from quant_backtest_core.daily.execution_sim.results import ExecutionAdjustedNavResult

    from quant_platform._portfolio.execution_sim import ExecutionSimConfig
    from quant_platform._portfolio.metrics import summarize_period_returns

    public = import_module("quant_platform._portfolio.execution_sim")
    owner = import_module("quant_backtest_core.daily.execution_sim")
    positions, pricing = fixture_frames()
    kwargs = {"price_col": "close", "trading_days_per_year": 244}
    args = [positions, pricing]
    if entrypoint == "simulate_execution_adjusted_nav":
        args.append(ExecutionSimConfig(enabled=True, portfolio_value=1000, participation_rate=1))
    else:
        kwargs["portfolio_value"] = 1000
    result = getattr(public, entrypoint)(*args, **kwargs)
    expected = getattr(owner, entrypoint)(*args, **kwargs)
    assert type(result) is ExecutionAdjustedNavResult
    for name in ("daily", "orders", "fills"):
        assert_frame_equal(getattr(result, name), getattr(expected, name), check_exact=True)
    ledger, expected_ledger = result.to_unified_ledger(), expected.to_unified_ledger()
    assert type(ledger) is type(expected_ledger)
    for name in ledger.__dataclass_fields__:
        assert_frame_equal(getattr(ledger, name), getattr(expected_ledger, name), check_exact=True)
    returns = pd.Series(
        pd.to_numeric(result.daily.executed_return, errors="coerce").to_numpy(),
        index=pd.to_datetime(result.daily.trade_date),
        name="net_return",
    )
    stats = summarize_period_returns(
        returns, [{"entry_idx": i, "exit_idx": i + 1} for i in range(len(returns))], 244
    )
    assert result.summary["stats"].keys() == stats.keys()
    for key in stats:
        if isinstance(stats[key], float) and pd.isna(stats[key]):
            assert pd.isna(result.summary["stats"][key])
        else:
            assert result.summary["stats"][key] == stats[key]


def test_exact_research_clock_translation():
    from quant_platform.backtest.engine_clocks import to_execution_clocks

    value = {
        "schema_version": "research.clock.v1",
        "timezone": "Asia/Shanghai",
        "information_cutoff_at": "2025-01-02T15:00:00+08:00",
        "signal_at": "2025-01-02T15:00:01+08:00",
        "decision_at": "2025-01-02T15:00:02+08:00",
        "earliest_order_at": "2025-01-03T09:30:00+08:00",
        "execution_window_start_at": "2025-01-03T09:30:00+08:00",
        "execution_window_end_at": "2025-01-03T15:00:00+08:00",
        "valuation_at": "2025-01-06T15:00:00+08:00",
        "timing_policy_id": "synthetic",
        "trading_calendar_ref": "synthetic",
    }
    clocks = to_execution_clocks(value)
    assert clocks.information_ns == str(
        pd.Timestamp(value["information_cutoff_at"]).as_unit("ns").value
    )
    assert clocks.entry_ns == str(pd.Timestamp(value["earliest_order_at"]).as_unit("ns").value)
    assert clocks.effective_ns is None and clocks.report_ns is None


def test_product_translator_exists_and_rejects_non_product():
    from quant_platform.backtest.engine_results import to_canonical_result

    with pytest.raises(TypeError):
        to_canonical_result({})


def _product(tmp_path, *, missing_mark=False, mode="adjusted", receivable=False, zero_fills=False):
    import hashlib
    import json
    from pathlib import Path

    from quant_backtest_core.artifacts import json_bytes
    from quant_backtest_core.backends.daily import DailyBackend
    from quant_backtest_core.backends.protocol import BackendContext
    from quant_backtest_engine.product import parse_manifest

    fixtures = Path(__file__).parent / "fixtures" / "engine_daily"
    wire = json.loads((fixtures / "daily.json").read_text())
    if missing_mark:
        days = ["2020-01-03", "2020-01-06", "2020-01-07", "2020-01-08"]
        wire["inline_inputs"]["positions"] = wire["inline_inputs"]["positions"][:1]
        wire["inline_inputs"]["pricing"] = [
            {"trade_date": day, "symbol": "A", "close": mark, "amount": "1000000", "sell": True}
            for day, mark in zip(days, ["10", None, "12", "13.2"], strict=True)
        ]
        wire["settings"]["decision_clocks"].pop("2020-01-06")
        horizon = str(pd.Timestamp("2020-01-08T16:00:00+08:00").as_unit("ns").value)
        wire["clocks"]["valuation_ns"] = horizon
        wire["settings"]["decision_clocks"]["2020-01-02"]["valuation_ns"] = horizon
        from quant_backtest_core.daily.contracts import ExecutionCalendar

        calendar = ExecutionCalendar.from_dates("Asia/Shanghai", days)
        payload = calendar.semantic_bytes()
        wire["calendar"]["sha256"] = hashlib.sha256(payload).hexdigest()
    else:
        payload = (fixtures / "daily-calendar.json").read_bytes()
    (tmp_path / "daily-calendar.json").write_bytes(payload)
    wire["settings"]["mode"] = mode
    if zero_fills:
        for row in wire["inline_inputs"]["pricing"]:
            row["amount"] = "0"
    if receivable:
        wire["inline_inputs"]["positions"] = wire["inline_inputs"]["positions"][:1]
        wire["settings"]["decision_clocks"].pop("2020-01-06")
        wire["tapes"]["corporate_actions"] = [
            {
                "event_id": "synthetic-dividend",
                "symbol": "A",
                "available_date": "2020-01-02",
                "record_date": "2020-01-03",
                "ex_date": "2020-01-06",
                "cash_per_share": "1",
                "cash_pay_date": "2020-01-07" if receivable == "paid" else "2020-01-10",
                "stock_per_share": "0",
                "stock_tradable_date": None,
                "withholding_rate": "0",
            }
        ]
    context = BackendContext(tmp_path, tmp_path)
    backend = DailyBackend(context)
    manifest = parse_manifest(wire)
    request = backend._prepare(manifest, context)
    result = backend.run(manifest, context)
    assert json_bytes(wire)
    return result, request


def test_product_full_ledger_matches_owned_hand_oracle_and_serialized_identity(tmp_path):
    from dataclasses import replace

    from quant_backtest_core.daily.runner import run_daily
    from quant_backtest_engine.product import parse_result, result_to_json

    from quant_platform._portfolio.backends.native import _attach_fill_ids, _attach_order_ids
    from quant_platform.backtest.engine_results import to_canonical_result

    product, request = _product(tmp_path)
    assert parse_result(result_to_json(product)) == product
    canonical = to_canonical_result(product, artifact_root=tmp_path)
    owned = run_daily(request)
    ledger = owned.to_unified_ledger(portfolio_value=request.config.portfolio_value)
    orders = _attach_order_ids(ledger.orders)
    ledger = replace(ledger, orders=orders, fills=_attach_fill_ids(ledger.fills, orders))
    for name in ledger.__dataclass_fields__:
        assert_frame_equal(
            getattr(canonical.unified_ledger, name), getattr(ledger, name), check_exact=True
        )
    assert canonical.daily_ledger.cash.tolist() == [0.0, 0.0, 0.0]
    assert canonical.daily_ledger.nav.tolist() == [1000.0, 1000.0, 1000.0]
    assert canonical.orders.loc[canonical.orders.symbol.eq("B"), "filled_notional"].sum() == 0
    assert canonical.schema_version == "canonical_backtest_result.v1"
    assert canonical.metadata["execution_aware"] is True
    without_raw = to_canonical_result(product)
    assert without_raw.unified_ledger is None
    assert without_raw.metadata["execution_aware"] is False
    assert without_raw.summary == canonical.summary


@pytest.mark.parametrize("mode", ["adjusted", "sequenced"])
def test_canonical_keeps_incomplete_intervals_unknown_and_unpublishable(tmp_path, mode):
    from quant_platform._portfolio.backends.bundle import write_execution_aware_result_bundle
    from quant_platform.backtest.engine_results import to_canonical_result

    product, _ = _product(tmp_path, missing_mark=True, mode=mode)
    canonical = to_canonical_result(product, artifact_root=tmp_path)
    returns = canonical.performance.net_return.tolist()
    assert returns[0] == 0 and returns[1:3] == [None, None]
    assert returns[3] == pytest.approx(0.1)
    assert canonical.performance.raw_executed_return.iloc[2] == pytest.approx(0.2)
    assert canonical.summary["cumulative_return"] is None
    assert canonical.summary["valuation_complete"] is False
    assert canonical.metadata["execution_aware"] is False
    with pytest.raises(ValueError, match="complete supported"):
        write_execution_aware_result_bundle(
            tmp_path / "bundle",
            result=canonical,
            run_id="synthetic",
            research_clock={},
            producer={},
            configuration_sha256="0" * 64,
            input_refs=[],
        )
    assert not (tmp_path / "bundle").exists()


def test_product_tampered_raw_and_noncompleted_results_fail(tmp_path):
    from dataclasses import replace

    from quant_platform.backtest.engine_results import to_canonical_result

    product, _ = _product(tmp_path)
    with pytest.raises(ValueError, match="completed"):
        to_canonical_result(replace(product, status="partial"))
    path = tmp_path / product.raw_result.uri
    path.write_bytes(path.read_bytes() + b" ")
    with pytest.raises(ValueError, match="digest"):
        to_canonical_result(product, artifact_root=tmp_path)


def test_all_pure_financial_helpers_are_exact_provider_aliases():
    pairs = [
        (
            "leg_helpers",
            "leg_financial",
            ["_build_backtest_leg_result", "_build_leg_turnover_report", "_next_position_state"],
        ),
        ("pricing", "pricing", ["slippage_pricing_row"]),
        (
            "period_turnover",
            "period_turnover",
            ["period_result_from_leg", "period_result_from_legs"],
        ),
        (
            "trade_accounting",
            "trade_accounting",
            ["compute_trade_summary", "drift_previous_weights"],
        ),
        ("types", "types", ["BacktestPeriodResult"]),
    ]
    for old, new, names in pairs:
        consumer = import_module("quant_platform._portfolio." + old)
        provider = import_module("quant_backtest_core.daily." + new)
        for name in names:
            assert getattr(consumer, name) is getattr(provider, name)
    legacy = import_module("quant_platform._portfolio.trade_accounting")
    helpers = import_module("quant_backtest_core.daily._period_helpers")
    assert legacy.compute_trade_summary is not helpers._compute_trade_summary


@pytest.mark.parametrize("change", ["schema", "dtype", "media", "escape"])
def test_full_owner_artifact_boundary_fails_closed(tmp_path, change):
    import hashlib
    import json
    from dataclasses import replace

    from quant_backtest_engine.product import ArtifactRef

    from quant_platform.backtest.engine_results import to_canonical_result

    product, _ = _product(tmp_path)
    reference = product.raw_result
    if change == "media":
        reference = replace(reference, media_type="application/octet-stream")
    elif change == "escape":
        reference = replace(reference, uri="../outside.json")
    else:
        path = tmp_path / reference.uri
        raw = json.loads(path.read_text())
        if change == "schema":
            raw["schema"] = "unknown-owner.v9"
        else:
            raw["owner_tables"]["daily"]["dtypes"][0] = "__import__('os').system('false')"
        payload = json.dumps(raw).encode()
        path.write_bytes(payload)
        reference = ArtifactRef(
            reference.uri, hashlib.sha256(payload).hexdigest(), "application/json"
        )
    product = replace(
        product,
        raw_result=reference,
        normalization=replace(product.normalization, source_sha256=reference.sha256),
    )
    with pytest.raises(ValueError):
        to_canonical_result(product, artifact_root=tmp_path)


def test_available_empty_evidence_remains_distinct_from_unavailable(tmp_path):
    from dataclasses import replace

    from quant_backtest_engine.product import EvidenceTable

    from quant_platform.backtest.engine_results import to_canonical_result

    product, _ = _product(tmp_path)
    tables = tuple(
        EvidenceTable(t.name, "available", (), None) if t.name == "fills" else t
        for t in product.tables
    )
    canonical = to_canonical_result(replace(product, tables=tables))
    saved = {t["name"]: t for t in canonical.metadata["product_result"]["tables"]}
    assert saved["fills"]["status"] == "available" and saved["fills"]["rows"] == []
    assert saved["capital_flows"]["status"] == "unavailable"
    assert saved["capital_flows"]["reason"]
    assert canonical.metadata["execution_aware"] is False


def test_explicit_daily_request_keeps_clock_bounds_and_exact_selector():
    from quant_backtest_core.daily.contracts import ExecutionCalendar

    from quant_platform._portfolio.execution_sim import ExecutionSimConfig
    from quant_platform.backtest.engine_daily import build_daily_request, run_daily

    positions, pricing = fixture_frames()
    pricing = pricing.rename(columns={"amount": "turnover_cny"})
    clock = {
        "schema_version": "research.clock.v1",
        "timezone": "Asia/Shanghai",
        "information_cutoff_at": "2025-01-02T15:00:00+08:00",
        "signal_at": "2025-01-02T15:00:01+08:00",
        "decision_at": "2025-01-02T15:00:02+08:00",
        "earliest_order_at": "2025-01-03T09:30:00+08:00",
        "execution_window_start_at": "2025-01-03T09:35:00+08:00",
        "execution_window_end_at": "2025-01-03T15:00:00+08:00",
        "valuation_at": "2025-01-06T15:00:00+08:00",
        "timing_policy_id": "synthetic",
        "trading_calendar_ref": "synthetic",
    }
    request = build_daily_request(
        positions=positions,
        pricing=pricing,
        calendar=ExecutionCalendar.from_dates("Asia/Shanghai", ["2025-01-03", "2025-01-06"]),
        decision_clocks={"20250102": clock},
        config=ExecutionSimConfig(
            enabled=True,
            portfolio_value=1000,
            participation_rate=1,
            liquidity_cols=("turnover_cny",),
        ),
    )
    assert request.config.liquidity_cols == ("turnover_cny",)
    assert request.decision_clocks["2025-01-02"].entry_ns == str(
        pd.Timestamp(clock["execution_window_start_at"]).as_unit("ns").value
    )
    result = run_daily(request)
    assert result.summary["stats"]["total_return"] == pytest.approx(0.1)
    assert result.summary["execution_summary"]["valuation_complete"] is True


def test_mapping_clock_preserves_submicrosecond_precision():
    from test_sequenced_execution_backend import _clock

    from quant_platform.backtest.engine_clocks import to_execution_clocks

    mapping = _clock("20200102", "20200103")
    mapping["information_cutoff_at"] = "2020-01-02T18:00:00.123456789+08:00"
    assert to_execution_clocks(mapping).information_ns == str(
        pd.Timestamp(mapping["information_cutoff_at"]).as_unit("ns").value
    )


@pytest.mark.parametrize("paid", [False, True])
def test_receivables_remain_raw_and_do_not_fabricate_balanced_canonical_cash(tmp_path, paid):
    from quant_platform.backtest.engine_results import to_canonical_result

    product, _ = _product(tmp_path, receivable="paid" if paid else True)
    canonical = to_canonical_result(product, artifact_root=tmp_path)
    assert canonical.unified_ledger is None
    assert canonical.daily_ledger.empty
    assert canonical.metadata["execution_aware"] is False
    assert canonical.metadata["full_owner_artifact_verified"] is True
    assert canonical.metadata["canonical_ledger_limitation"] == "unpaid_owner_receivables"
    raw = canonical.metadata["owner_result"]
    assert len(raw["owner_unified_ledger"]) == 8
    daily = raw["tables"]["daily"]["rows"]
    assert [row["cash_receivable"] for row in daily] == ["0.0", "100.0", "0.0" if paid else "100.0"]
    assert [row["cash"] for row in daily] == ["0.0", "0.0", "100.0" if paid else "0.0"]
    assert raw["owner_tables"]["actions"]["data"]
    assert raw["owner_tables"]["holdings"]["data"]
    from quant_backtest_engine.product import result_to_json

    assert canonical.summary == result_to_json(product)["summary"]


def test_normalization_source_schema_must_match_verified_owner_schema(tmp_path):
    from dataclasses import replace

    from quant_platform.backtest.engine_results import to_canonical_result

    product, _ = _product(tmp_path)
    product = replace(
        product, normalization=replace(product.normalization, source_schema="unknown.v9")
    )
    with pytest.raises(ValueError, match="schema"):
        to_canonical_result(product, artifact_root=tmp_path)


def test_unknown_string_dtype_is_not_silently_coerced():
    from quant_platform.backtest.engine_results import _dtype

    with pytest.raises(ValueError, match="dtype"):
        _dtype("<StringDtype(storage='unknown', na_value=nan)>")


def test_raw_artifact_symlink_cannot_escape_explicit_root(tmp_path):
    from quant_platform.backtest.engine_results import to_canonical_result

    product, _ = _product(tmp_path)
    other = tmp_path / "isolated-root"
    other.mkdir()
    ref = other / product.raw_result.uri
    ref.parent.mkdir(parents=True, exist_ok=True)
    ref.symlink_to(tmp_path / product.raw_result.uri)
    with pytest.raises(ValueError):
        to_canonical_result(product, artifact_root=other)


def test_real_rust_product_keeps_limited_canonical_evidence(tmp_path):
    import json
    import os
    from pathlib import Path

    from quant_backtest_core.backends.protocol import BackendContext
    from quant_backtest_core.backends.rust import RustBackend
    from quant_backtest_engine.product import parse_manifest

    from quant_platform.backtest.engine_results import to_canonical_result

    binary = os.environ.get("SESSION_ENGINE_BINARY")
    if not binary:
        pytest.skip("set SESSION_ENGINE_BINARY and SESSION_ENGINE_SHA256 for native product test")
    fixtures = Path(__file__).parent / "fixtures" / "engine_daily"
    (tmp_path / "synthetic-calendar.json").write_bytes(
        (fixtures / "synthetic-calendar.json").read_bytes()
    )
    manifest = parse_manifest(json.loads((fixtures / "rust-session.json").read_text()))
    context = BackendContext(tmp_path, tmp_path, Path(binary), os.environ["SESSION_ENGINE_SHA256"])
    result = RustBackend(context).run(manifest, context)
    canonical = to_canonical_result(result, artifact_root=tmp_path)
    canonical.validate()
    assert len(canonical.fills) == 2
    assert canonical.daily_ledger.iloc[-1]["nav"] == pytest.approx(10197.8)
    assert canonical.unified_ledger is None
    assert canonical.metadata["execution_aware"] is False
    assert canonical.metadata["product_result"]["tables"]


@pytest.mark.parametrize("value", [None, float("nan"), float("inf"), -float("inf")])
def test_unknown_receivable_is_never_treated_as_zero(value):
    from quant_platform.backtest.engine_results import _receivable_limitation

    assert (
        _receivable_limitation(pd.DataFrame({"cash_receivable": [value]}))
        == "unknown_owner_receivables"
    )


def test_genuine_available_empty_fills_keep_verified_eight_table_ledger(tmp_path):
    from quant_platform.backtest.engine_results import to_canonical_result

    product, _ = _product(tmp_path, zero_fills=True)
    fills = next(table for table in product.tables if table.name == "fills")
    assert fills.status == "available"
    assert fills.rows == ()
    canonical = to_canonical_result(product, artifact_root=tmp_path)
    assert canonical.fills.empty
    assert canonical.unified_ledger is not None
    assert len(canonical.unified_ledger.__dataclass_fields__) == 8
    assert canonical.daily_ledger.cash.tolist() == [1000.0] * 3
    assert canonical.metadata["execution_aware"] is True
