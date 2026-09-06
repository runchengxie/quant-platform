import pytest

from strategy_pipeline.control_plane.contracts import ArtifactRef, HandoffRequest
from strategy_pipeline.control_plane.handoff import publish_handoff


def test_publish_handoff_delegates_validated_request():
    artifact = ArtifactRef("target", "memory://target", "abc", "owner")
    request = HandoffRequest("run-1", (artifact,), "memory://handoff")
    seen: list[str] = []

    class Publisher:
        def publish(self, received: HandoffRequest) -> ArtifactRef:
            seen.append(received.destination)
            return ArtifactRef("handoff", "memory://handoff", "def", "publisher")

    result = publish_handoff(request, Publisher())

    assert seen == ["memory://handoff"]
    assert result.kind == "handoff"


def test_handoff_rejects_an_empty_artifact_list():
    with pytest.raises(ValueError, match="artifacts"):
        HandoffRequest("run-1", (), "memory://handoff")

