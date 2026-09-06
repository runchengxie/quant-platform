from __future__ import annotations

import pytest

from strategy_pipeline.config import deep_merge, resolve_config


def test_deep_merge_preserves_nested_base_values() -> None:
    assert deep_merge({"model": {"name": "linear", "seed": 1}}, {"model": {"seed": 7}}) == {
        "model": {"name": "linear", "seed": 7}
    }


def test_resolve_config_supports_alias_and_relative_extends(tmp_path) -> None:
    base = tmp_path / "base.yml"
    base.write_text("model:\n  name: linear\n  seed: 1\n", encoding="utf-8")
    child = tmp_path / "child.yml"
    child.write_text("extends: base.yml\nmodel:\n  seed: 7\n", encoding="utf-8")

    resolved = resolve_config(child, aliases={"default": "child.yml"}, search_paths=[str(tmp_path)])
    assert resolved.data == {"model": {"name": "linear", "seed": 7}}

    aliased = resolve_config("default", aliases={"default": "child.yml"}, search_paths=[str(tmp_path)])
    assert aliased.data == resolved.data


def test_resolve_config_falls_back_to_filename_in_search_roots(tmp_path) -> None:
    base = tmp_path / "base.yml"
    base.write_text("model:\n  name: linear\n", encoding="utf-8")
    child = tmp_path / "nested" / "child.yml"
    child.parent.mkdir()
    child.write_text("extends: old-layout/base.yml\nmodel:\n  seed: 7\n", encoding="utf-8")

    resolved = resolve_config(child, search_paths=[str(tmp_path)])

    assert resolved.data == {"model": {"name": "linear", "seed": 7}}


def test_resolve_config_rejects_circular_extends(tmp_path) -> None:
    first = tmp_path / "first.yml"
    second = tmp_path / "second.yml"
    first.write_text("extends: second.yml\n", encoding="utf-8")
    second.write_text("extends: first.yml\n", encoding="utf-8")

    with pytest.raises(SystemExit, match="Circular extends"):
        resolve_config(first)


def test_resolve_config_accepts_an_injected_normalizer(tmp_path) -> None:
    config = tmp_path / "config.yml"
    config.write_text("legacy: true\n", encoding="utf-8")

    def normalize(data):
        normalized = dict(data)
        normalized["normalized"] = normalized.pop("legacy")
        return normalized

    resolved = resolve_config(config, normalizer=normalize)
    assert resolved.data == {"normalized": True}
