"""Installed wheels must give shared contracts exactly one distribution owner."""

from __future__ import annotations

import csv
import io
import os
import shutil
import subprocess
import sys
import venv
import zipfile
from pathlib import Path

import pytest


def _build_wheel(source: Path, output: Path) -> Path:
    subprocess.run(
        [
            sys.executable,
            "-c",
            "from setuptools.build_meta import build_wheel; import sys; build_wheel(sys.argv[1])",
            str(output),
        ],
        cwd=source,
        check=True,
        capture_output=True,
        text=True,
    )
    return next(output.glob("*.whl"))


def _python_files(wheel: Path) -> set[str]:
    with zipfile.ZipFile(wheel) as archive:
        record = next(name for name in archive.namelist() if name.endswith(".dist-info/RECORD"))
        rows = csv.reader(io.StringIO(archive.read(record).decode()))
        return {row[0] for row in rows if row[0].endswith(".py")}


@pytest.mark.parametrize("provider_first", [True, False])
def test_wheels_have_disjoint_contract_ownership(tmp_path: Path, provider_first: bool) -> None:
    root = Path(__file__).resolve().parents[1]
    source = tmp_path / "source"
    source.mkdir()
    shutil.copy2(root / "pyproject.toml", source)
    shutil.copytree(
        root / "packages",
        source / "packages",
        ignore=shutil.ignore_patterns(
            "__pycache__",
            "*.egg-info",
            "build",
            "target",
            ".venv",
        ),
    )
    provider = _build_wheel(source, tmp_path / "provider-wheel")
    contracts = _build_wheel(source / "packages/research-contracts", tmp_path / "contracts-wheel")
    provider_files = _python_files(provider)
    contracts_files = _python_files(contracts)
    assert contracts_files
    assert not provider_files & contracts_files
    assert not any(path.startswith("research_contracts/") for path in provider_files)
    with zipfile.ZipFile(provider) as archive:
        metadata = next(name for name in archive.namelist() if name.endswith(".dist-info/METADATA"))
        assert "Requires-Dist: research-contracts>=0.1.0" in archive.read(metadata).decode()

    environment = tmp_path / "environment"
    venv.EnvBuilder(with_pip=True).create(environment)
    python = environment / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    order = (provider, contracts) if provider_first else (contracts, provider)
    for wheel in order:
        subprocess.run(
            [str(python), "-I", "-m", "pip", "install", "--no-index", "--no-deps", str(wheel)],
            cwd=tmp_path,
            check=True,
            capture_output=True,
            text=True,
        )
    check = """
from importlib.metadata import distribution
from pathlib import Path
import research_contracts
assert callable(research_contracts.validate_contract_ownership)
owner = distribution('research-contracts')
expected = Path(owner.locate_file('research_contracts/__init__.py')).resolve()
assert Path(research_contracts.__file__).resolve() == expected
provider_files = {str(p) for p in distribution('quant-platform').files if str(p).endswith('.py')}
contract_files = {str(p) for p in owner.files if str(p).endswith('.py')}
assert not provider_files & contract_files
"""
    subprocess.run(
        [str(python), "-I", "-c", check], cwd=tmp_path, check=True, capture_output=True, text=True
    )
    subprocess.run(
        [str(python), "-I", "-m", "pip", "uninstall", "-y", "quant-platform"],
        cwd=tmp_path,
        check=True,
        capture_output=True,
        text=True,
    )
    subprocess.run(
        [
            str(python),
            "-I",
            "-c",
            "import research_contracts; "
            "assert callable(research_contracts.validate_contract_ownership)",
        ],
        cwd=tmp_path,
        check=True,
        capture_output=True,
        text=True,
    )
