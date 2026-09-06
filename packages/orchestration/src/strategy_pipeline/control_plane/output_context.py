"""Domain-neutral context assembly for control-plane output stages."""

from __future__ import annotations

from collections.abc import Iterator, Mapping
from dataclasses import dataclass, field
from typing import Any

_ALLOWED_SOURCE_OVERRIDES = {
    ("active_log_file", "loaded", "run_artifacts"),
    ("EMBARGO_STEPS", "eval_settings", "extras"),
    ("EFFECTIVE_GAP_STEPS", "eval_settings", "extras"),
    ("OUTPUT_DIR", "eval_settings", "run_artifacts"),
    ("PURGE_STEPS", "eval_settings", "extras"),
    ("WF_FEATURE_TOP_K", "eval_settings", "runtime_settings"),
    ("features", "panel_state", "dataset_state"),
}


@dataclass(frozen=True)
class OutputContext(Mapping[str, Any]):
    """Flatten named stage inputs while rejecting accidental key collisions."""

    loaded: Mapping[str, Any]
    universe_inputs: Mapping[str, Any]
    date_label_settings: Mapping[str, Any]
    eval_settings: Mapping[str, Any]
    universe_filters: Mapping[str, Any]
    runtime_settings: Mapping[str, Any]
    run_artifacts: Mapping[str, Any]
    panel_state: Mapping[str, Any]
    dataset_state: Mapping[str, Any]
    split_state: Mapping[str, Any]
    extras: Mapping[str, Any]
    _flat: dict[str, Any] = field(init=False, repr=False)

    def __post_init__(self) -> None:
        flat: dict[str, Any] = {}
        owners: dict[str, str] = {}
        for label, source in self.named_sources:
            for key, value in source.items():
                if key in flat and _values_conflict(flat[key], value):
                    if (key, owners[key], label) in _ALLOWED_SOURCE_OVERRIDES:
                        flat[key] = value
                        owners[key] = label
                        continue
                    raise ValueError(
                        f"OutputContext key conflict for {key!r}: "
                        f"{owners[key]} and {label} provide different values."
                    )
                flat[key] = value
                owners[key] = label
        object.__setattr__(self, "_flat", flat)

    @property
    def sources(self) -> tuple[Mapping[str, Any], ...]:
        return tuple(source for _, source in self.named_sources)

    @property
    def named_sources(self) -> tuple[tuple[str, Mapping[str, Any]], ...]:
        return tuple(
            (label, getattr(self, label))
            for label in (
                "loaded",
                "universe_inputs",
                "date_label_settings",
                "eval_settings",
                "universe_filters",
                "runtime_settings",
                "run_artifacts",
                "panel_state",
                "dataset_state",
                "split_state",
                "extras",
            )
        )

    def __getitem__(self, key: str) -> Any:
        return self._flat[key]

    def __iter__(self) -> Iterator[str]:
        return iter(self._flat)

    def __len__(self) -> int:
        return len(self._flat)

    def as_dict(self) -> dict[str, Any]:
        return dict(self._flat)


def _values_conflict(left: Any, right: Any) -> bool:
    if left is right:
        return False
    try:
        return bool(left != right)
    except (TypeError, ValueError):
        return True


def build_output_context(
    *,
    loaded: Mapping[str, Any],
    universe_inputs: Mapping[str, Any],
    date_label_settings: Mapping[str, Any],
    eval_settings: Mapping[str, Any],
    universe_filters: Mapping[str, Any],
    runtime_settings: Mapping[str, Any],
    run_artifacts: Mapping[str, Any],
    panel_state: Mapping[str, Any],
    dataset_state: Mapping[str, Any],
    split_state: Mapping[str, Any],
    extras: Mapping[str, Any],
) -> OutputContext:
    return OutputContext(
        loaded=loaded,
        universe_inputs=universe_inputs,
        date_label_settings=date_label_settings,
        eval_settings=eval_settings,
        universe_filters=universe_filters,
        runtime_settings=runtime_settings,
        run_artifacts=run_artifacts,
        panel_state=panel_state,
        dataset_state=dataset_state,
        split_state=split_state,
        extras=extras,
    )
