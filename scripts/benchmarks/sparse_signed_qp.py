"""Synthetic sparse QP scale evidence; run with the sparse extra installed.

Print JSON to stdout; redirect retained results to the project's DATA_ROOT.
No performance threshold: hardware, build, thread environment and three cold /
warm repetitions are recorded so results can be interpreted on their host.
"""

import contextlib
import io
import json
import os
import platform
import resource
import subprocess
import time
from dataclasses import replace
from pathlib import Path

import numpy as np
import osqp
import pandas as pd
import scipy

from quant_platform.portfolio.sparse_signed_optimization import (
    SparseSignedOptimizationRequest,
    SparseSignedOptimizer,
)


def request(n):
    rng = np.random.default_rng(8321)
    assets, factors = pd.Index([f"a{i}" for i in range(n)]), pd.Index(["risk1", "risk2"])

    def series(value):
        return pd.Series(value, index=assets, dtype=float)

    return SparseSignedOptimizationRequest(
        expected_returns=series(rng.normal(0, 0.001, n)),
        risk_loadings=pd.DataFrame(rng.normal(0, 0.1, (n, 2)), index=assets, columns=factors),
        factor_covariance=pd.DataFrame(np.eye(2) * 0.01, index=factors, columns=factors),
        specific_variance=series(0.05),
        current_weights=series(0),
        lower_bounds=series(-0.02),
        upper_bounds=series(0.02),
        trade_costs=series(0.0001),
        borrow_costs=series(0.0001),
        holding_costs=series(0.0001),
        factor_loadings=pd.DataFrame({"beta": np.ones(n)}, index=assets),
        factor_bounds={"beta": (-0.1, 0.1)},
        gross_limit=1,
        net_target=0,
        risk_aversion=1,
        horizon_days=5,
        units="horizon_decimal",
        assumptions="Synthetic scale example",
        information_time=pd.Timestamp("2026-01-01", tz="UTC"),
        decision_time=pd.Timestamp("2026-01-02", tz="UTC"),
    )


def objective(r, result):
    return (
        r.risk_aversion * result.variance / 2
        - result.expected_return
        + result.trade_cost
        + result.borrow_cost
        + result.holding_cost
    )


def benchmark(n):
    r = request(n)
    updated = replace(r, expected_returns=r.expected_returns * 0.95)
    repetitions = []
    for _ in range(3):
        solver = SparseSignedOptimizer(backend="osqp", tolerance=1e-11)
        start = time.perf_counter()
        cold = solver.solve(r)
        cold_seconds = time.perf_counter() - start
        start = time.perf_counter()
        warm = solver.solve(updated)
        warm_seconds = time.perf_counter() - start
        independent = SparseSignedOptimizer(backend="osqp", tolerance=1e-11).solve(updated)
        if any(result.status != "optimal" for result in (cold, warm, independent)):
            raise RuntimeError([result.message for result in (cold, warm, independent)])
        delta = abs(objective(updated, warm) - objective(updated, independent))
        if delta > 1e-7:
            raise RuntimeError(f"Warm/cold objective mismatch: {delta}")
        repetitions.append(
            dict(
                cold_seconds=cold_seconds,
                warm_seconds=warm_seconds,
                objective_delta=delta,
                max_residual=max(warm.residuals.values()),
                **solver.structure_stats,
            )
        )
    return {"assets": n, "risk_factors": 2, "repetitions": repetitions}


def host_info():
    cpu = platform.processor()
    if not cpu and Path("/proc/cpuinfo").exists():
        for line in Path("/proc/cpuinfo").read_text().splitlines():
            if line.startswith("model name"):
                cpu = line.split(":", 1)[1].strip()
                break
    return {
        "cpu_model": cpu,
        "machine": platform.machine(),
        "source_revision": subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
        "source_dirty": bool(
            subprocess.check_output(["git", "status", "--porcelain"], text=True).strip()
        ),
    }


def main():
    output = io.StringIO()
    with contextlib.redirect_stdout(output):
        np.show_config()
    report = {
        "platform": platform.platform(),
        "processor": platform.processor(),
        "cpu_count": os.cpu_count(),
        "python": platform.python_version(),
        "numpy": np.__version__,
        "scipy": scipy.__version__,
        "osqp": osqp.__version__,
        "threads": {
            key: os.environ.get(key)
            for key in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS")
        },
        "numpy_build": output.getvalue(),
        "sizes": [benchmark(n) for n in (100, 500, 1000)],
    }
    report.update(host_info())
    report["peak_rss_kib"] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
