from __future__ import annotations

import re
import runpy
import subprocess
import sys
from html.parser import HTMLParser
from pathlib import Path

import yaml

PAIRS = (
    ("architecture/runtime-kernel.md", "architecture/runtime-kernel.zh-CN.md"),
    ("risk-model-kernel.md", "risk-model-kernel.zh-CN.md"),
    (
        "development/portfolio-execution-profiling-2026-09.md",
        "development/portfolio-execution-profiling-2026-09.zh-CN.md",
    ),
)


def test_new_english_pages_are_registered_and_linked_to_chinese_companions() -> None:
    root = Path(__file__).resolve().parents[1]
    navigation_hook = (root / "docs/hooks/locale_navigation.py").read_text(encoding="utf-8")

    for english_path, chinese_path in PAIRS:
        english = root / "docs" / english_path
        chinese = root / "docs" / chinese_path
        assert english.is_file()
        assert chinese.is_file()
        english_text = english.read_text(encoding="utf-8")
        chinese_text = chinese.read_text(encoding="utf-8")
        assert f"Language: English · [简体中文]({Path(chinese_path).name})" in english_text
        assert f"语言：简体中文 · [English]({Path(english_path).name})" in chinese_text
        assert f'"{english_path}"' in navigation_hook


def test_every_chinese_navigation_page_links_to_an_english_canonical() -> None:
    root = Path(__file__).resolve().parents[1]
    english_paths = runpy.run_path(str(root / "docs/hooks/locale_navigation.py"))["ENGLISH_PAGES"]
    navigation = yaml.load(
        (root / "mkdocs.yml").read_text(encoding="utf-8"),
        Loader=yaml.BaseLoader,
    )["nav"]
    page_paths: set[str] = set()

    def collect_pages(item: object) -> None:
        if isinstance(item, dict):
            for child in item.values():
                collect_pages(child)
        elif isinstance(item, list):
            for child in item:
                collect_pages(child)
        elif isinstance(item, str) and item.endswith(".md"):
            page_paths.add(item)

    collect_pages(navigation)
    for chinese_path in sorted(page_paths - english_paths):
        path = Path(chinese_path)
        if path.name.endswith(".zh-CN.md"):
            candidate_names = [path.name.replace(".zh-CN.md", ".md")]
        else:
            candidate_names = [f"{path.stem}{suffix}.md" for suffix in (".en", ".en-US", ".en-GB")]
        canonical_paths = [
            (path.parent / name).as_posix()
            for name in candidate_names
            if (path.parent / name).as_posix() in english_paths
            and (root / "docs" / path.parent / name).is_file()
        ]
        assert canonical_paths, chinese_path
        source = (root / "docs" / chinese_path).read_text(encoding="utf-8")
        assert any(Path(canonical).name in source for canonical in canonical_paths), chinese_path


class _PrimaryNavigation(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.active = False
        self.depth = 0
        self.text: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag != "nav":
            return
        classes = (dict(attrs).get("class") or "").split()
        if not self.active and "md-nav--primary" in classes:
            self.active = True
            self.depth = 1
        elif self.active:
            self.depth += 1

    def handle_endtag(self, tag: str) -> None:
        if tag == "nav" and self.active:
            self.depth -= 1
            if self.depth == 0:
                self.active = False

    def handle_data(self, data: str) -> None:
        if self.active:
            self.text.append(data.strip())


def test_new_pages_render_locale_specific_navigation(tmp_path: Path) -> None:
    root = Path(__file__).resolve().parents[1]
    site = tmp_path / "site"
    result = subprocess.run(
        [sys.executable, "-m", "mkdocs", "build", "--strict", "--site-dir", str(site)],
        cwd=root,
        capture_output=True,
        check=False,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr

    expected = {
        "architecture/runtime-kernel": "en",
        "architecture/runtime-kernel.zh-CN": "zh",
        "risk-model-kernel": "en",
        "risk-model-kernel.zh-CN": "zh",
        "development/portfolio-execution-profiling-2026-09": "en",
        "development/portfolio-execution-profiling-2026-09.zh-CN": "zh",
    }
    for page, language in expected.items():
        rendered = (site / page / "index.html").read_text(encoding="utf-8")
        match = re.search(r'<html lang="([^"]+)"', rendered)
        assert match is not None and match.group(1) == language, page
        nav = _PrimaryNavigation()
        nav.feed(rendered)
        labels = " ".join(nav.text)
        if language == "en":
            assert not re.search(r"[\u3400-\u9fff]", labels), page
            for title in ("Runtime kernel", "Risk model kernel", "Portfolio execution profiling"):
                assert title in labels, page
        else:
            assert "运行时内核" in labels
            assert "风险模型内核" in labels
            assert "组合执行性能基线" in labels
            assert "Runtime kernel" not in labels
