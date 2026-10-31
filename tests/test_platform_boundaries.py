"""Public owner boundaries do not load the legacy implementation for contracts."""

import importlib
import json
import subprocess
import sys


def test_neutral_contracts_do_not_load_legacy_simulator():
    code = """
import sys
from quant_platform.backtest.contracts import CanonicalBacktestResult
from quant_platform.backtest.ledger import UnifiedLedger, reconcile_unified_ledger
for name in sys.modules:
    assert name != 'portfolio_backtester'
    assert not name.startswith(('portfolio_backtester.', 'quant_platform._portfolio'))
"""
    subprocess.run([sys.executable, "-c", code], check=True)


def test_old_and_owner_modules_share_identity_and_patched_globals(monkeypatch):
    old = importlib.import_module("portfolio_backtester.metrics")
    new = importlib.import_module("quant_platform.analytics.metrics")
    assert old is new
    monkeypatch.setattr(new, "scipy_stats", None)
    assert old.scipy_stats is None


def test_public_mapping_covers_compatibility_modules():
    from pathlib import Path

    root = Path(__file__).parents[1]
    mapping = json.loads((root / "docs/migration/portfolio-module-map.json").read_text())
    assert "portfolio_backtester.backends.base" in mapping
    assert (
        mapping["portfolio_backtester.backends.base"]["public_module"]
        == "quant_platform.backtest.contracts"
    )


def test_analytics_import_does_not_load_execution_simulator():
    subprocess.run(
        [
            sys.executable,
            "-c",
            """
import sys
from quant_platform.analytics.metrics import summarize_ic
assert not any(n.startswith('quant_platform._portfolio.execution_sim') for n in sys.modules)
assert not any(n.startswith('portfolio_backtester') for n in sys.modules)
""",
        ],
        check=True,
    )


def test_legacy_import_ratchet_checks_production_source():
    subprocess.run([sys.executable, "scripts/dev/check_legacy_imports.py"], check=True)


def test_import_ratchet_detects_dynamic_imports_but_keeps_schema_ids(tmp_path):
    import runpy
    from pathlib import Path

    namespace = runpy.run_path(str(Path("scripts/dev/check_legacy_imports.py")))
    source = tmp_path / "packages" / "owner"
    source.mkdir(parents=True)
    module = source / "example.py"
    module.write_text('schema = "portfolio_backtester.backtest_result.v1"\n')
    assert namespace["violations"](tmp_path) == []
    module.write_text('importlib.import_module("portfolio_backtester.metrics")\n')
    assert namespace["violations"](tmp_path)


def test_legacy_module_cli_still_runs_its_entrypoint():
    process = subprocess.run(
        [sys.executable, "-m", "portfolio_backtester.a_share_executable_oos_topk", "--help"],
        capture_output=True,
        text=True,
        check=True,
    )
    assert "usage:" in process.stdout
