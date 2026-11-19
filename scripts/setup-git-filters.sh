#!/bin/bash
# Bootstrap Git's local filter and the active pre-commit hook after cloning.
# With extensions.worktreeConfig already enabled, --worktree writes the
# filter settings to this checkout. core.hooksPath still selects the hook.
set -euo pipefail

cd "$(dirname "$0")/.."
scope=--local
if [[ "$#" == 1 && "$1" == --worktree ]]; then
  if [[ "$(git config --bool extensions.worktreeConfig || true)" != true ]]; then
    echo "error: --worktree requires extensions.worktreeConfig in this clone" >&2
    exit 1
  fi
  scope=--worktree
elif [[ "$#" != 0 ]]; then
  echo "Usage: bash scripts/setup-git-filters.sh [--worktree]" >&2
  exit 2
fi

# A failed clean command normally falls back to storing the raw input. Set
# required first so even an interrupted setup errs on the side of refusal.
git config "$scope" filter.strip-speaker-notes.required true
git config "$scope" filter.strip-speaker-notes.clean 'python3 scripts/strip_qmd_notes.py'
git config "$scope" filter.strip-speaker-notes.smudge cat

hook="$(git rev-parse --git-path hooks/pre-commit)"
mkdir -p "$(dirname "$hook")"
if ! cmp -s scripts/pre-commit.sh "$hook" || [[ ! -x "$hook" ]]; then
  if [[ -e "$hook" || -L "$hook" ]]; then
    backup="$(mktemp "${hook}.replaced-XXXXXX")"
    cp -p "$hook" "$backup"
    echo "Saved the previous pre-commit hook at $backup"
  fi
  # Replace the hook atomically, including when the previous hook is a link.
  temp="$(mktemp "${hook}.install-XXXXXX")"
  trap 'rm -f "$temp"' EXIT
  cp scripts/pre-commit.sh "$temp"
  chmod 755 "$temp"
  mv -f "$temp" "$hook"
fi
echo "Required speaker-note filter and pre-commit gates installed ($hook)."
