#!/bin/bash
# One-time setup for git clean/smudge filters.
# Run after cloning: ./scripts/setup-git-filters.sh

set -e

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"

echo "Setting up git filters..."
git config filter.strip-speaker-notes.clean 'python3 scripts/strip_qmd_notes.py'
git config filter.strip-speaker-notes.smudge 'cat'
echo "  Git filter 'strip-speaker-notes' configured."

echo "Installing pre-commit hook (Korean text detection)..."
cp "$REPO_ROOT/scripts/check-korean-pre-commit.sh" "$REPO_ROOT/.git/hooks/pre-commit"
chmod +x "$REPO_ROOT/.git/hooks/pre-commit"
echo "  Pre-commit hook installed."

echo ""
echo "Done. Setup complete:"
echo "  - Speaker notes stripped from QMD on commit (clean filter)"
echo "  - Korean text blocked in non-exempt files (pre-commit hook)"
echo ""
echo "Tip: Run 'python3 scripts/backup_notes.py backup <PaperName>' to save notes."
