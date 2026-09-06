import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DOCUMENTS = [
    path
    for path in (
        ROOT / "README.md",
        ROOT / "AGENTS.md",
        ROOT / "CONTRIBUTING.md",
        ROOT / "SECURITY.md",
    )
    if path.exists()
] + [
    path
    for path in sorted((ROOT / "docs").rglob("*.md"))
    if "superpowers" not in path.relative_to(ROOT / "docs").parts
]
FORBIDDEN_PATTERNS = (
    re.compile(r"\*\*"),
    re.compile(r"[“”]"),
    re.compile("；"),
    re.compile("——"),
    re.compile(r"不是[\s\S]{0,80}而是"),
)


def test_chinese_documentation_style_is_consistent():
    violations = []
    for path in DOCUMENTS:
        content = path.read_text(encoding="utf-8")
        for pattern in FORBIDDEN_PATTERNS:
            if pattern.search(content):
                violations.append(f"{path.relative_to(ROOT)}: {pattern.pattern}")

    assert not violations, "documentation style violations: " + ", ".join(violations)
