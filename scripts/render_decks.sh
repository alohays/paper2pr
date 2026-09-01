#!/bin/bash
# Render decks with Quarto.
#
# One script so CI and local preview cannot drift. Both used to carry their own
# loop over the deck files, with their own idea of what to skip; the workflow's
# copy could only ever be exercised by pushing.
#
# What counts as a publishable deck comes from deckprofile.py, which reads the
# same deck configs as the rest of the pipeline and excludes `publish: false`.
# An explicitly named unpublished deck still renders for local authoring or an
# external host.
#
# A render failure stops the run. A preview that quietly carries on and then
# assembles the previous render is how a broken deck reaches the site looking
# fine.
#
# Usage:
#   bash scripts/render_decks.sh              # every deck
#   bash scripts/render_decks.sh DreamZero    # one, by bare name or genre/name

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"

if [ $# -gt 0 ]; then
  if ! qmd=$(python3 scripts/deckpath.py "$1" --relative); then
    echo "Available decks:" >&2
    python3 scripts/deckpath.py --list | sed 's|^|  |' >&2
    exit 1
  fi
  echo "Rendering $qmd"
  quarto render "$qmd"
  echo "Rendered 1 deck"
  exit 0
fi

n=0
while IFS= read -r slug; do
  [ -n "$slug" ] || continue
  qmd=$(python3 scripts/deckpath.py "$slug" --relative)
  echo "Rendering $qmd"
  quarto render "$qmd"
  n=$((n + 1))
done < <(python3 scripts/deckprofile.py --list-publishable)

echo "Rendered $n deck(s)"
