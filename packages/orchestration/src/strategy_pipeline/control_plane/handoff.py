"""Provider-neutral artifact handoff boundary."""

from __future__ import annotations

from .contracts import ArtifactRef, HandoffRequest
from .ports import HandoffPublisher


def publish_handoff(request: HandoffRequest, publisher: HandoffPublisher) -> ArtifactRef:
    """Publish a validated handoff through an injected destination adapter."""

    published = publisher.publish(request)
    if not isinstance(published, ArtifactRef):
        raise TypeError("handoff publisher must return an ArtifactRef")
    return published
