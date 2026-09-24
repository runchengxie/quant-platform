from __future__ import annotations

from copy import deepcopy
from datetime import datetime
from zoneinfo import ZoneInfo

import pytest
from research_contracts import (
    ARTIFACT_ENVELOPE_KEY,
    ARTIFACT_ENVELOPE_SCHEMA_VERSION,
    ArtifactEnvelopeV2,
    LegacyArtifactMetadata,
    TargetHandoffContext,
    attach_artifact_envelope_v2,
    read_artifact_envelope,
)

_SHA = "a" * 64


def _envelope_mapping() -> dict[str, object]:
    return {
        "schema_version": ARTIFACT_ENVELOPE_SCHEMA_VERSION,
        "artifact_id": "artifact-1",
        "artifact_type": "portfolio-targets",
        "run_id": "run-1",
        "created_at": "2026-09-25T09:10:00+00:00",
        "producer": {
            "repository": "quant-research",
            "version": "1.2.3",
            "commit": "0123456789abcdef",
            "backend": "native",
            "backend_version": "1.0",
        },
        "configuration_sha256": _SHA,
        "content_sha256": "b" * 64,
        "lineage": [{"artifact_id": "source-1", "sha256": "c" * 64}],
        "target_handoff": {
            "valid_from": "2026-09-25T09:10:00+00:00",
            "expires_at": "2026-09-25T10:10:00+00:00",
            "portfolio_scope": "paper-portfolio",
            "account_scope": "paper-account",
            "policy_reference": "execution-policy-v1",
            "idempotency_scope": "run-1",
        },
        "write_mode": "opt_in",
    }


def test_artifact_envelope_round_trips_nested_metadata() -> None:
    envelope = ArtifactEnvelopeV2.from_mapping(_envelope_mapping())

    assert ArtifactEnvelopeV2.from_mapping(envelope.to_mapping()) == envelope
    assert envelope.to_mapping()["lineage"] == [{"artifact_id": "source-1", "sha256": "c" * 64}]


def test_read_artifact_envelope_reads_wrapped_v2_envelope() -> None:
    envelope = read_artifact_envelope({ARTIFACT_ENVELOPE_KEY: _envelope_mapping()})

    assert isinstance(envelope, ArtifactEnvelopeV2)
    assert envelope.artifact_id == "artifact-1"


def test_read_artifact_envelope_preserves_legacy_payload_by_default() -> None:
    result = read_artifact_envelope({"legacy_field": "value"})

    assert isinstance(result, LegacyArtifactMetadata)
    assert result.payload == {"legacy_field": "value"}


def test_read_artifact_envelope_can_reject_legacy_payload() -> None:
    with pytest.raises(ValueError, match="artifact_envelope is required"):
        read_artifact_envelope({"legacy_field": "value"}, allow_legacy=False)


def test_attach_envelope_preserves_legacy_fields() -> None:
    envelope = ArtifactEnvelopeV2.from_mapping(_envelope_mapping())

    migrated = attach_artifact_envelope_v2({"legacy_field": "value"}, envelope)

    assert migrated["legacy_field"] == "value"
    assert migrated[ARTIFACT_ENVELOPE_KEY] == envelope.to_mapping()


def test_attach_envelope_rejects_existing_envelope_key() -> None:
    envelope = ArtifactEnvelopeV2.from_mapping(_envelope_mapping())

    with pytest.raises(ValueError, match="already exists"):
        attach_artifact_envelope_v2({ARTIFACT_ENVELOPE_KEY: {}}, envelope)


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("schema_version", "research.artifact-envelope.v1", "unsupported artifact envelope schema"),
        ("artifact_id", None, "artifact_id is required"),
        ("created_at", "2026-09-25T09:10:00", "created_at must be timezone-aware"),
        ("content_sha256", "not-a-digest", "content_sha256 must be a lowercase SHA-256 digest"),
        ("write_mode", "implicit", "write_mode must be opt_in"),
        ("producer", [], "producer must be an object"),
        ("lineage", {}, "lineage must be a list"),
        ("lineage", [None], "each lineage item must be an object"),
        ("target_handoff", [], "target_handoff must be an object"),
    ],
)
def test_artifact_envelope_rejects_invalid_mappings(
    field: str, value: object, message: str
) -> None:
    payload = deepcopy(_envelope_mapping())
    payload[field] = value

    with pytest.raises(ValueError, match=message):
        ArtifactEnvelopeV2.from_mapping(payload)


def test_artifact_envelope_rejects_invalid_lineage_digest() -> None:
    payload = _envelope_mapping()
    payload["lineage"] = [{"artifact_id": "source-1", "sha256": "ABC"}]

    with pytest.raises(ValueError, match=r"lineage.sha256 must be a lowercase SHA-256 digest"):
        ArtifactEnvelopeV2.from_mapping(payload)


def test_target_handoff_rejects_expiration_before_start_across_dst_fold() -> None:
    new_york = ZoneInfo("America/New_York")

    with pytest.raises(ValueError, match="expires_at must be after valid_from"):
        TargetHandoffContext(
            valid_from=datetime(2026, 11, 1, 1, 30, tzinfo=new_york, fold=1),
            expires_at=datetime(2026, 11, 1, 1, 45, tzinfo=new_york, fold=0),
            portfolio_scope="paper-portfolio",
            account_scope="paper-account",
            policy_reference="execution-policy-v1",
            idempotency_scope="run-1",
        )
