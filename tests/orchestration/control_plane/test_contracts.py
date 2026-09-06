import json
from dataclasses import FrozenInstanceError

import pytest

from strategy_pipeline.control_plane.contracts import (
    ArtifactRef,
    HandoffRequest,
    PublicationRequest,
    RunReceipt,
    RunRequest,
)


def test_public_contracts_are_immutable_and_json_safe():
    artifact = ArtifactRef(kind="result", uri="memory://result", digest="abc", producer="owner")
    request = RunRequest(run_id="run-1", inputs=(artifact,))
    publication = PublicationRequest(run_id="run-1", artifact=artifact)
    handoff = HandoffRequest(run_id="run-1", artifacts=(artifact,), destination="memory://handoff")
    receipt = RunReceipt(run_id="run-1", status="published", artifacts=(artifact,))

    with pytest.raises(FrozenInstanceError):
        artifact.uri = "memory://other"

    assert json.dumps(
        {
            "request": request.to_dict(),
            "publication": publication.to_dict(),
            "handoff": handoff.to_dict(),
            "receipt": receipt.to_dict(),
        }
    )


def test_public_contracts_reject_empty_identity_fields():
    with pytest.raises(ValueError, match="run_id"):
        RunRequest(run_id="", inputs=())
    with pytest.raises(ValueError, match="destination"):
        HandoffRequest(run_id="run-1", artifacts=(), destination="")

