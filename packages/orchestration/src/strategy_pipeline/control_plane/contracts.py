"""Domain-neutral request, artifact, publication, and handoff contracts."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


def _require_text(value: str, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be a non-empty string")
    return value


@dataclass(frozen=True, slots=True)
class ArtifactRef:
    kind: str
    uri: str
    digest: str
    producer: str

    def __post_init__(self) -> None:
        for field in ("kind", "uri", "digest", "producer"):
            _require_text(getattr(self, field), field)

    def to_dict(self) -> dict[str, str]:
        return {
            "kind": self.kind,
            "uri": self.uri,
            "digest": self.digest,
            "producer": self.producer,
        }


@dataclass(frozen=True, slots=True)
class RunRequest:
    run_id: str
    inputs: tuple[ArtifactRef, ...]

    def __post_init__(self) -> None:
        _require_text(self.run_id, "run_id")
        if not all(isinstance(artifact, ArtifactRef) for artifact in self.inputs):
            raise TypeError("inputs must contain only ArtifactRef values")

    def to_dict(self) -> dict[str, Any]:
        return {"run_id": self.run_id, "inputs": [artifact.to_dict() for artifact in self.inputs]}


@dataclass(frozen=True, slots=True)
class PublicationRequest:
    run_id: str
    artifact: ArtifactRef

    def __post_init__(self) -> None:
        _require_text(self.run_id, "run_id")
        if not isinstance(self.artifact, ArtifactRef):
            raise TypeError("artifact must be an ArtifactRef")

    def to_dict(self) -> dict[str, Any]:
        return {"run_id": self.run_id, "artifact": self.artifact.to_dict()}


@dataclass(frozen=True, slots=True)
class HandoffRequest:
    run_id: str
    artifacts: tuple[ArtifactRef, ...]
    destination: str

    def __post_init__(self) -> None:
        _require_text(self.run_id, "run_id")
        _require_text(self.destination, "destination")
        if not self.artifacts:
            raise ValueError("artifacts must contain at least one ArtifactRef")
        if not all(isinstance(artifact, ArtifactRef) for artifact in self.artifacts):
            raise TypeError("artifacts must contain only ArtifactRef values")

    def to_dict(self) -> dict[str, Any]:
        return {
            "run_id": self.run_id,
            "artifacts": [artifact.to_dict() for artifact in self.artifacts],
            "destination": self.destination,
        }


@dataclass(frozen=True, slots=True)
class RunReceipt:
    run_id: str
    status: str
    artifacts: tuple[ArtifactRef, ...] = ()
    failure_category: str | None = None
    failure_message: str | None = None

    def __post_init__(self) -> None:
        _require_text(self.run_id, "run_id")
        _require_text(self.status, "status")
        if not all(isinstance(artifact, ArtifactRef) for artifact in self.artifacts):
            raise TypeError("artifacts must contain only ArtifactRef values")

    def to_dict(self) -> dict[str, Any]:
        return {
            "run_id": self.run_id,
            "status": self.status,
            "artifacts": [artifact.to_dict() for artifact in self.artifacts],
            "failure_category": self.failure_category,
            "failure_message": self.failure_message,
        }
