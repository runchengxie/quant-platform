import pytest

from strategy_pipeline.control_plane.output_context import (
    OutputContext,
    build_output_context,
)


def _build(**overrides):
    fields = {
        "loaded": {"run_dir": "/tmp/run"},
        "universe_inputs": {},
        "date_label_settings": {},
        "eval_settings": {},
        "universe_filters": {},
        "runtime_settings": {},
        "run_artifacts": {},
        "panel_state": {},
        "dataset_state": {},
        "split_state": {},
        "extras": {},
    }
    fields.update(overrides)
    return build_output_context(**fields)


def test_output_context_is_a_flat_mapping():
    context = _build()
    assert isinstance(context, OutputContext)
    assert context["run_dir"] == "/tmp/run"
    assert context.as_dict() == dict(context)


def test_output_context_rejects_unregistered_conflicts():
    with pytest.raises(ValueError, match="OutputContext key conflict"):
        _build(universe_inputs={"run_dir": "/tmp/other"})


def test_output_context_allows_registered_output_dir_override():
    context = _build(
        eval_settings={"OUTPUT_DIR": "resolved"},
        run_artifacts={"OUTPUT_DIR": "final"},
    )
    assert context["OUTPUT_DIR"] == "final"
