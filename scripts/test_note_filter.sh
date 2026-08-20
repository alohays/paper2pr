#!/bin/bash
# Regression test for the speaker-note clean filter.
#
# Why this exists: .gitattributes patterns that contain a slash are anchored,
# and `*` does not cross a directory separator. `Quarto/*.qmd` therefore covers
# a deck at Quarto/DreamZero.qmd but NOT one at Quarto/papers/DreamZero.qmd.
# Git does not warn when an attribute stops matching -- the filter simply never
# runs and speaker notes get committed. That is a privacy leak that fails
# silently, so it gets a test.
#
# Usage: bash scripts/test_note_filter.sh

set -u

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"

fail=0

check_attr() {
  local path="$1"
  local got
  got="$(git check-attr filter -- "$path" | sed 's/.*filter: //')"
  if [ "$got" = "strip-speaker-notes" ]; then
    echo "  ok    $path"
  else
    echo "  FAIL  $path -> filter: $got (expected strip-speaker-notes)"
    fail=1
  fi
}

echo "1. Clean filter is configured in this clone"
if [ -n "$(git config --get filter.strip-speaker-notes.clean || true)" ]; then
  echo "  ok    filter.strip-speaker-notes.clean is set"
else
  echo "  FAIL  filter is not configured -- run scripts/setup-git-filters.sh"
  echo "        Until you do, committing a deck writes its speaker notes to git."
  fail=1
fi

echo "2. The attribute resolves at every depth a deck can live at"
check_attr "Quarto/DreamZero.qmd"
check_attr "Quarto/papers/DreamZero.qmd"
check_attr "Quarto/lectures/dgist-2026f-w02.qmd"
check_attr "Quarto/talks/SUNY.qmd"

echo "3. The filter removes both note forms: the divs and the title data-notes"
tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT
cat > "$tmp/probe.qmd" <<'QMD'
---
title: Probe
title-slide-attributes:
  data-notes: |
    The title notes must never reach git.

    Not even after a blank line inside the block.
---

## A slide

Body text.

::: {.notes}
This line must never reach git.
:::
QMD
stripped="$(python3 scripts/strip_qmd_notes.py < "$tmp/probe.qmd")"
if printf '%s' "$stripped" | grep -q "must never reach git"; then
  echo "  FAIL  strip_qmd_notes.py left note text in its output"
  fail=1
else
  echo "  ok    note div text removed by strip_qmd_notes.py"
fi
if printf '%s' "$stripped" | grep -q "data-notes"; then
  echo "  FAIL  strip_qmd_notes.py left the title data-notes block in its output"
  fail=1
else
  echo "  ok    title data-notes block removed by strip_qmd_notes.py"
fi

echo "4. Render output stays ignored under genre directories"
for p in "Quarto/papers/DreamZero.html" "Quarto/lectures/w02_files/x.js"; do
  if git check-ignore -q "$p"; then
    echo "  ok    $p is ignored"
  else
    echo "  FAIL  $p is NOT ignored -- a rendered deck would be committable"
    fail=1
  fi
done

echo
if [ "$fail" -eq 0 ]; then
  echo "PASS"
else
  echo "FAIL -- do not move decks into subdirectories until this passes"
fi
exit "$fail"
