"""Check public owners and compatibility aliases in a regular installed wheel."""

from __future__ import annotations

import argparse
import importlib
import importlib.util
import json
import sys
from importlib.metadata import distribution
from pathlib import Path


def _check_clean_imports() -> None:
    import quant_platform
    from quant_platform.backtest.contracts import CanonicalBacktestResult
    from quant_platform.backtest.ledger import UnifiedLedger

    assert CanonicalBacktestResult and UnifiedLedger
    assert not any(name.startswith("quant_platform._portfolio") for name in sys.modules)
    from quant_platform.analytics.metrics import summarize_ic

    assert callable(summarize_ic)
    assert not any(
        name.startswith("quant_platform._portfolio.execution_sim") for name in sys.modules
    )
    assert not any(name.startswith("portfolio_backtester") for name in sys.modules)
    assert "site-packages" in Path(quant_platform.__file__).parts
    assert importlib.util.find_spec("quant_backtest_engine") is not None
    assert distribution("quant-backtest-core").version == "0.3.0"
    assert distribution("quant-backtest-engine-client").version == "0.3.0"


def _check_aliases(mapping: dict) -> None:
    for old, entry in mapping.items():
        old_module = importlib.import_module(old)
        implementation = importlib.import_module(entry["implementation_module"])
        public = importlib.import_module(entry["public_module"])
        if hasattr(old_module, "__path__"):
            for name in getattr(old_module, "__all__", ()):
                assert getattr(old_module, name) is getattr(implementation, name)
        else:
            assert old_module is implementation
            assert public is implementation


def _check_provider_aliases(manifest: dict) -> None:
    for old, new in manifest["modules"].items():
        facade = importlib.import_module(old)
        provider = importlib.import_module(new)
        assert facade is provider
        assert provider.__file__ is not None
        assert Path(provider.__file__).is_relative_to(Path(sys.prefix))
        for name, value in vars(provider).items():
            if isinstance(value, type):
                assert getattr(facade, name) is value
    for old, entry in manifest["adapters"].items():
        facade = importlib.import_module(old)
        provider = importlib.import_module(entry["provider"])
        for name in entry["value_aliases"]:
            assert getattr(facade, name) is getattr(provider, name)
    import ticknet
    from quant_backtest_core.microstructure import impact
    from ticknet import simulator

    for name in ("ExecutionSchedule", "ImpactResult", "ImpactEstimator"):
        assert getattr(ticknet, name) is getattr(simulator, name) is getattr(impact, name)
    assert not {
        "torch",
        "ticknet.dataset",
        "ticknet.model",
        "ticknet.simulator.generator",
        "ticknet.simulator.sqrt_law",
    } & set(sys.modules)
    for name in ("quant-platform", "quant-backtest-core", "quant-backtest-engine-client"):
        installed = distribution(name)
        direct_url = json.loads(installed.read_text("direct_url.json") or "{}")
        assert not direct_url.get("dir_info", {}).get("editable", False)
        if "vcs_info" in direct_url:
            assert direct_url["vcs_info"]["commit_id"] == manifest["provider_revision"]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--module-map", type=Path, required=True)
    parser.add_argument(
        "--engine-enabled", action="store_true", help="Compatibility flag; SDK is now mandatory."
    )
    args = parser.parse_args()
    _check_clean_imports()
    _check_aliases(json.loads(args.module_map.read_text()))
    manifest = args.module_map.with_name("engine-provider-b.json")
    aliases = json.loads(manifest.read_text())
    current = json.loads(manifest.with_name("engine-provider-c.json").read_text())
    aliases["provider_revision"] = current["provider_revision"]
    _check_provider_aliases(aliases)
    from quant_backtest_core.daily import dated_fees as owned_fees
    from quant_backtest_core.daily.types import BacktestLegResult, BacktestPeriodResult

    from quant_platform._portfolio import types as legacy_types
    from quant_platform.backtest.legacy import dated_fees as public_fees

    assert public_fees.DatedTradeFeeModel is owned_fees.DatedTradeFeeModel
    assert legacy_types.BacktestLegResult is BacktestLegResult
    assert legacy_types.BacktestPeriodResult is BacktestPeriodResult
    installed = distribution("quant-platform")
    forbidden = {"torch", "xgboost", "sklearn", "alpha_research.backends.qlib"}
    assert not forbidden & set(sys.modules)
    assert installed.version == "0.3.0"
    print("Regular wheel: neutral imports, owner aliases and mandatory provider boundary verified")


if __name__ == "__main__":
    main()
