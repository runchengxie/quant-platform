"""Public composition API. Inputs must already satisfy the caller's PIT data contract."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from ._composition_provenance import composition_frame_sha256
from ._composition_static import preprocess, static_compose, validate_panel
from .factor_catalog import FactorSpec
from .factor_composition_spec import (
    COMPOSITION_SCHEMA,
    FITTED_METHODS,
    FactorCompositionSpec,
    FactorInput,
)

__all__ = [
    "COMPOSITION_SCHEMA",
    "FactorCompositionResult",
    "FactorCompositionSpec",
    "FactorInput",
    "compose_factors",
    "composition_frame_sha256",
]


@dataclass(frozen=True)
class FactorCompositionResult:
    scores: pd.Series
    transformed: pd.DataFrame
    weights: pd.DataFrame
    fit_audit: pd.DataFrame
    spec: FactorCompositionSpec

    @property
    def fingerprint(self) -> str:
        return self.spec.fingerprint

    def to_factor_spec(
        self,
        *,
        owner: str,
        frequency: str,
        pit_semantics: str,
        universe_semantics: str,
        implementation_sha256: str,
    ) -> FactorSpec:
        """Register the output using the existing catalog's identity contract.

        A configuration fingerprint is not an implementation-code hash; callers
        supply that hash and their actual PIT/universe semantics explicitly.
        """
        normalization = "rank" if self.spec.method == "rank" else self.spec.normalization
        return FactorSpec(
            factor_id=self.spec.composition_id,
            version=self.spec.version,
            owner=owner,
            frequency=frequency,
            dependencies=tuple(
                dict.fromkeys(f"{item.factor_id}@{item.version}" for item in self.spec.inputs)
            ),
            pit_semantics=pit_semantics,
            universe_semantics=universe_semantics,
            implementation_sha256=implementation_sha256,
            preprocessing=(
                f"normalization:{normalization}",
                f"missing:{self.spec.missing_policy}",
            ),
            description=f"Composition {self.spec.method}; configuration sha256={self.fingerprint}",
        )


def compose_factors(
    frame: pd.DataFrame,
    spec: FactorCompositionSpec,
    *,
    labels: pd.Series | None = None,
    label_available_at: pd.Series | None = None,
) -> FactorCompositionResult:
    """Compose a unique dated panel without mutating it or silently filling missing factors.

    ``weights`` records linear input coefficients; interaction terms remain in
    ``spec`` and model nonlinear effects are represented by fit provenance.
    Static coefficients are literal, not implicitly normalized.
    """
    validate_panel(frame, spec.aliases)
    values = preprocess(frame, spec)
    if spec.method in FITTED_METHODS:
        from ._composition_temporal import temporal_compose

        scores, weights, audit = temporal_compose(values, spec, labels, label_available_at)
        transformed = values
    else:
        scores, transformed, weights = static_compose(values, spec)
        audit = pd.DataFrame()
    if np.isinf(scores.to_numpy(dtype=float)).any() or np.isinf(transformed.to_numpy()).any():
        raise ValueError("computed factor values must be finite or missing")
    return FactorCompositionResult(
        scores.rename(spec.composition_id), transformed, weights, audit, spec
    )
