from strategy_pipeline.control_plane.contracts import ArtifactRef, PublicationRequest
from strategy_pipeline.control_plane.publication import publish_artifact


def test_publish_artifact_delegates_to_injected_writer():
    request = PublicationRequest(
        run_id="run-1",
        artifact=ArtifactRef("result", "memory://result", "abc", "owner"),
    )
    seen: list[str] = []

    def writer(received: PublicationRequest) -> ArtifactRef:
        seen.append(received.run_id)
        return ArtifactRef("published", "memory://published", "def", "publisher")

    result = publish_artifact(request, writer)

    assert seen == ["run-1"]
    assert result.kind == "published"

