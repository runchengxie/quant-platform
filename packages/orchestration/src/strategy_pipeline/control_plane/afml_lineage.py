"""Attach AFML evidence hashes to an existing targets lineage sidecar."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

_EVIDENCE_FILES = {
    "research_protocol": "research_protocol_report.json",
    "sizing_receipt": "sizing_receipt.json",
    "strategy_risk": "strategy_risk_report.json",
    "hrp_receipt": "hrp_receipt.json",
}


def attach_afml_evidence_to_lineage(
    lineage_path: str | Path,
    *,
    run_dir: str | Path,
    require_release_protocol: bool = True,
) -> dict[str, Any]:
    """Add evidence paths and hashes without modifying target semantics."""

    lineage_file = Path(lineage_path).expanduser().resolve()
    root = Path(run_dir).expanduser().resolve()
    if not lineage_file.is_file():
        raise FileNotFoundError(f"Targets lineage file not found: {lineage_file}")
    if not root.is_dir():
        raise FileNotFoundError(f"Run directory not found: {root}")
    payload = json.loads(lineage_file.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise TypeError("Targets lineage must contain a JSON object")

    attached: dict[str, Any] = {}
    for key, file_name in _EVIDENCE_FILES.items():
        artifact = root / file_name
        if not artifact.is_file():
            if key == "research_protocol" and require_release_protocol:
                raise FileNotFoundError(f"Required release protocol report not found: {artifact}")
            continue
        entry: dict[str, Any] = {
            "path": str(artifact),
            "sha256": hashlib.sha256(artifact.read_bytes()).hexdigest(),
        }
        if key == "research_protocol":
            report = json.loads(artifact.read_text(encoding="utf-8"))
            if not isinstance(report, dict):
                raise ValueError(f"Research protocol report must be a JSON object: {artifact}")
            level = str(report.get("level") or "")
            status = str(report.get("status") or "")
            if level != "release" or status != "pass":
                raise ValueError(
                    "Research protocol evidence must be a passed release report "
                    "before lineage binding"
                )
            entry.update(
                {
                    "level": level,
                    "status": status,
                    "manifest_sha256": report.get("manifest_sha256"),
                }
            )
        attached[key] = entry
        payload[key] = entry

    payload["afml_evidence"] = {
        "schema_version": 1,
        "run_dir": str(root),
        "artifacts": attached,
    }
    lineage_file.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, default=str) + "\n",
        encoding="utf-8",
    )
    return payload


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Attach AFML evidence paths and SHA-256 values to targets lineage."
    )
    parser.add_argument("lineage")
    parser.add_argument("--run-dir", required=True)
    parser.add_argument(
        "--require-release-protocol",
        action=argparse.BooleanOptionalAction,
        default=True,
    )
    args = parser.parse_args(argv)
    payload = attach_afml_evidence_to_lineage(
        args.lineage,
        run_dir=args.run_dir,
        require_release_protocol=args.require_release_protocol,
    )
    print(json.dumps(payload.get("afml_evidence"), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = ["attach_afml_evidence_to_lineage", "main"]
