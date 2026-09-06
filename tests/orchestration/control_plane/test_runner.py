from strategy_pipeline.control_plane.contracts import (
    ArtifactRef,
    PublicationRequest,
    RunRequest,
)
from strategy_pipeline.control_plane.runner import run


def _artifact(kind: str = "result") -> ArtifactRef:
    return ArtifactRef(kind=kind, uri=f"memory://{kind}", digest="abc", producer="owner")


def test_run_calls_owner_then_publisher_and_returns_published_receipt():
    calls: list[str] = []
    produced = _artifact()
    published = _artifact("published")

    class Owner:
        def run(self, request: RunRequest) -> ArtifactRef:
            calls.append(request.run_id)
            return produced

    class Publisher:
        def publish(self, request: PublicationRequest) -> ArtifactRef:
            calls.append(request.artifact.kind)
            return published

    receipt = run(RunRequest("run-1", ()), owner=Owner(), publisher=Publisher())

    assert calls == ["run-1", "result"]
    assert receipt.to_dict() == {
        "run_id": "run-1",
        "status": "published",
        "artifacts": [published.to_dict()],
        "failure_category": None,
        "failure_message": None,
    }


def test_run_redacts_owner_and_publication_exception_details():
    class FailingOwner:
        def run(self, _request: RunRequest) -> ArtifactRef:
            raise RuntimeError("private path /srv/strategy-secret")

    owner_failure = run(RunRequest("run-1", ()), owner=FailingOwner(), publisher=None)
    assert owner_failure.failure_category == "owner_failure"
    assert owner_failure.failure_message == "owner execution failed"
    assert "strategy-secret" not in str(owner_failure.to_dict())

    class FailingPublisher:
        def publish(self, _request: PublicationRequest) -> ArtifactRef:
            raise RuntimeError("private path /srv/strategy-secret")

    class Owner:
        def run(self, _request: RunRequest) -> ArtifactRef:
            return _artifact()

    publication_failure = run(
        RunRequest("run-1", ()), owner=Owner(), publisher=FailingPublisher()
    )
    assert publication_failure.failure_category == "publication_failure"
    assert publication_failure.failure_message == "artifact publication failed"
    assert "strategy-secret" not in str(publication_failure.to_dict())

