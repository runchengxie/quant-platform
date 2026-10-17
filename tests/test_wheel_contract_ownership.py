"""Installed wheels must give shared contracts exactly one distribution owner."""

from __future__ import annotations

import csv
import io
import json
import os
import shutil
import subprocess
import sys
import tomllib
import venv
import zipfile
from importlib.metadata import distribution
from pathlib import Path

import pytest
from packaging.requirements import Requirement


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


def _seed_runtime_dependencies(python: Path, requirements: list[str]) -> None:
    """Use installed third-party runtime files, never editable/source paths."""
    target = Path(
        subprocess.check_output(
            [str(python), "-I", "-c", "import sysconfig; print(sysconfig.get_path('purelib'))"],
            text=True,
        ).strip()
    )
    pending = [(requirement, {""}) for requirement in requirements]
    seen: set[tuple[str, frozenset[str]]] = set()
    copied = {"research-contracts"}  # Installed from its own wheel below.
    while pending:
        raw_requirement, parent_extras = pending.pop()
        requirement = Requirement(raw_requirement)
        if requirement.marker and not any(
            requirement.marker.evaluate({"extra": extra}) for extra in parent_extras
        ):
            continue
        name = requirement.name.lower().replace("_", "-")
        key = (name, frozenset(requirement.extras))
        if key in seen or name == "research-contracts":
            continue
        seen.add(key)
        installed = distribution(name)
        direct_url = json.loads(installed.read_text("direct_url.json") or "{}")
        assert not direct_url.get("dir_info", {}).get("editable"), name
        pending.extend((item, requirement.extras or {""}) for item in installed.requires or ())
        if name in copied:
            continue
        copied.add(name)
        for record in installed.files or ():
            relative = Path(record)
            if ".." in relative.parts or relative.suffix == ".pyc":
                continue
            origin = Path(installed.locate_file(record))
            destination = target / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            try:
                os.link(origin, destination)
            except OSError:
                try:
                    destination.symlink_to(origin)
                except OSError:
                    shutil.copy2(origin, destination)


@pytest.mark.parametrize("provider_first", [True, False])
def test_wheels_have_disjoint_contract_ownership(tmp_path: Path, provider_first: bool) -> None:
    root = Path(__file__).resolve().parents[1]
    project = tomllib.loads((root / "pyproject.toml").read_text())
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
    _seed_runtime_dependencies(
        python,
        project["project"]["dependencies"]
        + project["project"]["optional-dependencies"]["ml"]
        + project["project"]["optional-dependencies"]["microstructure"],
    )
    order = (provider, contracts) if provider_first else (contracts, provider)
    for wheel in order:
        subprocess.run(
            [str(python), "-I", "-m", "pip", "install", "--no-index", "--no-deps", str(wheel)],
            cwd=tmp_path,
            check=True,
            capture_output=True,
            text=True,
        )
    packages = project["tool"]["setuptools"]["packages"]
    check = (
        "import importlib\npackages = "
        + repr(packages)
        + "\n"
        + """
from importlib.metadata import distribution
from pathlib import Path
import research_contracts
provider = distribution('quant-platform')
for name in packages:
    module = importlib.import_module(name)
    expected = Path(provider.locate_file(name.replace('.', '/') + '/__init__.py')).resolve()
    assert Path(module.__file__).resolve() == expected, (name, module.__file__)
from alpha_research import style_factors, style_replica
from alpha_research.style_factors import helpers
assert callable(style_factors.compute_factors)
assert callable(helpers.add_new_factors)
assert callable(style_replica.generate_daily_signals)
assert callable(research_contracts.validate_contract_ownership)
owner = distribution('research-contracts')
expected = Path(owner.locate_file('research_contracts/__init__.py')).resolve()
assert Path(research_contracts.__file__).resolve() == expected
provider_files = {str(p) for p in distribution('quant-platform').files if str(p).endswith('.py')}
contract_files = {str(p) for p in owner.files if str(p).endswith('.py')}
assert not provider_files & contract_files
"""
    )
    imports = subprocess.run(
        [str(python), "-I", "-c", check], cwd=tmp_path, capture_output=True, text=True
    )
    assert imports.returncode == 0, imports.stderr
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
