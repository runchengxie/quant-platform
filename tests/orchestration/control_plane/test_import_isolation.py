import builtins
import importlib


def test_control_plane_imports_without_owner_packages(monkeypatch):
    blocked = {
        "alpha_research",
        "market_data_platform",
        "portfolio_backtester",
        "strategy_app",
        "strategy_pipeline_internal",
        "rqdatac",
    }
    original_import = builtins.__import__

    def guarded_import(name, *args, **kwargs):
        if name.split(".", 1)[0] in blocked:
            raise ModuleNotFoundError(name)
        return original_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", guarded_import)
    contracts = importlib.import_module("strategy_pipeline.control_plane.contracts")
    ports = importlib.import_module("strategy_pipeline.control_plane.ports")

    assert contracts.ArtifactRef
    assert ports.RunOwner

