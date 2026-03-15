#!/bin/bash
# preview.sh
# Live preview Quarto slides with hot-reload
#
# Usage: ./scripts/preview.sh [PaperName]
# Example: ./scripts/preview.sh DreamZero

set -e

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
QUARTO_DIR="$REPO_ROOT/Quarto"

PAPER="${1:-DreamZero}"
QMD="${PAPER}.qmd"

if [ ! -f "$QUARTO_DIR/$QMD" ]; then
  echo "ERROR: Quarto/$QMD not found"
  echo "Available slides:"
  ls "$QUARTO_DIR"/*.qmd 2>/dev/null | xargs -n1 basename | sed 's|\.qmd||'
  exit 1
fi

echo "=== Previewing $PAPER ==="
echo "Edit Quarto/${PAPER}.qmd — browser will auto-reload"
echo "Note: Figures may not display in preview (use /deploy for full render)"
echo ""

cd "$QUARTO_DIR"
exec quarto preview "$QMD" "$@"
