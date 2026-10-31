"""Module alias preserving implementation identity during compatibility migration."""

import sys
from importlib import import_module
from typing import TYPE_CHECKING

__all__ = [
    "DEFAULT_PARTICIPATION_RATES",
    "DEFAULT_PORTFOLIO_VALUES",
    "THRESHOLD_PROFILES",
    "Any",
    "add_capacity_report_args",
    "annotations",
    "build_capacity_report",
    "capacity_cfg",
    "coerce_liquidity_cols",
    "execution_sim_raw",
    "float_grid",
    "json_default",
    "parse_csv_floats",
    "read_json_mapping",
    "read_tca_evidence",
    "read_yaml_mapping",
    "resolve_path",
    "resolve_positions_path",
    "resolve_pricing_path",
    "run",
]

if TYPE_CHECKING:
    from quant_platform._portfolio._capacity_report_cli import (
        DEFAULT_PARTICIPATION_RATES,
        DEFAULT_PORTFOLIO_VALUES,
        THRESHOLD_PROFILES,
        Any,
        add_capacity_report_args,
        annotations,
        build_capacity_report,
        capacity_cfg,
        coerce_liquidity_cols,
        execution_sim_raw,
        float_grid,
        json_default,
        parse_csv_floats,
        read_json_mapping,
        read_tca_evidence,
        read_yaml_mapping,
        resolve_path,
        resolve_positions_path,
        resolve_pricing_path,
        run,
    )

sys.modules[__name__] = import_module("quant_platform._portfolio._capacity_report_cli")
