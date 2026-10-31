"""Check public owners and compatibility aliases in a regular installed wheel."""

from __future__ import annotations

import argparse
import importlib
import importlib.util
import json
import sys
from importlib.metadata import distribution
from pathlib import Path


def _check_clean_imports(engine_enabled: bool) -> None:
    import quant_platform
    from quant_platform.backtest.contracts import CanonicalBacktestResult
    from quant_platform.backtest.ledger import UnifiedLedger

    assert CanonicalBacktestResult and UnifiedLedger
    assert not any(name.startswith("quant_platform._portfolio") for name in sys.modules)
    from quant_platform.analytics.metrics import summarize_ic

    assert summarize_ic
    assert not any(
        name.startswith("quant_platform._portfolio.execution_sim") for name in sys.modules
    )
    assert not any(name.startswith("portfolio_backtester") for name in sys.modules)
    assert "site-packages" in Path(quant_platform.__file__).parts
    assert (
        importlib.util.find_spec("quant_backtest_engine") is not None
        if engine_enabled
        else importlib.util.find_spec("quant_backtest_engine") is None
    )


def _check_aliases(mapping: dict, engine_enabled: bool) -> None:
    for old, entry in mapping.items():
        modern = entry["public_module"] == "quant_platform.backtest.engine_sessions"
        if modern and not engine_enabled:
            try:
                importlib.import_module(old)
            except ImportError as error:
                assert "quant-platform[engine]" in str(error)
            else:
                raise AssertionError("Engine adapter must request its optional SDK")
            continue
        old_module = importlib.import_module(old)
        implementation = importlib.import_module(entry["implementation_module"])
        public = importlib.import_module(entry["public_module"])
        if hasattr(old_module, "__path__"):
            for name in getattr(old_module, "__all__", ()):
                assert getattr(old_module, name) is getattr(implementation, name)
        else:
            assert old_module is implementation
            assert public is implementation


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--module-map", type=Path, required=True)
    parser.add_argument("--engine-enabled", action="store_true")
    args = parser.parse_args()
    _check_clean_imports(args.engine_enabled)
    _check_aliases(json.loads(args.module_map.read_text()), args.engine_enabled)
    installed = distribution("quant-platform")
    forbidden = {"torch", "xgboost", "sklearn", "alpha_research.backends.qlib"}
    assert not forbidden & set(sys.modules)
    assert installed.version == "0.0.1"
    print("Regular wheel: neutral imports, owner aliases and optional engine boundary verified")


if __name__ == "__main__":
    main()
