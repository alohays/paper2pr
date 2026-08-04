#!/bin/bash
# preview.sh
# Live preview Quarto slides with hot-reload
#
# Usage: ./scripts/preview.sh [Deck]
# Examples:
#   ./scripts/preview.sh DreamZero          # bare name, genre resolved for you
#   ./scripts/preview.sh papers/DreamZero   # explicit, if a name is ambiguous

set -e

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"

DECK="${1:-DreamZero}"
shift || true

# scripts/deckpath.py knows the Quarto/<genre>/ layout so this script does not.
if ! QMD=$(python3 scripts/deckpath.py "$DECK" --relative 2>&1); then
  echo "$QMD"
  echo
  echo "Available decks:"
  python3 scripts/deckpath.py --list | sed 's|^|  |'
  exit 1
fi

echo "=== Previewing $DECK ==="
echo "Edit $QMD — browser will auto-reload"
echo "Note: Figures may not display in preview (use /deploy for full render)"
echo ""

exec quarto preview "$QMD" "$@"
