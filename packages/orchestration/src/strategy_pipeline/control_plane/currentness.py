"""Domain-neutral input currentness policy for publication control."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from dataclasses import asdict, dataclass
from typing import Literal

PublicationTier = Literal["production", "research"]


@dataclass(frozen=True, slots=True)
class PublicationCurrentnessPolicy:
    """Rules for deciding whether an owner-provided input bundle is current enough."""

    publication_tier: PublicationTier = "production"
    allow_stale_research: bool = True
    require_current_production: bool = True

    def __post_init__(self) -> None:
        if self.publication_tier not in {"production", "research"}:
            raise ValueError("publication_tier must be production or research")

    @property
    def require_current(self) -> bool:
        return self.publication_tier == "production" and self.require_current_production

    @property
    def policy_id(self) -> str:
        payload = {"schema_version": "publication.currentness.v1", **asdict(self)}
        digest = hashlib.sha256(
            json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()[:16]
        return f"publication.currentness.v1:{digest}"

    def to_dict(self) -> dict[str, object]:
        return {
            "schema_version": "publication.currentness.v1",
            "policy_id": self.policy_id,
            **asdict(self),
        }


@dataclass(frozen=True, slots=True)
class PublicationCurrentness:
    """Auditable result of applying a currentness policy to an input bundle."""

    status: str
    source_date: str
    signal_date: str
    required_input_date: str
    input_source: str | None
    current_as_of: str
    max_input_date: str | None
    require_current: bool
    input_mode: str
    input_count: int | None
    input_policy_id: str | None
    reasons: tuple[str, ...]

    @property
    def ready(self) -> bool:
        return self.status == "ready"

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def _text(availability: Mapping[str, object], key: str) -> str:
    return str(availability.get(key) or "")


def evaluate_input_currentness(
    availability: Mapping[str, object],
    policy: PublicationCurrentnessPolicy,
) -> PublicationCurrentness:
    """Apply release-currentness rules without revalidating owner artifacts."""

    raw_issues = availability.get("issues")
    reasons = (
        [str(issue) for issue in raw_issues]
        if isinstance(raw_issues, (list, tuple))
        else []
    )
    if availability.get("available") is not True:
        reasons.append("owner input availability is not passed")
    if policy.require_current and availability.get("current_as_of") != availability.get(
        "source_date"
    ):
        reasons.append(
            f"input current_as_of is {_text(availability, 'current_as_of')}, "
            f"expected {_text(availability, 'source_date')}"
        )
    if (
        policy.publication_tier == "research"
        and not policy.allow_stale_research
        and availability.get("current_as_of") != availability.get("source_date")
    ):
        reasons.append("research publication policy forbids stale inputs")
    return PublicationCurrentness(
        status="ready" if not reasons else "unavailable",
        source_date=_text(availability, "source_date"),
        signal_date=_text(availability, "signal_date"),
        required_input_date=_text(availability, "required_input_date"),
        input_source=str(availability.get("input_source"))
        if availability.get("input_source") is not None
        else None,
        current_as_of=_text(availability, "current_as_of"),
        max_input_date=str(availability.get("max_input_date"))
        if availability.get("max_input_date") is not None
        else None,
        require_current=policy.require_current,
        input_mode=_text(availability, "input_mode"),
        input_count=(
            int(availability["input_count"])
            if isinstance(availability.get("input_count"), int)
            else None
        ),
        input_policy_id=str(availability.get("input_policy_id"))
        if availability.get("input_policy_id") is not None
        else None,
        reasons=tuple(dict.fromkeys(reasons)),
    )


__all__ = [
    "PublicationCurrentness",
    "PublicationCurrentnessPolicy",
    "PublicationTier",
    "evaluate_input_currentness",
]
