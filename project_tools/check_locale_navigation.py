"""Check representative language-specific sidebars in a built MkDocs site."""

from pathlib import Path

SITE = Path(__file__).resolve().parents[1] / "site"


def primary_navigation(path: str) -> str:
    html = (SITE / path / "index.html").read_text(encoding="utf-8")
    return html.split("md-sidebar--primary", 1)[1].split("md-sidebar--secondary", 1)[0]


def main() -> None:
    english = primary_navigation("concepts/lean-differential-spike-2026-09")
    english_guide = primary_navigation("guides/execution-simulation.en")
    chinese_companion = primary_navigation("README.zh-CN")
    chinese_original = primary_navigation("guides/execution-simulation")

    assert "Core concepts" in english
    assert "指南（中文原文）" not in english
    assert "execution-simulation/" not in english
    assert "guides/execution-simulation.en/" in english
    assert "guides/point-in-time-data/" in english
    assert "guides/sequenced-execution/" in english
    assert "canonical-backtest-bundle.en/" in english
    assert "Execution simulation" in english_guide
    assert "指南（中文原文）" not in english_guide
    for navigation in (chinese_companion, chinese_original):
        assert "核心概念" in navigation
        assert "Core concepts" not in navigation
        assert "lean-differential-spike-2026-09/" not in navigation
    assert "guides/execution-simulation/" in chinese_companion
    assert "README.zh-CN/" in chinese_original
    assert "concepts/backtest-configuration.zh-CN/" in chinese_companion
    assert "reference/public-api.zh-CN/" in chinese_companion
    assert "reference/allocation-reference.zh-CN/" in chinese_companion
    assert "data/README.zh-CN/" in chinese_companion
    assert "concepts/canonical-backtest-bundle/" in chinese_companion


if __name__ == "__main__":
    main()
