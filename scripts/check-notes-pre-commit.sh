#!/bin/bash
# Pre-commit hook: refuse to commit a deck whose speaker notes are still in it.
#
# The notes never reach git because a clean filter takes them out on the way
# in (scripts/strip_qmd_notes.py, wired by .gitattributes). That defence has
# two silent failure modes, and both have happened to this kind of setup:
#
#   1. The filter is a *local* git config value. A fresh clone that skips
#      scripts/setup-git-filters.sh has no filter, nothing warns, and the
#      next commit writes the notes into a public history.
#   2. A .gitattributes pattern that stops matching (an anchored pattern and
#      a deck that moved a directory deeper) switches the filter off for that
#      file with no error at all.
#
# So this checks the outcome rather than the mechanism: every staged deck qmd
# must claim the filter attribute, and its staged blob -- what git is about
# to record -- must contain no notes div and no title-slide data-notes.
#
# Install: scripts/setup-git-filters.sh (as part of the pre-commit hook)
# Run by hand: bash scripts/check-notes-pre-commit.sh

set -u

REPO_ROOT="$(git rev-parse --show-toplevel)"
cd "$REPO_ROOT" || exit 1

fail=0

if [ -z "$(git config --get filter.strip-speaker-notes.clean || true)" ]; then
  echo "ERROR: the speaker-note clean filter is not configured in this clone."
  echo "  Every deck you commit would carry its speaker notes into git."
  echo "  Fix: bash scripts/setup-git-filters.sh"
  fail=1
fi

for file in $(git diff --cached --name-only --diff-filter=ACM -- 'Quarto/*.qmd' 'Quarto/**/*.qmd'); do
  attr="$(git check-attr filter -- "$file" | sed 's/.*filter: //')"
  if [ "$attr" != "strip-speaker-notes" ]; then
    echo "ERROR: $file is not covered by the speaker-note filter"
    echo "  git says filter: $attr (expected strip-speaker-notes)"
    echo "  A .gitattributes pattern stopped matching. Fix the pattern, not this hook."
    fail=1
    continue
  fi
  if ! git show ":$file" | python3 -c '
import sys
sys.path.insert(0, "scripts")
import re
import strip_qmd_notes

text = sys.stdin.read()
try:
    blocks = strip_qmd_notes.find_note_divs(text)
except ValueError as e:
    print(f"  unreadable: {e}")
    sys.exit(1)
lines = text.split("\n")
bad = [f"  line {s + 1}: {lines[s].strip()}" for s, _ in blocks]
bad += [f"  line {i}: {l.strip()}" for i, l in enumerate(lines, 1)
        if re.match(r"^\s*data-notes:", l)]
if bad:
    print("\n".join(bad))
    sys.exit(1)
'; then
    echo "ERROR: $file would be committed with its speaker notes"
    echo "  (the lines above are in the staged blob, after the filter ran)"
    fail=1
  fi
done

if [ "$fail" -eq 1 ]; then
  echo ""
  echo "Nothing was committed. Speaker notes are the one thing in this repo"
  echo "that must not reach a public history."
  exit 1
fi
exit 0
