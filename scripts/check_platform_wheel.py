"""Check public owners and compatibility aliases in a regular installed wheel."""

from __future__ import annotations

import argparse
import importlib
import importlib.util
import json
import re
import sys
import tomllib
from importlib.metadata import distribution
from pathlib import Path

_PROVIDER_SUBDIRECTORIES = {
    "quant-backtest-core": "packages/core",
    "quant-backtest-engine-client": "packages/python-sdk",
}
_PROVIDER_GIT_URL = "git+https://github.com/runchengxie/quant-backtest-engine.git@"


def _provider_pin(requirement: str) -> tuple[str, str] | None:
    match = re.match(
        r"^(quant-backtest-core|quant-backtest-engine-client)(?=$|\[|\s|[<>=!~])",
        requirement,
    )
    if match is None:
        return None
    name = match.group(1)
    _, separator, url = requirement.partition(" @ ")
    if not separator or not url.startswith(_PROVIDER_GIT_URL):
        raise ValueError(f"{name} must pin the Git provider with a 40-character SHA")
    revision, _, subdirectory = url.removeprefix(_PROVIDER_GIT_URL).partition("#subdirectory=")
    if re.fullmatch(r"[0-9a-fA-F]{40}", revision) is None:
        raise ValueError(f"{name} must pin a 40-character Git SHA")
    if subdirectory != _PROVIDER_SUBDIRECTORIES[name]:
        raise ValueError(f"{name} has an incompatible provider subdirectory")
    return name, revision.lower()


def active_provider_revision(pyproject: dict) -> str:
    """Resolve coherent active pins without reading or mutating historical receipts."""
    project = pyproject["project"]
    mandatory = [
        pin
        for requirement in project["dependencies"]
        if (pin := _provider_pin(requirement)) is not None
    ]
    if {name for name, _ in mandatory} != set(_PROVIDER_SUBDIRECTORIES):
        raise ValueError("both Engine distributions require mandatory Git pins")
    pins = list(mandatory)
    groups = [
        *project.get("optional-dependencies", {}).values(),
        *pyproject.get("dependency-groups", {}).values(),
    ]
    for requirements in groups:
        pins.extend(
            pin
            for requirement in requirements
            if isinstance(requirement, str) and (pin := _provider_pin(requirement)) is not None
        )
    revisions = {revision for _, revision in pins}
    if len(revisions) != 1:
        raise ValueError("Engine core and SDK pins must be coherent across dependency groups")
    return revisions.pop()


def source_provider_revision(module_map: Path) -> str:
    """The explicitly supplied migration map identifies the source checkout root."""
    with (module_map.resolve().parents[2] / "pyproject.toml").open("rb") as stream:
        return active_provider_revision(tomllib.load(stream))


def check_provider_metadata(revision: str, direct_urls: dict) -> None:
    """Both installed owners must attest the active immutable source revision."""
    for name in _PROVIDER_SUBDIRECTORIES:
        commit = direct_urls.get(name, {}).get("vcs_info", {}).get("commit_id")
        if commit != revision:
            raise ValueError(f"installed {name} source revision differs from active Git pin")


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


def _check_provider_aliases(manifest: dict, revision: str) -> None:
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
    direct_urls = {}
    for name in ("quant-platform", "quant-backtest-core", "quant-backtest-engine-client"):
        installed = distribution(name)
        direct_url = json.loads(installed.read_text("direct_url.json") or "{}")
        assert not direct_url.get("dir_info", {}).get("editable", False)
        direct_urls[name] = direct_url
    check_provider_metadata(revision, direct_urls)


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
    _check_provider_aliases(aliases, source_provider_revision(args.module_map))
    from quant_backtest_core.daily import dated_fees as owned_fees
    from quant_backtest_core.daily.types import BacktestLegResult, BacktestPeriodResult

    from quant_platform._portfolio import types as legacy_types
    from quant_platform.backtest.legacy import dated_fees as public_fees

    assert public_fees.DatedTradeFeeModel is owned_fees.DatedTradeFeeModel
    assert legacy_types.BacktestLegResult is BacktestLegResult
    assert legacy_types.BacktestPeriodResult is BacktestPeriodResult
    owned_accounting = importlib.import_module("quant_backtest_core.daily.trade_accounting")
    for module_name in (
        "quant_platform._portfolio.backends.trade_accounting",
        "quant_platform.backtest.legacy.backends.trade_accounting",
        "portfolio_backtester.backends.trade_accounting",
    ):
        public_accounting = importlib.import_module(module_name)
        for name in (
            "TradeCostConfig",
            "TradeAccounting",
            "_clean_weights",
            "drift_weights",
            "compute_trade_accounting",
            "compute_trade_accounting_frame",
        ):
            assert getattr(public_accounting, name) is getattr(owned_accounting, name)
    installed = distribution("quant-platform")
    forbidden = {"torch", "xgboost", "sklearn", "alpha_research.backends.qlib"}
    assert not forbidden & set(sys.modules)
    assert installed.version == "0.3.0"
    print("Regular wheel: neutral imports, owner aliases and mandatory provider boundary verified")


if __name__ == "__main__":
    main()
