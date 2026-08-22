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

echo "3b. Every notes spelling pandoc accepts is removed, and only those"
cat > "$tmp/forms.qmd" <<'QMD'
---
title: Forms
---

## A

::: {.notes}
LEAK-canonical
:::

## B

:::{.notes}
LEAK-nospace
:::

## C

::: notes
LEAK-bareclass
:::

## D

::: {.notes .fragment}
LEAK-twoclasses
:::

## E

::::: {.notes}
LEAK-fivecolons
:::::

## F

::: {.notes}
before

::: {.callout-note}
inner div
:::

LEAK-afternested
:::

## G

::: {.callout-note}
KEEP-this-is-not-a-note
:::

```
::: {.notes}
KEEP-inside-a-code-fence
```
QMD
forms="$(python3 scripts/strip_qmd_notes.py < "$tmp/forms.qmd")"
if printf '%s' "$forms" | grep -q "LEAK-"; then
  echo "  FAIL  a notes spelling survived the filter:"
  printf '%s' "$forms" | grep -n "LEAK-" | sed 's/^/        /'
  fail=1
else
  echo "  ok    all six notes spellings removed"
fi
for keep in KEEP-this-is-not-a-note KEEP-inside-a-code-fence; do
  if printf '%s' "$forms" | grep -q "$keep"; then
    echo "  ok    kept: $keep"
  else
    echo "  FAIL  the filter removed content that is not a speaker note: $keep"
    fail=1
  fi
done

echo "3c. An unbalanced notes fence stops the commit instead of half-stripping"
printf -- '---\ntitle: T\n---\n\n## A\n\n::: {.notes}\nunclosed\n' > "$tmp/unbalanced.qmd"
if python3 scripts/strip_qmd_notes.py < "$tmp/unbalanced.qmd" >/dev/null 2>&1; then
  echo "  FAIL  strip_qmd_notes.py exited 0 on an unclosed notes div"
  fail=1
else
  echo "  ok    non-zero exit, so git aborts the add"
fi

echo "3d. A backup restores whatever spelling the author used, byte for byte"
cat > "$tmp/roundtrip.py" <<'PY'
import sys
sys.path.insert(0, "scripts")
import backup_notes as B
content = open(sys.argv[1], encoding="utf-8").read()
stripped, title_notes, div_notes = B.extract(content)
back = B._reinsert_exact(stripped, {"title_notes": title_notes, "notes": div_notes})
sys.exit(0 if back == content else 1)
PY
if python3 "$tmp/roundtrip.py" "$tmp/forms.qmd"; then
  echo "  ok    extract + _reinsert_exact round-trip is byte-exact"
else
  echo "  FAIL  a restore would not reproduce the file it backed up"
  fail=1
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
