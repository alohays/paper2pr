#!/bin/bash
# Export a deck's rendered RevealJS HTML to a PDF handout (D10, WP7).
#
# Usage:
#   bash scripts/export_pdf.sh <Deck-or-html> [--out FILE]
#
#   <Deck-or-html>  a bare deck name or genre/name (resolved by deckpath.py),
#                   a path to a .qmd (fixtures outside the genres included),
#                   or a path to an already rendered .html
#   --out FILE      where to write the PDF (default: exports/<deck>.pdf under
#                   the repo root; exports/ is gitignored -- handouts are
#                   uploaded to the LMS by hand and never enter git)
#
# The deck is re-rendered first when the HTML is missing or older than its
# qmd, so the handout can never be a stale render.
#
# Mode: decktape reveal (screen rendering), NOT Chrome ?print-pdf.
# Verified 2026-08-20 on Quarto/_fixtures/video/video.qmd: decktape shows the
# poster (not a black box) on all three video slide types -- the full-bleed
# background-video slide, the inline video-card and the two-up montage --
# because in screen mode a paused/unbuffered <video> paints its poster
# attribute, the background clip has the data-background-poster CSS underlay
# that slide-types.lua installs, and decktape waits for media buffering
# (--buffer-timeout, default 30 s) plus the explicit --pause below before
# capturing. Fragment captions come out revealed. The ?print-pdf route was
# rejected: reveal's print mode moves .slide-background under .pdf-page, where
# the theme's @media print selectors do not reach background videos, so it
# would need a theme change plus a JS-settle heuristic for headless
# --print-to-pdf; decktape needs neither. Videos need the network once (the
# clips and posters live on the deck's GitHub Release), same as playback.
#
# After the export the script asserts, loudly:
#   1. the PDF has at least one page (pdfinfo), and
#   2. no Hangul leaked into the text layer (pdftotext): every Hangul
#      character in the PDF must appear in the deck's own visible source --
#      the qmd AFTER the speaker-note strip (strip_qmd_notes.py, the same
#      filter git runs), plus its {{< include >}} targets, with HTML
#      entities decoded (tracked qmds write glosses as &#NNNN;). A gloss the
#      deck shows on purpose (D18) passes; a speaker note, which the strip
#      removed from the expected set, fails naming the page. A bare .html
#      with no qmd has an empty expected set: any Hangul fails.
#
# Needs: decktape (nvm node), quarto, pdfinfo/pdftotext (poppler), python3.

set -euo pipefail

ORIG_CWD="$(pwd)"
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"

usage() { sed -n '2,12p' "$0" | sed 's/^# \{0,1\}//' >&2; exit 2; }

ref=""
out=""
while [ $# -gt 0 ]; do
  case "$1" in
    --out) [ $# -ge 2 ] || { echo "error: --out needs a value" >&2; exit 2; }
           out="$2"; shift 2 ;;
    -h|--help) usage ;;
    *) [ -z "$ref" ] || { echo "error: unexpected argument: $1" >&2; exit 2; }
       ref="$1"; shift ;;
  esac
done
[ -n "$ref" ] || usage

command -v decktape >/dev/null || {
  echo "error: decktape not on PATH (it lives in the nvm node bin; nvm use 22)" >&2
  exit 1
}
for tool in quarto pdfinfo pdftotext python3; do
  command -v "$tool" >/dev/null || { echo "error: $tool not on PATH" >&2; exit 1; }
done

# A path argument may be relative to the repo root (the documented way) or to
# wherever the caller stood; try both, return it absolute.
resolve_path() {
  if [ -f "$1" ]; then
    echo "$(cd "$(dirname "$1")" && pwd)/$(basename "$1")"
  elif [ -f "$ORIG_CWD/$1" ]; then
    echo "$(cd "$(dirname "$ORIG_CWD/$1")" && pwd)/$(basename "$1")"
  else
    echo "error: no such file: $1" >&2
    return 1
  fi
}

