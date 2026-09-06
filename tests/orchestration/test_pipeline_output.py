from __future__ import annotations

from strategy_pipeline.pipeline import output


def test_persist_run_outputs_preserves_owner_callback_order(monkeypatch):
    events: list[object] = []
    monkeypatch.setattr(
        output,
        "write_run_artifacts",
        lambda *, context: (
            events.append(("artifacts", context)) or {"path": "run.json"}
        ),
    )

    def evidence_builder(*, context, artifacts):
        events.append(("evidence", dict(artifacts)))
        artifacts["evidence"] = "evidence.json"

    def summary_builder(*, context, artifacts):
        events.append(("summary", dict(artifacts)))
        return {"artifacts": dict(artifacts)}

    def metadata_writer(*, context, summary):
        events.append(("metadata", summary))

    artifacts = output.persist_run_outputs(
        context={"SAVE_ARTIFACTS": True},
        evidence_builder=evidence_builder,
        summary_builder=summary_builder,
        metadata_writer=metadata_writer,
    )

    assert artifacts == {"path": "run.json", "evidence": "evidence.json"}
    assert [event[0] for event in events] == [
        "artifacts",
        "evidence",
        "summary",
        "metadata",
    ]
    assert events[-1][1]["artifacts"]["evidence"] == "evidence.json"


def test_persist_run_outputs_skips_all_work_when_disabled(monkeypatch):
    def fail_if_called(**_kwargs):
        raise AssertionError("output callbacks must not run")

    monkeypatch.setattr(output, "write_run_artifacts", fail_if_called)
    assert (
        output.persist_run_outputs(
            context={"SAVE_ARTIFACTS": False},
            summary_builder=fail_if_called,
            metadata_writer=fail_if_called,
            evidence_builder=fail_if_called,
        )
        == {}
    )
