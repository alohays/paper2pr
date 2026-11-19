#!/usr/bin/env python3
"""Export one Reveal page per slide with the project's locked DeckTape."""
import argparse
import html
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
from urllib.request import urlopen

import deckpath
from browser import executable
from qmd_includes import expanded_source
from strip_qmd_notes import strip_notes

ROOT = Path(__file__).resolve().parents[1]
HANGUL = re.compile("[\u1100-\u11ff\u3130-\u318f\ua960-\ua97f\uac00-\ud7a3\ud7b0-\ud7ff]")


def source_path(value):
    path = Path(value)
    if not path.is_file():
        path = ROOT / path
    if not path.is_file():
        raise ValueError(f"Input file not found: {Path(value).name}")
    return path.resolve()


def visible_hangul(qmd):
    """Allow glosses in the source and its includes, after Git's note filter."""
    if qmd is None:
        return set()
    source, _ = expanded_source(qmd)
    return set(HANGUL.findall(html.unescape(strip_notes(source))))


def validate_pdf(pdf, qmd, expected_pages):
    info = subprocess.check_output(["pdfinfo", str(pdf)], text=True, env={**os.environ, "LC_ALL": "C"})
    count = re.search(r"^Pages:\s+(\d+)$", info, re.MULTILINE)
    if not count or int(count[1]) < 1:
        raise ValueError("The exported handout is empty")
    pages = int(count[1])
    if expected_pages is not None and pages != expected_pages:
        raise ValueError(f"Handout has {pages} pages for {expected_pages} rendered slides")

    allowed = visible_hangul(qmd)
    text = subprocess.check_output(["pdftotext", str(pdf), "-"], text=True)
    for i, page in enumerate(text.split("\f"), 1):
        if set(HANGUL.findall(page)) - allowed:
            raise ValueError(f"Page {i} contains Hangul outside the note-filtered source")
    return pages


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("deck", help="deck name, .qmd, or exact rendered .html")
    parser.add_argument("--source", help="QMD for checking a separately assembled HTML file")
    parser.add_argument("--url", help="URL serving the same HTML and its runtime assets")
    parser.add_argument("--pages", type=int, help="expected rendered slide count")
    parser.add_argument("--out", type=Path, help="output PDF (default exports/<deck>.pdf)")
    args = parser.parse_args()

    if args.deck.endswith(".html"):
        page = source_path(args.deck)
        sibling = page.with_suffix(".qmd")
        qmd = source_path(args.source) if args.source else None
        if qmd is None and sibling.is_file():
            qmd = sibling
    else:
        if args.source:
            parser.error("--source applies to a rendered .html input")
        qmd = source_path(args.deck) if args.deck.endswith(".qmd") else deckpath.find(args.deck).qmd
        subprocess.run(["bash", "scripts/render_decks.sh", str(qmd)], cwd=ROOT, check=True)
        page = qmd.with_suffix(".html")
    url = args.url or page.as_uri()
    if args.url:
        with urlopen(args.url, timeout=30) as response:
            if response.read() != page.read_bytes():
                raise ValueError("The URL serves a different HTML build")

    local_tool = ROOT / "node_modules" / "decktape"
    locked = json.loads((ROOT / "package.json").read_text())["devDependencies"]["decktape"]
    if not local_tool.is_dir() or json.loads((local_tool / "package.json").read_text())["version"] != locked:
        raise ValueError("Install the locked DeckTape with npm ci")

    out = ROOT / (args.out or Path("exports", page.stem + ".pdf"))
    if out.suffix.lower() != ".pdf":
        raise ValueError("Choose a .pdf output file")
    out.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=out.parent) as temp:
        pdf = Path(temp) / out.name
        command = [str(ROOT / "node_modules" / ".bin" / "decktape"), "reveal",
                   "--chrome-path", executable(), "--size", "1280x720", "--pause", "1000",
                   url, str(pdf)]
        # Browser console output may contain private author paths or notes.
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        if result.returncode:
            if b"Navigation timeout" in result.stdout:
                raise ValueError(f"DeckTape timed out waiting for {page.name} to finish loading")
            raise ValueError(f"DeckTape failed with exit {result.returncode} on {page.name}")
        pages = validate_pdf(pdf, qmd, args.pages)
        pdf.replace(out)
    print(f"Handout verified: {out.name}, {pages} pages")


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, RuntimeError, deckpath.DeckNotFound, deckpath.AmbiguousDeck,
            subprocess.CalledProcessError) as error:
        sys.exit(str(error))