# ---- resolve <Deck-or-html> to a qmd (maybe) and an html ---------------------
qmd=""
html=""
case "$ref" in
  *.qmd)
    qmd="$(resolve_path "$ref")"
    html="${qmd%.qmd}.html"
    ;;
  *.html)
    html="$(resolve_path "$ref")"
    # Re-render through the sibling qmd when there is one (a doctored or
    # hand-made html has none and is exported as-is).
    [ -f "${html%.html}.qmd" ] && qmd="${html%.html}.qmd"
    ;;
  *)
    # A deck name: deckpath.py owns the layout (and prints its own error).
    qmd="$(python3 scripts/deckpath.py "$ref" --field qmd)"
    html="$(python3 scripts/deckpath.py "$ref" --field html)"
    ;;
esac

# ---- render when stale (missing html, or qmd newer) --------------------------
if [ -n "$qmd" ] && { [ ! -f "$html" ] || [ "$qmd" -nt "$html" ]; }; then
  echo "Rendering $qmd (html missing or stale)"
  # Render from the qmd's own directory: decks under Quarto/<genre>/ still
  # pick up the _quarto.yml project defaults, and fixtures under _fixtures/
  # (outside the project on purpose) render standalone, as AGENTS.md does.
  ( cd "$(dirname "$qmd")" && quarto render "$(basename "$qmd")" )
  [ -f "$html" ] || { echo "error: render produced no $html" >&2; exit 1; }
fi

# ---- export ------------------------------------------------------------------
stem="$(basename "${html%.html}")"
[ -n "$out" ] || out="exports/$stem.pdf"
mkdir -p "$(dirname "$out")"

decktape reveal "file://$html" "$out" --size 1280x720 --pause 1000

# ---- assert: pages > 0 -------------------------------------------------------
pages="$(pdfinfo "$out" | awk '/^Pages:/ {print $2}')"
if [ -z "$pages" ] || [ "$pages" -lt 1 ]; then
  echo "error: $out has no pages (pdfinfo said: '${pages:-nothing}')" >&2
  exit 1
fi

# ---- assert: no Hangul leak in the text layer --------------------------------
# Every Hangul character on a PDF page must be one the deck visibly shows on
# purpose: present in the note-stripped qmd (or an included qmd), entities
# decoded. Notes are removed from that expected set by the same filter git
# runs, so a note that somehow reached the render fails here, by page.
if ! python3 - "$out" "$qmd" <<'PY'
import html as html_mod, re, subprocess, sys
from pathlib import Path

pdf, qmd = sys.argv[1], sys.argv[2]
HANGUL = re.compile("[\u1100-\u11FF\u3130-\u318F\uA960-\uA97F\uAC00-\uD7A3\uD7B0-\uD7FF]")
INCLUDE = re.compile(r"\{\{<\s*include\s+(\S+)\s*>\}\}")

def visible_hangul(path: Path):
    """(Hangul set the qmd shows on slides, the note-stripped text).
    Stripped by the same filter git runs, entities decoded."""
    stripped = subprocess.run(
        ["python3", "scripts/strip_qmd_notes.py"],
        input=path.read_text(encoding="utf-8"),
        capture_output=True, text=True, check=True).stdout
    return set(HANGUL.findall(html_mod.unescape(stripped))), stripped

expected = set()
if qmd:
    q = Path(qmd)
    chars, stripped = visible_hangul(q)
    expected |= chars
    for inc in INCLUDE.findall(stripped):          # one level, as Quarto uses it
        p = (q.parent / inc)
        if p.is_file():
            expected |= visible_hangul(p)[0]

text = subprocess.run(["pdftotext", pdf, "-"],
                      capture_output=True, text=True, check=True).stdout
bad = []
for i, page in enumerate(text.split("\f"), start=1):
    leaked = sorted(set(HANGUL.findall(page)) - expected)
    if leaked:
        cps = ", ".join(f"U+{ord(c):04X}" for c in leaked[:8])
        more = " ..." if len(leaked) > 8 else ""
        bad.append(f"  page {i}: {len(leaked)} Hangul character(s) not in the "
                   f"deck's visible source ({cps}{more})")
if bad:
    print("Hangul leaked into the PDF text layer:")
    print("\n".join(bad))
    sys.exit(1)
PY
then
  echo "error: Hangul reached the handout $out -- notes must never be in a PDF." >&2
  echo "       Check the deck and the strip chain (strip_qmd_notes.py, CI strip)." >&2
  exit 1
fi

size="$(du -h "$out" | cut -f1 | tr -d ' ')"
echo "OK  $out  ($pages pages, $size, no Hangul leak in the text layer)"
