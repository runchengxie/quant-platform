"""Generic YAML configuration loading for public pipeline integrations."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from importlib import resources
from pathlib import Path
from typing import Any

import yaml

EXTENDS_KEY = "extends"


@dataclass(frozen=True)
class LoadedConfigRef:
    data: dict[str, Any]
    path: Path | None
    source: str


@dataclass(frozen=True)
class ResolvedConfig:
    data: dict[str, Any]
    label: str
    path: Path | None
    source: str


def deep_merge(base: Mapping[str, Any], override: Mapping[str, Any]) -> dict[str, Any]:
    """Merge nested mappings, with values from ``override`` taking precedence."""

    result = dict(base)
    for key, value in override.items():
        previous = result.get(key)
        if isinstance(previous, Mapping) and isinstance(value, Mapping):
            result[key] = deep_merge(previous, value)
        else:
            result[key] = value
    return result


def _load_yaml_text(text: str) -> dict[str, Any]:
    payload = yaml.safe_load(text) or {}
    if not isinstance(payload, dict):
        raise SystemExit("Config root must be a mapping.")
    return dict(payload)


def load_yaml_path(path: Path) -> dict[str, Any]:
    """Load one YAML mapping from a filesystem path."""

    if not path.is_file():
        raise SystemExit(f"Config file not found: {path}")
    try:
        return _load_yaml_text(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, yaml.YAMLError) as exc:
        raise SystemExit(f"Unable to load config {path}: {exc}") from exc


def read_package_text(package: str, filename: str) -> str:
    try:
        return resources.files(package).joinpath(filename).read_text(encoding="utf-8")
    except (FileNotFoundError, ModuleNotFoundError) as exc:
        raise SystemExit(f"Packaged config not found: {package}/{filename}") from exc


def load_yaml_package(package: str, filename: str) -> dict[str, Any]:
    """Load one YAML mapping bundled in an installed Python package."""

    try:
        return _load_yaml_text(read_package_text(package, filename))
    except (OSError, UnicodeDecodeError, yaml.YAMLError) as exc:
        raise SystemExit(f"Unable to load packaged config {package}/{filename}: {exc}") from exc


def _package_has_file(package: str, filename: str) -> bool:
    try:
        return resources.files(package).joinpath(filename).is_file()
    except (ModuleNotFoundError, OSError):
        return False


def _search_candidates(
    ref: str,
    *,
    current_path: Path | None,
    search_paths: list[str],
) -> list[Path]:
    path = Path(ref).expanduser()
    if path.is_absolute():
        return [path]

    candidates: list[Path] = []
    if current_path is not None:
        candidates.append(current_path.parent / path)
    candidates.append(Path.cwd() / path)
    for root in search_paths:
        search_root = Path(root)
        candidates.append(search_root / path)
        if path.name and path.name != str(path):
            candidates.append(search_root / path.name)

    result: list[Path] = []
    seen: set[Path] = set()
    for candidate in candidates:
        resolved = candidate.resolve()
        if resolved not in seen:
            seen.add(resolved)
            result.append(resolved)
    return result


def _load_config_by_ref(
    ref: str,
    *,
    package: str | None,
    search_paths: list[str],
    current_path: Path | None,
) -> LoadedConfigRef | None:
    for candidate in _search_candidates(
        ref,
        current_path=current_path,
        search_paths=search_paths,
    ):
        if candidate.is_file():
            resolved = candidate.resolve()
            return LoadedConfigRef(
                data=load_yaml_path(resolved),
                path=resolved,
                source=str(resolved),
            )

    filename = Path(ref).name
    if package is not None and filename and _package_has_file(package, filename):
        return LoadedConfigRef(
            data=load_yaml_package(package, filename),
            path=None,
            source=f"package:{package}/{filename}",
        )
    return None


def _resolve_extends(
    data: dict[str, Any],
    *,
    package: str | None,
    search_paths: list[str],
    current_path: Path | None,
    stack: set[str],
    normalizer: Callable[[Mapping[str, Any]], dict[str, Any]] | None,
) -> dict[str, Any]:
    normalized = normalizer(data) if normalizer is not None else dict(data)
    extends = normalized.get(EXTENDS_KEY)
    if extends is None:
        return normalized
    if isinstance(extends, str):
        refs = [extends]
    elif isinstance(extends, list):
        refs = extends
    else:
        raise SystemExit("'extends' must be a string or list of strings")

    merged: dict[str, Any] = {}
    for raw_ref in refs:
        ref = str(raw_ref).strip()
        if not ref:
            continue
        loaded = _load_config_by_ref(
            ref,
            package=package,
            search_paths=search_paths,
            current_path=current_path,
        )
        if loaded is None:
            raise SystemExit(f"Config file not found for extends: {ref}")
        if loaded.source in stack:
            raise SystemExit(f"Circular extends detected: {ref}")
        stack.add(loaded.source)
        try:
            resolved = _resolve_extends(
                loaded.data,
                package=package,
                search_paths=search_paths,
                current_path=loaded.path,
                stack=stack,
                normalizer=normalizer,
            )
        finally:
            stack.remove(loaded.source)
        merged = deep_merge(merged, resolved)

    local = normalized
    local.pop(EXTENDS_KEY, None)
    return deep_merge(merged, local)


def resolve_config(
    ref: str | Path | None,
    *,
    package: str | None = None,
    default_name: str | None = None,
    aliases: Mapping[str, str] | None = None,
    search_paths: list[str] | None = None,
    normalizer: Callable[[Mapping[str, Any]], dict[str, Any]] | None = None,
) -> ResolvedConfig:
    """Resolve a config path, alias, or package resource with ``extends``."""

    paths = list(search_paths or [])
    ref_text = "" if ref is None else str(ref).strip()
    if not ref_text:
        if not default_name:
            raise SystemExit("A config reference or default_name is required.")
        ref_text = default_name

    loaded = _load_config_by_ref(
        ref_text,
        package=package,
        search_paths=paths,
        current_path=None,
    )
    if loaded is None and aliases:
        alias = aliases.get(ref_text) or aliases.get(ref_text.lower())
        if alias:
            ref_text = alias
            loaded = _load_config_by_ref(
                ref_text,
                package=package,
                search_paths=paths,
                current_path=None,
            )
    if loaded is None:
        raise SystemExit(f"Config file not found: {ref_text}")

    resolved = _resolve_extends(
        loaded.data,
        package=package,
        search_paths=paths,
        current_path=loaded.path,
        stack={loaded.source},
        normalizer=normalizer,
    )
    return ResolvedConfig(
        data=resolved,
        label=Path(ref_text).stem,
        path=loaded.path,
        source=loaded.source,
    )
