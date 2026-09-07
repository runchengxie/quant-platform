#!/usr/bin/env python3
"""Audit a tree and reachable Git history before public publication."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path

SECRET_PATTERNS = (
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b"),
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    re.compile(r"\bgithub_pat_[A-Za-z0-9_]{20,}\b"),
    re.compile(r"\bsk-[A-Za-z0-9]{20,}\b"),
)
PRIVATE_STRATEGY_PATTERN = re.compile(
    r"\b(?:daily[_-]?watch20|deepseek|hotsector|style[_-]?replica|d11[_-]?h5)\b",
    re.IGNORECASE,
)
PRIVATE_GIT_PATTERN = re.compile(
    r"git\+https?://[^\s'\"]+|https?://github\.com/[^\s'\"]+\.git(?:[@#][^\s'\"]+)?",
    re.IGNORECASE,
)
PUBLIC_GIT_SOURCES = {
    "https://github.com/runchengxie/alpha-research.git",
    "https://github.com/runchengxie/quant-market-data-platform.git",
    "https://github.com/runchengxie/portfolio-backtester.git",
    "https://github.com/runchengxie/research-workspace.git",
    "https://github.com/runchengxie/quant-code-quality.git",
}
AUDIT_TOOL_PATHS = {
    "scripts/dev/history_publication_audit.py",
    "scripts/dev/public_surface_export.py",
}


def scan_text(text: str, *, path: str) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    if any(pattern.search(text) for pattern in SECRET_PATTERNS):
        findings.append({"category": "secret-pattern", "path": path})
    if PRIVATE_STRATEGY_PATTERN.search(text) or PRIVATE_STRATEGY_PATTERN.search(path):
        findings.append({"category": "private-strategy-marker", "path": path})
    git_sources = {
        match.group(0).removeprefix("git+").split("@", 1)[0].split("#", 1)[0].split("?", 1)[0]
        for match in PRIVATE_GIT_PATTERN.finditer(text)
    }
    if git_sources - PUBLIC_GIT_SOURCES:
        findings.append({"category": "git-source-reference", "path": path})
    return findings


def publication_outcome(findings: list[dict[str, str]], *, current_tree_clean: bool) -> str:
    categories = {finding["category"] for finding in findings}
    if "secret-pattern" in categories:
        return "rewrite-required"
    if not current_tree_clean:
        return "clean-history-publication-required"
    if categories & {"private-strategy-marker", "git-source-reference"}:
        return "clean-history-publication-required"
    return "direct-public-safe"


def _iter_current_files(repo_root: Path):
    ignored = {".git", ".venv", "__pycache__", "build", "dist"}
    for path in repo_root.rglob("*"):
        if not path.is_file() or any(part in ignored for part in path.parts):
            continue
        try:
            yield path, path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue


def _iter_history_blobs(repo_root: Path):
    result = subprocess.run(
        ["git", "rev-list", "--objects", "--all"],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=True,
    )
    objects: dict[str, str] = {}
    for line in result.stdout.splitlines():
        object_id, _, path = line.partition(" ")
        if object_id and path:
            objects.setdefault(object_id, path)

    result = subprocess.run(
        ["git", "cat-file", "--batch"],
        cwd=repo_root,
        input=("\n".join(objects) + "\n").encode(),
        capture_output=True,
        check=True,
    )
    stream = memoryview(result.stdout)
    offset = 0
    for path in objects.values():
        header_end = result.stdout.find(b"\n", offset)
        if header_end < 0:
            break
        parts = result.stdout[offset:header_end].split()
        offset = header_end + 1
        if len(parts) != 3:
            continue
        size = int(parts[2])
        content = stream[offset : offset + size]
        offset += size + 1
        if parts[1] == b"blob" and size <= 10_000_000:
            yield path, bytes(content).decode("utf-8", errors="replace")


def audit_repository(repo_root: Path) -> dict[str, object]:
    findings: dict[tuple[str, str], dict[str, str]] = {}
    for path, text in _iter_current_files(repo_root):
        relative = path.relative_to(repo_root).as_posix()
        if relative in AUDIT_TOOL_PATHS:
            continue
        for finding in scan_text(text, path=relative):
            findings[(finding["category"], finding["path"])] = finding

    history_available = (repo_root / ".git").exists() or (repo_root / ".git").is_file()
    if history_available:
        for path, text in _iter_history_blobs(repo_root):
            if path in AUDIT_TOOL_PATHS:
                continue
            for finding in scan_text(text, path=f"history:{path}"):
                findings[(finding["category"], finding["path"])] = finding

    result = sorted(findings.values(), key=lambda finding: (finding["category"], finding["path"]))
    current_findings = [finding for finding in result if not finding["path"].startswith("history:")]
    return {
        "findings": result,
        "current_tree_clean": not current_findings,
        "history_available": history_available,
        "outcome": publication_outcome(result, current_tree_clean=not current_findings),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    args = parser.parse_args(argv)
    report = audit_repository(args.root.resolve())
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if report["outcome"] == "direct-public-safe" else 1


if __name__ == "__main__":
    raise SystemExit(main())
