#!/bin/bash
# Strip speaker notes from rendered deck HTML. Safety net behind the git clean
# filter: the committed qmd has no notes, so this normally finds nothing, and
# finding nothing is the point.
#
# Scoped to the deck pages directly under <root>/<genre>/. Not a recursive
# find: each deck's <name>_files/ carries RevealJS's own speaker-view.html,
# which is a plugin template rather than a deck, and rewriting it is at best
# wasted work.
#
# This lived inline in deploy.yml and could therefore only ever run on CI.
# It shipped a loop ending in `[ -f "$html" ] && python3 ...`, which returns 1
# when a genre directory holds no rendered deck -- Quarto/lectures/ was empty,
# it sorted last, and `bash -e` failed the whole step after the strip had
# already done its job correctly. Assemble, the asset check and the deploy
# never ran. Hence: a script, runnable locally, that ends on an echo.
#
# Usage: bash scripts/strip_notes.sh [root]      (default: Quarto)

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"

ROOT="${1:-Quarto}"
GENRES=$(grep -vE '^[[:space:]]*(#|$)' Quarto/_genres.txt | tr '\n' ' ')

n=0
for genre in $GENRES; do
  [ -d "$ROOT/$genre" ] || continue
  for html in "$ROOT/$genre"/*.html; do
    [ -f "$html" ] || continue
    python3 scripts/strip_speaker_notes.py "$html"
    n=$((n + 1))
  done
done

echo "Checked $n rendered deck(s) under $ROOT/"
