#!/bin/bash
# Assemble the publishable site from rendered decks.
#
# This lives in a script rather than inline in deploy.yml so it can be run and
# checked locally. The assemble step is where this repo has broken twice --
# robottt-stepper.js shipped missing and killed arrow-key stepping while every
# slide still rendered, and SUNY's theme-compat CSS went the same way. Both
# were invisible until someone interacted with the live deck. A step that only
# ever executes on CI is a step nobody can test before pushing.
#
# Usage: bash scripts/assemble_site.sh [outdir]     (default: _site)
#
# Expects decks to be rendered already. Pair with scripts/check_site_assets.py.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"

OUT="${1:-_site}"
GENRES=$(grep -vE '^\s*(#|$)' Quarto/_genres.txt | tr '\n' ' ')

rm -rf "$OUT"
mkdir -p "$OUT/slides" "$OUT/Figures" "$OUT/files/code"

# Landing page, regenerated from the decks that exist right now. The committed
# copy is there so it can be opened locally; this line is what guarantees the
# published one is never stale, whatever state the committed copy is in.
python3 scripts/build_landing.py >/dev/null
cp pages/index.html "$OUT/"
touch "$OUT/.nojekyll"

for genre in $GENRES; do
  [ -d "Quarto/$genre" ] || continue
  mkdir -p "$OUT/slides/$genre"

  # Rendered HTML + the RevealJS assets Quarto compiles beside it
  for html in Quarto/"$genre"/*.html; do
    [ -f "$html" ] || continue
    name=$(basename "$html" .html)
    cp "$html" "$OUT/slides/$genre/"
    if [ -d "Quarto/$genre/${name}_files" ]; then
      cp -r "Quarto/$genre/${name}_files" "$OUT/slides/$genre/"
    fi
  done

  # Loose runtime assets sitting next to the qmd. Quarto compiles scss into
  # <name>_files, but a plain <script src="foo.js"> in the header is left for
  # us to ship.
  find "Quarto/$genre" -maxdepth 1 -type f \( -name '*.js' -o -name '*.css' \) \
    -exec cp {} "$OUT/slides/$genre/" \; 2>/dev/null || true
done

# Shared fonts. Decks reference these as ../fonts/, which resolves to
# slides/fonts/ from inside a genre directory.
[ -d "Quarto/fonts" ] && cp -r Quarto/fonts "$OUT/slides/fonts"

# Beamer PDFs keep their flat names -- they were never genre-scoped and the
# links to them are the ones already in circulation.
cp Slides/*.pdf "$OUT/slides/" 2>/dev/null || true

# Figures, already genre-scoped on disk
cp -r Figures/* "$OUT/Figures/" 2>/dev/null || true

# R scripts (if any)
cp scripts/R/*.R "$OUT/files/code/" 2>/dev/null || true

# Redirect stubs for the URLs these decks had before genres existed. Cheap
# insurance: the links are already out in a CV, in email, and in chat, and a
# 404 there is a worse outcome than four generated files.
emit_redirect() {
  local old="$1" new="$2"
  if [ ! -f "$OUT/slides/$new" ]; then
    echo "  no target for $old, skipping"
    return
  fi
  printf '%s\n' \
    '<!doctype html>' \
    '<html lang="en"><head><meta charset="utf-8">' \
    '<title>Moved</title>' \
    "<link rel=\"canonical\" href=\"$new\">" \
    "<meta http-equiv=\"refresh\" content=\"0; url=$new\">" \
    '</head><body>' \
    "<p>This deck moved to <a href=\"$new\">$new</a>.</p>" \
    '</body></html>' > "$OUT/slides/$old"
  echo "  slides/$old -> slides/$new"
}

echo "Redirects:"
emit_redirect DreamDojo.html papers/DreamDojo.html
emit_redirect DreamZero.html papers/DreamZero.html
emit_redirect RoboTTT.html papers/RoboTTT.html
emit_redirect SUNY.html talks/SUNY.html

echo
echo "Assembled $OUT:"
find "$OUT/slides" -maxdepth 2 -name '*.html' | sort | sed 's|^|  |'
