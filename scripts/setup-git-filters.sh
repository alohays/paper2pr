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

echo "Installing pre-commit hook (speaker notes, then Korean text)..."
HOOK="$REPO_ROOT/.git/hooks/pre-commit"
# Never overwrite someone else's hook without leaving them a copy: this used
# to be a bare cp, and a hook installed by anything else vanished silently.
if [ -e "$HOOK" ] && ! cmp -s "$HOOK" "$REPO_ROOT/scripts/pre-commit.sh"; then
  BACKUP="$HOOK.replaced-$(date +%Y%m%d%H%M%S)"
  cp "$HOOK" "$BACKUP"
  echo "  Existing pre-commit hook saved to ${BACKUP#"$REPO_ROOT"/}"
fi
cp "$REPO_ROOT/scripts/pre-commit.sh" "$HOOK"
chmod +x "$HOOK"
echo "  Pre-commit hook installed."

echo ""
echo "Done. Setup complete:"
echo "  - Speaker notes stripped from QMD on commit (clean filter)"
echo "  - A commit is refused if the filter is missing or a note survived it"
echo "  - Korean text blocked in non-exempt files (pre-commit hook)"
echo ""
echo "Tip: Run 'python3 scripts/backup_notes.py backup <PaperName>' to save notes."
