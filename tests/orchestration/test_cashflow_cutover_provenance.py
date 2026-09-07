from __future__ import annotations

import json
from pathlib import Path

from strategy_pipeline.cashflow_publication import publish_cashflow_shadow
from tests.orchestration.test_cashflow_publication import _readiness, _selection


def test_cashflow_publication_records_private_and_public_commit_provenance(
    tmp_path: Path,
) -> None:
    output = publish_cashflow_shadow(
        _selection(tmp_path / "selection.json"),
        readiness_path=_readiness(tmp_path / "readiness.json"),
        output_root=tmp_path / "published",
        producer_repository="runchengxie/quant-research",
        producer_commit="producer-commit",
        platform_repository="runchengxie/quant-platform",
        platform_commit="platform-commit",
    )
    receipt = json.loads(output.receipt_path.read_text(encoding="utf-8"))
    assert receipt["producer_repository"] == "runchengxie/quant-research"
    assert receipt["platform_repository"] == "runchengxie/quant-platform"
    assert receipt["producer_commit"] == "producer-commit"
    assert receipt["platform_commit"] == "platform-commit"
    assert receipt["research_only"] is True
    assert receipt["eligible_for_live"] is False
