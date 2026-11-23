"""Versioned, strategy-independent factor composition configuration."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from dataclasses import asdict, dataclass, field, fields
from math import isfinite
from types import MappingProxyType
from typing import Any

COMPOSITION_SCHEMA = "alpha_research.factor_composition.v1"
STATIC_METHODS = frozenset(
    {"equal", "weighted", "rank", "hierarchical", "residualized", "interaction", "conditional"}
)
FITTED_METHODS = frozenset({"ic", "icir", "covariance", "pca", "ridge", "pls", "lightgbm"})


def _text(value: object) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError("identity fields must be nonempty strings")
    return value.strip()


def _number(value: object) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not isfinite(value):
        raise ValueError("coefficients must be finite numbers")
    return float(value)


@dataclass(frozen=True)
class FactorInput:
    alias: str
    factor_id: str
    version: str
    direction: int = 1

    def __post_init__(self) -> None:
        for name in ("alias", "factor_id", "version"):
            object.__setattr__(self, name, _text(getattr(self, name)))
        if self.alias.startswith("__"):
            raise ValueError("input aliases beginning with __ are reserved")
        if isinstance(self.direction, bool) or self.direction not in (-1, 1):
            raise ValueError("direction must be -1 or 1")


@dataclass(frozen=True)
class FactorCompositionSpec:
    composition_id: str
    version: str
    inputs: tuple[FactorInput, ...]
    method: str = "equal"
    normalization: str = "zscore"
    missing_policy: str = "propagate"
    weights: Mapping[str, float] = field(default_factory=dict)
    groups: Mapping[str, tuple[str, ...]] = field(default_factory=dict)
    residualize: Mapping[str, tuple[str, ...]] = field(default_factory=dict)
    interactions: tuple[tuple[str, str, float], ...] = ()
    gate: str | None = None
    threshold: float = 0.0
    low_weights: Mapping[str, float] = field(default_factory=dict)
    window: int = 60
    min_periods: int = 20
    min_cross_section: int = 5
    regularization: float = 1.0
    shrinkage: float = 0.2
    max_weight_turnover: float = 2.0
    n_components: int = 1

    def __post_init__(self) -> None:
        for name in ("composition_id", "version"):
            object.__setattr__(self, name, _text(getattr(self, name)))
        inputs = tuple(self.inputs)
        if not inputs or not all(isinstance(item, FactorInput) for item in inputs):
            raise ValueError("inputs must contain FactorInput entries")
        aliases = [item.alias for item in inputs]
        if len(set(aliases)) != len(aliases):
            raise ValueError("input aliases must be unique")
        object.__setattr__(self, "inputs", inputs)
        if self.method not in STATIC_METHODS | FITTED_METHODS:
            raise ValueError("unknown composition method")
        if self.normalization not in {"none", "zscore", "rank"}:
            raise ValueError("unknown normalization")
        if self.missing_policy not in {"propagate", "error"}:
            raise ValueError("unknown missing policy")
        self._validate_mappings(aliases)
        self._validate_interactions(aliases)
        self._validate_numbers(aliases)
        self._validate_method(aliases)

    def _validate_mappings(self, aliases: list[str]) -> None:
        for name in ("weights", "low_weights"):
            value = dict(getattr(self, name))
            if value and set(value) != set(aliases):
                raise ValueError(f"{name} must specify every input alias exactly once")
            value = {key: _number(coef) for key, coef in value.items()}
            if value and sum(abs(coef) for coef in value.values()) == 0:
                raise ValueError(f"{name} cannot be all zero")
            object.__setattr__(self, name, MappingProxyType(value))
        for name in ("groups", "residualize"):
            value = {key: tuple(items) for key, items in getattr(self, name).items()}
            for key, items in value.items():
                _text(key)
                if not items or len(set(items)) != len(items) or not set(items) <= set(aliases):
                    raise ValueError(f"{name} contains invalid aliases")
                if name == "residualize" and (key not in aliases or key in items):
                    raise ValueError("residualize target must differ from exposures")
            object.__setattr__(self, name, MappingProxyType(value))

    def _validate_interactions(self, aliases: list[str]) -> None:
        interactions = tuple((a, b, _number(c)) for a, b, c in self.interactions)
        if any(a not in aliases or b not in aliases or a == b for a, b, _ in interactions):
            raise ValueError("interaction requires two distinct input aliases")
        if len({tuple(sorted((a, b))) for a, b, _ in interactions}) != len(interactions):
            raise ValueError("duplicate interaction pair")
        object.__setattr__(self, "interactions", interactions)

    def _validate_numbers(self, aliases: list[str]) -> None:
        for name in ("threshold", "regularization", "shrinkage", "max_weight_turnover"):
            object.__setattr__(self, name, _number(getattr(self, name)))
        for name in ("window", "min_periods", "min_cross_section", "n_components"):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, int) or value < 1:
                raise ValueError(f"{name} must be a positive integer")
        if self.min_periods > self.window or self.min_cross_section < 3:
            raise ValueError("min_periods must be <= window; min_cross_section must be >= 3")
        if self.regularization <= 0 or not 0 < self.shrinkage <= 1:
            raise ValueError("regularization must be positive and shrinkage in (0, 1]")
        if not 0 <= self.max_weight_turnover <= 2:
            raise ValueError("max_weight_turnover must be in [0, 2]")
        if self.n_components > len(aliases):
            raise ValueError("n_components exceeds input count")

    def _validate_method(self, aliases: list[str]) -> None:
        if self.method in {"weighted", "interaction", "conditional"} and not self.weights:
            raise ValueError("method requires explicit main-effect weights")
        if self.method == "interaction" and not self.interactions:
            raise ValueError("interaction method requires interactions")
        if self.method == "conditional" and (self.gate not in aliases or not self.low_weights):
            raise ValueError("conditional method requires gate and low_weights")
        if self.method == "hierarchical":
            members = [item for group in self.groups.values() for item in group]
            if sorted(members) != sorted(aliases):
                raise ValueError("groups must partition the inputs")
        if self.method == "residualized" and not self.residualize:
            raise ValueError("residualized method requires residualize")
        for name, allowed in (
            ("weights", {"weighted", "interaction", "conditional", "residualized"}),
            ("low_weights", {"conditional"}),
            ("groups", {"hierarchical"}),
            ("residualize", {"residualized"}),
            ("interactions", {"interaction"}),
        ):
            if getattr(self, name) and self.method not in allowed:
                raise ValueError(f"{name} is unused by {self.method}")
        if self.gate is not None and self.method != "conditional":
            raise ValueError("gate is only used by conditional")

    @property
    def aliases(self) -> tuple[str, ...]:
        return tuple(item.alias for item in self.inputs)

    def to_mapping(self) -> dict[str, Any]:
        result = {item.name: getattr(self, item.name) for item in fields(self)}
        result["inputs"] = [asdict(item) for item in self.inputs]
        for name in ("weights", "low_weights"):
            result[name] = dict(result[name])
        for name in ("groups", "residualize"):
            result[name] = {key: list(value) for key, value in result[name].items()}
        result["interactions"] = [list(item) for item in self.interactions]
        return {"schema_version": COMPOSITION_SCHEMA, **result}

    @property
    def fingerprint(self) -> str:
        return hashlib.sha256(
            json.dumps(
                self.to_mapping(), sort_keys=True, separators=(",", ":"), allow_nan=False
            ).encode()
        ).hexdigest()

    @classmethod
    def from_mapping(cls, payload: Mapping[str, Any]) -> FactorCompositionSpec:
        raw = dict(payload)
        if raw.pop("schema_version", COMPOSITION_SCHEMA) != COMPOSITION_SCHEMA:
            raise ValueError("unknown composition schema")
        if set(raw) - {item.name for item in fields(cls)}:
            raise ValueError("unknown composition fields")
        try:
            raw["inputs"] = tuple(FactorInput(**item) for item in raw["inputs"])
            return cls(**raw)
        except (KeyError, TypeError) as exc:
            raise ValueError(f"invalid composition configuration: {exc}") from exc
