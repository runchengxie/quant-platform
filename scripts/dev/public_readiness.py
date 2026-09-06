#!/usr/bin/env python3
"""Report and ratchet blockers to a public clean-room default dependency graph."""

from __future__ import annotations

import argparse
import json
import re
import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import cast

REPO_ROOT = Path(__file__).resolve().parents[2]
REGISTRY_PATH = Path("scripts/dev/public_dependency_registry.json")
DEBT_PATH = Path("scripts/dev/public_readiness_debt.json")
PROJECT_PATH = Path("pyproject.toml")
NAME_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*")
NORMALIZE_RE = re.compile(r"[-_.]+")
DIRECT_GIT_RE = re.compile(r"\s@\s+git\+(https?://[^@\s;]+)(?:@[^\s;]+)?")


@dataclass(frozen=True, slots=True)
class ReadinessFinding:
    gate: str
    key: str
    detail: str

    @property
    def finding_key(self) -> str:
        return f"{self.gate}|{self.key}"


def _normalize_name(value: str) -> str:
    return NORMALIZE_RE.sub("-", value).lower()


def _requirement_name(requirement: str) -> str:
    match = NAME_RE.match(requirement.strip())
    if not match:
        raise ValueError(f"cannot parse dependency name: {requirement!r}")
    return _normalize_name(match.group(0))


def _direct_git_url(requirement: str) -> str | None:
    match = DIRECT_GIT_RE.search(requirement)
    if match:
        return match.group(1)
    return None


def _load_registry(repo_root: Path) -> dict[str, str]:
    payload = json.loads((repo_root / REGISTRY_PATH).read_text(encoding="utf-8"))
    if payload.get("schema_version") != 1:
        raise ValueError("public dependency registry schema_version must be 1")
    repositories = payload.get("repositories")
    if not isinstance(repositories, dict):
        raise TypeError("public dependency registry repositories must be an object")
    result: dict[str, str] = {}
    for url, visibility in repositories.items():
        if visibility not in {"public", "private"}:
            raise ValueError(f"invalid dependency visibility for {url}: {visibility!r}")
        result[str(url)] = str(visibility)
    return result


def _load_debt(repo_root: Path) -> dict[str, dict[str, str]]:
    payload = json.loads((repo_root / DEBT_PATH).read_text(encoding="utf-8"))
    if payload.get("schema_version") != 1:
        raise ValueError("public readiness debt schema_version must be 1")
    entries = payload.get("entries")
    if not isinstance(entries, dict):
        raise TypeError("public readiness debt entries must be an object")
    required = {"owner", "removal_stream", "reason"}
    validated: dict[str, dict[str, str]] = {}
    for key, metadata in entries.items():
        if not isinstance(key, str) or len(key.split("|")) != 2:
            raise ValueError(f"invalid public readiness debt key: {key!r}")
        if not isinstance(metadata, dict):
            raise TypeError(f"invalid public readiness debt metadata for {key}")
        missing = sorted(required - metadata.keys())
        if missing:
            raise ValueError(f"public readiness debt {key} missing: {', '.join(missing)}")
        validated[key] = {name: str(metadata[name]) for name in sorted(required)}
    return validated


def _project_config(repo_root: Path) -> dict[str, object]:
    with (repo_root / PROJECT_PATH).open("rb") as handle:
        return cast(dict[str, object], tomllib.load(handle))


def _record_git_finding(
    findings: dict[str, ReadinessFinding],
    registry: dict[str, str],
    *,
    name: str,
    git_url: str,
    origin: str,
) -> None:
    visibility = registry.get(git_url)
    if visibility is None:
        finding = ReadinessFinding(
            "unreviewed-git-source",
            name,
            f"{origin} uses unreviewed Git source {git_url}",
        )
    elif visibility == "private":
        finding = ReadinessFinding(
            "default-dependency",
            name,
            f"{origin} resolves from private Git source {git_url}",
        )
    else:
        return
    findings[finding.finding_key] = finding


def collect_readiness_findings(repo_root: Path = REPO_ROOT) -> list[ReadinessFinding]:
    config = _project_config(repo_root)
    project = cast(dict[str, object], config.get("project", {}))
    dependencies = cast(list[str], project.get("dependencies", []))
    tool = cast(dict[str, object], config.get("tool", {}))
    uv = cast(dict[str, object], tool.get("uv", {}))
    sources = cast(dict[str, object], uv.get("sources", {}))
    overrides = cast(list[str], uv.get("override-dependencies", []))
    normalized_sources = {_normalize_name(name): value for name, value in sources.items()}
    registry = _load_registry(repo_root)
    findings: dict[str, ReadinessFinding] = {}

    for requirement in dependencies:
        name = _requirement_name(requirement)
        direct_git_url = _direct_git_url(requirement)
        if direct_git_url:
            _record_git_finding(
                findings,
                registry,
                name=name,
                git_url=direct_git_url,
                origin=f"default dependency {name}",
            )

        source = normalized_sources.get(name)
        if not isinstance(source, dict):
            continue
        git_url = source.get("git")
        if isinstance(git_url, str):
            _record_git_finding(
                findings,
                registry,
                name=name,
                git_url=git_url,
                origin=f"default dependency {name}",
            )

    for requirement in overrides:
        git_url = _direct_git_url(requirement)
        if not git_url:
            continue
        name = _requirement_name(requirement)
        _record_git_finding(
            findings,
            registry,
            name=name,
            git_url=git_url,
            origin=f"uv override {name}",
        )

    return [findings[key] for key in sorted(findings)]


def build_report(repo_root: Path = REPO_ROOT) -> dict[str, object]:
    findings = collect_readiness_findings(repo_root)
    finding_by_key = {finding.finding_key: finding for finding in findings}
    debt = _load_debt(repo_root)
    new_findings = sorted(finding_by_key.keys() - debt.keys())
    stale_debt = sorted(debt.keys() - finding_by_key.keys())
    issues = [finding_by_key[key].detail for key in new_findings]
    issues.extend(f"stale public readiness debt: {key}" for key in stale_debt)
    return {
        "findings": sorted(finding_by_key),
        "new_findings": new_findings,
        "stale_debt": stale_debt,
        "ready": not findings,
        "issues": issues,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=REPO_ROOT)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true", help="Fail only on new or stale debt.")
    mode.add_argument("--strict", action="store_true", help="Fail while any blocker remains.")
    parser.add_argument("--json", action="store_true", help="Print machine-readable report.")
    args = parser.parse_args(argv)

    report = build_report(args.root)
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        if report["ready"]:
            print("Public readiness dependency gate is clean.")
        else:
            print("Public readiness blockers:")
            for key in cast(list[str], report["findings"]):
                print(f"- {key}")
        for issue in cast(list[str], report["issues"]):
            print(f"! {issue}")

    ratchet_failed = bool(report["new_findings"] or report["stale_debt"])
    if args.strict:
        return 1 if ratchet_failed or not report["ready"] else 0
    if args.check:
        return 1 if ratchet_failed else 0
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
