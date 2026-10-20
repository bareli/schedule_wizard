"""Render the repository CHANGELOG.md inside the changelog pages."""
from pathlib import Path

MARKER = "<!-- changelog -->"
SOURCE = Path(__file__).resolve().parent.parent / "CHANGELOG.md"


def on_page_markdown(markdown, page, config, files):
    if MARKER not in markdown:
        return markdown
    lines = SOURCE.read_text(encoding="utf-8").splitlines()
    if lines and lines[0].startswith("# "):
        lines = lines[1:]
    text = "\n".join(lines).replace(" \u2014 ", ": ")
    return markdown.replace(MARKER, text)
