"""Active provider pins come from source dependencies, never frozen migration receipts."""

import copy
import json
import tomllib
from pathlib import Path

import pytest
import yaml

from scripts import check_platform_wheel as wheel

ROOT = Path(__file__).resolve().parents[1]
SHA = "d" * 40


def dependency(name, revision=SHA, path=None):
    path = (
        path
        or {
            "quant-backtest-core": "packages/core",
            "quant-backtest-engine-client": "packages/python-sdk",
        }[name]
    )
    return (
        f"{name} @ git+https://github.com/runchengxie/quant-backtest-engine.git@"
        f"{revision}#subdirectory={path}"
    )


def source():
    return {
        "project": {
            "dependencies": [
                dependency("quant-backtest-core"),
                dependency("quant-backtest-engine-client"),
            ]
        }
    }


def test_active_revision_uses_coherent_mandatory_source_pins():
    value = source()
    value["project"]["optional-dependencies"] = {
        "engine": [dependency("quant-backtest-engine-client")]
    }
    assert wheel.active_provider_revision(value) == SHA


@pytest.mark.parametrize(
    "mutation,match",
    [
        ("mismatch", "coherent"),
        ("short", "40-character"),
        ("branch", "40-character"),
        ("path", "subdirectory"),
        ("missing", "mandatory"),
        ("optional_mismatch", "coherent"),
    ],
)
def test_active_revision_rejects_ambiguous_or_incompatible_declared_pins(mutation, match):
    value = source()
    deps = value["project"]["dependencies"]
    if mutation == "mismatch":
        deps[1] = dependency("quant-backtest-engine-client", "e" * 40)
    elif mutation in ("short", "branch"):
        deps[0] = dependency("quant-backtest-core", "123abcd" if mutation == "short" else "main")
    elif mutation == "path":
        deps[0] = dependency("quant-backtest-core", path="core")
    elif mutation == "missing":
        deps.pop()
    else:
        value["project"]["optional-dependencies"] = {
            "engine": [dependency("quant-backtest-engine-client", "e" * 40)]
        }
    with pytest.raises(ValueError, match=match):
        wheel.active_provider_revision(value)


def test_source_location_comes_from_explicit_module_map_not_script_checkout(tmp_path):
    mapping = tmp_path / "other-source/docs/migration/portfolio-module-map.json"
    mapping.parent.mkdir(parents=True)
    mapping.write_text("{}")
    (mapping.parents[2] / "pyproject.toml").write_text(
        "[project]\ndependencies = " + json.dumps(source()["project"]["dependencies"]) + "\n"
    )
    assert wheel.source_provider_revision(mapping) == SHA


@pytest.mark.parametrize("commit", [None, "e" * 40, "main", "d" * 7])
def test_installed_provider_must_prove_matching_vcs_commit(commit):
    urls = {
        name: {"vcs_info": {"commit_id": SHA}}
        for name in ("quant-backtest-core", "quant-backtest-engine-client")
    }
    urls["quant-backtest-core"] = {} if commit is None else {"vcs_info": {"commit_id": commit}}
    with pytest.raises(ValueError, match="installed"):
        wheel.check_provider_metadata(SHA, urls)


def test_matching_installed_provider_metadata_passes_without_rewriting_historical_receipts():
    urls = {
        name: {"vcs_info": {"commit_id": SHA}}
        for name in ("quant-backtest-core", "quant-backtest-engine-client")
    }
    previous = copy.deepcopy(urls)
    wheel.check_provider_metadata(SHA, urls)
    assert previous == urls


def test_workflow_native_and_session_providers_match_active_dependency_revision_and_layout():
    value = tomllib.loads((ROOT / "pyproject.toml").read_text())
    revision = wheel.active_provider_revision(value)
    workflow = yaml.safe_load((ROOT / ".github/workflows/ci.yml").read_text())
    for job, directory in (
        ("rust-microstructure", "native-engine-provider"),
        ("engine-sessions", "session-engine-provider"),
    ):
        steps = workflow["jobs"][job]["steps"]
        checkout = next(
            step["with"] for step in steps if step.get("with", {}).get("path") == directory
        )
        assert checkout["ref"] == revision
    commands = "\n".join(
        step.get("run", "") for step in workflow["jobs"]["rust-microstructure"]["steps"]
    )
    assert "native-engine-provider/packages/microstructure-native/Cargo.toml" in commands
    assert "TICKNET_REQUIRE_RUST=1" in commands
    assert "tests/microstructure tests/test_engine_microstructure_compatibility.py" in commands
