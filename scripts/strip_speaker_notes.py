#!/usr/bin/env python3
"""Remove presenter notes from public copies of Reveal HTML, preserving other bytes."""
import argparse
import re
from html.parser import HTMLParser
from pathlib import Path


# Match whole attributes, including quoted values containing '>' or strings
# that look like other attributes. HTMLParser supplies the parsed names. The
# original spelling matters to the rest of a Quarto tag (SVG and inline JS).
ATTRIBUTE = re.compile(
    r"""\s+([^\s=/>]+)(?:\s*=\s*(?:"[^"]*"|'[^']*'|[^\s>]+))?"""
)


class NoteSpans(HTMLParser):
    """Locate private ranges, ignoring CSS, JavaScript and escaped examples."""

    def __init__(self, html):
        super().__init__(convert_charrefs=False)
        self.html = html
        self.lines = [0] + [m.end() for m in re.finditer("\n", html)]
        self.spans = []
        self.note_tag = None
        self.depth = 0
        self.feed(html)
        self.close()
        if self.note_tag is not None:
            raise ValueError("unclosed speaker-note element in rendered HTML")

    def source_offset(self):
        line, column = self.getpos()
        return self.lines[line - 1] + column

    def handle_starttag(self, tag, attrs):
        if self.note_tag is not None:
            if tag == self.note_tag:
                self.depth += 1
            return
        if tag in {"aside", "div"} and any(
                key == "class" and "notes" in (value or "").split() for key, value in attrs):
            self.note_tag = tag
            self.note_start = self.source_offset()
            self.depth = 1
            return

        expected = sum(key == "data-notes" for key, _ in attrs)
        if expected:
            start = self.source_offset()
            matches = [m for m in ATTRIBUTE.finditer(self.get_starttag_text())
                       if m.group(1).lower() == "data-notes"]
            if len(matches) != expected:
                raise ValueError("cannot locate a data-notes attribute in rendered HTML")
            self.spans.extend((start + m.start(), start + m.end()) for m in matches)

    def handle_endtag(self, tag):
        if tag == self.note_tag:
            self.depth -= 1
            if not self.depth:
                end = self.html.index(">", self.source_offset()) + 1
                self.spans.append((self.note_start, end))
                self.note_tag = None

    def handle_startendtag(self, tag, attrs):
        # A self-closing slash does not close a non-void HTML note container.
        self.handle_starttag(tag, attrs)


def count_notes(html_path: Path) -> int:
    return len(NoteSpans(html_path.read_bytes().decode("utf-8")).spans)


def strip_notes(html_path: Path) -> int:
    """Strip a public copy in place. A parse failure leaves the file intact."""
    html = html_path.read_bytes().decode("utf-8")
    spans = NoteSpans(html).spans
    if spans:
        kept = []
        previous = 0
        for start, end in spans:
            kept.append(html[previous:start])
            previous = end
        kept.append(html[previous:])
        html_path.write_bytes("".join(kept).encode("utf-8"))
    return len(spans)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pages", type=Path, nargs="+")
    args = parser.parse_args()
    try:
        count = sum(strip_notes(page) for page in args.pages)
    except (OSError, ValueError) as error:
        parser.exit(1, f"error: {error}\n")
    print(f"Removed {count} speaker-note block(s) or attribute(s).")


if __name__ == "__main__":
    main()
