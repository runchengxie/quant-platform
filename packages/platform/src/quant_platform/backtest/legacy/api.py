"""Module alias preserving implementation identity during compatibility migration."""

import sys
from importlib import import_module
from typing import TYPE_CHECKING

__all__ = [
    "Any",
    "BacktestSpec",
    "BpsCostModel",
    "EntryPolicy",
    "ExecutionModel",
    "ExitPolicy",
    "GroupCap",
    "Literal",
    "MaxNewNamesShortfallPolicy",
    "NoSlippageModel",
    "SelectionConstraints",
    "SelectionPricePolicy",
    "StrategySpec",
    "TargetWeightPolicy",
    "_assemble_topk_spec",
    "_attach_reproducibility_to_bundle",
    "annotations",
    "backtest_topk",
    "collect_reproducibility",
    "run_backtest",
    "write_run_metadata",
]

if TYPE_CHECKING:
    from quant_platform._portfolio.api import (
        Any,
        BacktestSpec,
        BpsCostModel,
        EntryPolicy,
        ExecutionModel,
        ExitPolicy,
        GroupCap,
        Literal,
        MaxNewNamesShortfallPolicy,
        NoSlippageModel,
        SelectionConstraints,
        SelectionPricePolicy,
        StrategySpec,
        TargetWeightPolicy,
        _assemble_topk_spec,
        _attach_reproducibility_to_bundle,
        annotations,
        backtest_topk,
        collect_reproducibility,
        run_backtest,
        write_run_metadata,
    )

sys.modules[__name__] = import_module("quant_platform._portfolio.api")
