"""Scanners must include the migrated business source trees."""

import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize(
    ("script", "business_source"),
    [
        ("scripts/dev/maintainability_metrics.py", "packages/portfolio-backtester/src/"),
        ("scripts/alpha-research/dev/maintainability_metrics.py", "packages/alpha/src/"),
    ],
)
def test_default_scanner_includes_business_source(script, business_source):
    completed = subprocess.run(
        [sys.executable, script, "--json", "--limit", "100000"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    payload = json.loads(completed.stdout)
    assert any(item["path"].startswith(business_source) for item in payload["largest_files"])


@pytest.mark.parametrize(
    ("script", "legacy_scope"),
    [
        ("scripts/dev/maintainability_metrics.py", "src"),
        ("scripts/alpha-research/dev/maintainability_metrics.py", "src/alpha_research"),
        ("scripts/alpha-research/dev/maintainability_metrics.py", "tests/alpha_research"),
    ],
)
def test_explicit_legacy_scope_remains_accepted(script, legacy_scope):
    completed = subprocess.run(
        [sys.executable, script, "--json", "--scope", legacy_scope],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    assert json.loads(completed.stdout)["roots"] == [legacy_scope]
