from __future__ import annotations

import importlib
import importlib.util
import json

import pandas as pd
import pytest


def _api():
    assert importlib.util.find_spec("quant_platform.scenarios"), "scenario API is missing"
    return importlib.import_module("quant_platform.scenarios")


@pytest.mark.parametrize(
    "name", ["null_signal", "industry_confound", "delayed_revision", "partial_fill", "sequence_gap"]
)
def test_scenario_round_trip_and_deterministic_hashes(tmp_path, name):
    api = _api()
    bundle = api.build_scenario(name, seed=7)
    first = api.write_scenario(bundle, tmp_path / "first")
    second = api.write_scenario(api.build_scenario(name, seed=7), tmp_path / "second")
    assert first.read_bytes() == second.read_bytes()
    loaded = api.read_scenario(first)
    assert loaded.truth == bundle.truth
    assert loaded.seed == 7
    assert loaded.name == name
    assert set(loaded.frames) == set(bundle.frames)
    for key, frame in bundle.frames.items():
        pd.testing.assert_frame_equal(loaded.frames[key], frame)


def test_seed_changes_inputs_and_refuses_overwrite(tmp_path):
    api = _api()
    first = api.write_scenario(api.build_scenario("null_signal", seed=7), tmp_path / "first")
    second = api.write_scenario(api.build_scenario("null_signal", seed=8), tmp_path / "second")
    assert json.loads(first.read_text())["inventory"] != json.loads(second.read_text())["inventory"]
    with pytest.raises(FileExistsError):
        api.write_scenario(api.build_scenario("null_signal"), tmp_path / "first")


@pytest.mark.parametrize("mutation", ["tamper", "missing", "traversal", "schema", "duplicate"])
def test_invalid_artifacts_fail_before_consumption(tmp_path, mutation):
    api = _api()
    manifest = api.write_scenario(api.build_scenario("null_signal"), tmp_path / "bundle")
    payload = json.loads(manifest.read_text())
    item = payload["inventory"][0]
    source = manifest.parent / item["path"]
    if mutation == "tamper":
        source.write_text("invalid data")
    elif mutation == "missing":
        source.unlink()
    elif mutation == "traversal":
        item["path"] = "../outside.csv"
    elif mutation == "schema":
        payload["schema_version"] = "unknown"
    else:
        payload["inventory"].append(item)
    manifest.write_text(json.dumps(payload))
    with pytest.raises((ValueError, FileNotFoundError)):
        api.read_scenario(manifest)


def test_unknown_scenario_and_invalid_seed_rejected():
    api = _api()
    with pytest.raises(ValueError):
        api.build_scenario("missing")
    with pytest.raises(ValueError):
        api.build_scenario("null_signal", seed=-1)
