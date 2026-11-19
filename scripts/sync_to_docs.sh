#!/bin/bash
# sync_to_docs.sh
# LOCAL PREVIEW TOOL — renders decks and assembles docs/ the way CI does.
# Production deployment is handled by GitHub Actions (.github/workflows/deploy.yml).
# The docs/ directory is gitignored; this script is for local testing only.
#
# Usage: ./scripts/sync_to_docs.sh [Deck]
# Examples:
#   ./scripts/sync_to_docs.sh                    # render and assemble everything
#   ./scripts/sync_to_docs.sh DreamZero          # render one deck, assemble everything
#   ./scripts/sync_to_docs.sh papers/DreamZero   # explicit genre
#
# The assembly itself is scripts/assemble_site.sh, the same script CI runs.
# This file used to carry its own copy of that logic along with a comment
# telling the reader to keep the two skip lists in step by hand. They are one
# list now, so a preview cannot quietly stop matching what ships.

set -e

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"

DOCS_DIR="$REPO_ROOT/docs"

echo "=== Rendering decks ==="
bash scripts/render_decks.sh ${1:+"$1"}

echo
echo "=== Assembling docs/ ==="
bash scripts/assemble_site.sh "$DOCS_DIR"

# Assembly strips notes from the audience copy and validates its assets.
echo
echo "=== Sync complete ==="
echo "Open: $DOCS_DIR/slides/"
