#!/usr/bin/env python3
"""Strip speaker notes from RevealJS HTML for public deployment.

Removes both forms RevealJS understands:
  - <aside class="notes"> ... </aside>, one per slide
  - a data-notes="..." attribute on a <section>, which is how the
    Quarto-generated title slide carries its notes (a notes div placed
    before the first `##` becomes its own slide instead of attaching)

Usage:
    python3 scripts/strip_speaker_notes.py path/to/slides.html
    python3 scripts/strip_speaker_notes.py docs/slides/*.html
"""

import re
import sys
from pathlib import Path

NOTES_PATTERN = re.compile(
    r'<aside class="notes">\s*.*?\s*</aside>',
    re.DOTALL
)

# Quarto HTML-escapes the value, so a quote never appears raw inside it.
DATA_NOTES_PATTERN = re.compile(r'\sdata-notes=(?:"[^"]*"|\'[^\']*\')')


def strip_notes(html_path: Path) -> int:
    """Remove speaker notes from HTML file in-place. Returns count removed."""
    content = html_path.read_text(encoding="utf-8")
    new_content, count = NOTES_PATTERN.subn("", content)
    new_content, attr_count = DATA_NOTES_PATTERN.subn("", new_content)
    count += attr_count
    if count > 0:
        html_path.write_text(new_content, encoding="utf-8")
    return count


def main():
    if len(sys.argv) < 2:
        print("Usage: strip_speaker_notes.py <html_file> [...]", file=sys.stderr)
        sys.exit(1)

    total = 0
    for arg in sys.argv[1:]:
        path = Path(arg)
        if not path.exists():
            print(f"  Skip (not found): {path}", file=sys.stderr)
            continue
        count = strip_notes(path)
        if count > 0:
            print(f"  Stripped {count} note blocks from {path.name}")
        total += count

    print(f"  Total: {total} note blocks stripped")


if __name__ == "__main__":
    main()
