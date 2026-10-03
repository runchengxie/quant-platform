"""Check representative language-specific sidebars in a built MkDocs site."""

import re
import runpy
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
ENGLISH_PAGES = runpy.run_path(str(ROOT / "docs/hooks/locale_navigation.py"))["ENGLISH_PAGES"]


def primary_navigation(path: str) -> str:
    html = (SITE / path / "index.html").read_text(encoding="utf-8")
    return html.split("md-sidebar--primary", 1)[1].split("md-sidebar--secondary", 1)[0]


class _VisibleText(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []

    def handle_data(self, data: str) -> None:
        if data.strip():
            self.parts.append(data.strip())


def assert_no_chinese_navigation(html: str) -> None:
    parser = _VisibleText()
    parser.feed(html)
    text = " ".join(parser.parts)
    assert not re.search(r"[\u4e00-\u9fff]", text), text


def check_all_english_pages() -> None:
    for source in sorted(ENGLISH_PAGES):
        path = Path(source)
        route = path.parent if path.name in {"README.md", "index.md"} else path.with_suffix("")
        navigation = primary_navigation(route.as_posix())
        assert_no_chinese_navigation(navigation)


def main() -> None:
    english = primary_navigation("concepts/lean-differential-spike-2026-09")
    english_turnover = primary_navigation("concepts/turnover.en-US")
    english_benchmark_ladder = primary_navigation("concepts/benchmark-ladder.en-US")
    english_guide = primary_navigation("guides/execution-simulation.en")
    english_orchestration = primary_navigation("orchestration/output-artifacts.en")
    chinese_companion = primary_navigation("README.zh-CN")
    chinese_original = primary_navigation("guides/execution-simulation")

    assert "Core concepts" in english
    assert "Additional research topics" in english
    assert "其他风险与研究主题" not in english
    assert_no_chinese_navigation(english)
    assert_no_chinese_navigation(english_guide)
    assert_no_chinese_navigation(english_orchestration)
    check_all_english_pages()
    assert "Turnover definitions" in english_turnover
    assert "Market benchmark comparisons" in english_benchmark_ladder
    assert "../turnover.en-US/" in english
    assert "../benchmark-ladder.en-US/" in english
    assert "指南（中文原文）" not in english
    assert "execution-simulation/" not in english
    assert "guides/execution-simulation.en/" in english
    assert "guides/point-in-time-data.en/" in english
    assert "guides/sequenced-execution.en/" in english
    assert "guides/incumbent-requalification.en/" in english
    assert "guides/incumbent-requalification-oos-controls.en/" in english
    assert "guides/promotion-sidecar.en/" in english
    assert "guides/sleeve-portfolio.en/" in english
    assert "guides/diagnostic-close-replay.en/" in english
    assert "../differential-backtesting.en/" in english
    assert "../portfolio-optimization-backends.en/" in english
    assert "reference/outputs/backtest-outputs.en/" in english
    assert "canonical-backtest-bundle.en/" in english
    assert "backtest-interpretation.en/" in english
    assert "Execution simulation" in english_guide
    assert "指南（中文原文）" not in english_guide
    assert "Run artifacts" in english_orchestration
    assert "Quality gates" in english_orchestration
    assert "Runtime helpers" in english_orchestration
    assert "输出产物" not in english_orchestration
    for navigation in (chinese_companion, chinese_original):
        assert "核心概念" in navigation
        assert "Core concepts" not in navigation
        assert "lean-differential-spike-2026-09/" not in navigation
    assert "../../concepts/turnover/" in chinese_original
    assert "../../concepts/turnover.en-US/" not in chinese_original
    assert "../../concepts/benchmark-ladder/" in chinese_original
    assert "../../concepts/benchmark-ladder.en-US/" not in chinese_original
    assert "guides/execution-simulation/" in chinese_companion
    assert "README.zh-CN/" in chinese_original
    assert "concepts/backtest-configuration.zh-CN/" in chinese_companion
    assert "reference/public-api.zh-CN/" in chinese_companion
    assert "reference/allocation-reference.zh-CN/" in chinese_companion
    assert "data/README.zh-CN/" in chinese_companion
    assert "concepts/canonical-backtest-bundle/" in chinese_companion
    assert "concepts/backtest-interpretation/" in chinese_companion


if __name__ == "__main__":
    main()
