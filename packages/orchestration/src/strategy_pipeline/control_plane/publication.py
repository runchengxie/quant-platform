"""Provider-neutral artifact publication boundary."""

from __future__ import annotations

from .contracts import ArtifactRef, PublicationRequest
from .ports import ArtifactWriter


def publish_artifact(request: PublicationRequest, writer: ArtifactWriter) -> ArtifactRef:
    """Delegate publication to an injected writer and validate its result."""

    published = writer(request)
    if not isinstance(published, ArtifactRef):
        raise TypeError("artifact writer must return an ArtifactRef")
    return published
