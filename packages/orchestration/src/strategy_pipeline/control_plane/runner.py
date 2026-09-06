"""Deterministic owner-to-publication orchestration."""

from __future__ import annotations

from .contracts import PublicationRequest, RunReceipt, RunRequest
from .ports import ArtifactPublisher, RunOwner


def run(
    request: RunRequest,
    *,
    owner: RunOwner,
    publisher: ArtifactPublisher | None,
) -> RunReceipt:
    """Run one owner operation and publish its artifact with safe failures."""

    try:
        produced = owner.run(request)
    except Exception:  # noqa: BLE001 - redact all owner implementation failures
        return RunReceipt(
            run_id=request.run_id,
            status="failed",
            failure_category="owner_failure",
            failure_message="owner execution failed",
        )

    try:
        if publisher is None:
            raise RuntimeError("publisher is required")
        published = publisher.publish(PublicationRequest(request.run_id, produced))
    except Exception:  # noqa: BLE001 - redact all publisher implementation failures
        return RunReceipt(
            run_id=request.run_id,
            status="failed",
            failure_category="publication_failure",
            failure_message="artifact publication failed",
        )

    return RunReceipt(run_id=request.run_id, status="published", artifacts=(published,))
