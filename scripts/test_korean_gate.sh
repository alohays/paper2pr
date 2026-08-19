#!/bin/bash
# Regression test for the Korean pre-commit gate.
#
# This hook has a history of passing while checking nothing: the original
# used `grep -cP` with \uXXXX escapes, which is wrong twice over (BSD grep has
# no -P, and PCRE spells it \x{AC00}), and the error was swallowed by
# `2>/dev/null || true`. A staged file of pure Korean exited 0 for months.
# So the gate does not get to be believed, only tested.
#
# What is verified here is the whole point of the deck config: a deck may
# carry Korean slides by declaring `language.slides: ko` in its own config,
# an English deck may carry up to `language.korean_allowance` Hangul
# characters (deck config, else its profile: lecture 300, the others 0),
# and everything else stays strict. The alternative was exempting
# Quarto/lectures/ as a path, which would have silently covered every future
# lecture, including the ones that should stay English.
#
# Runs against a throwaway index (GIT_INDEX_FILE), so it never touches what
# you have staged.
#
# Usage: bash scripts/test_korean_gate.sh

set -u

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"

PROBE_QMD="Quarto/lectures/zz-korean-gate-probe.qmd"
PROBE_CFG="Quarto/lectures/zz-korean-gate-probe.deck.yml"
PAPER_QMD="Quarto/papers/zz-korean-gate-probe-paper.qmd"
PAPER_CFG="Quarto/papers/zz-korean-gate-probe-paper.deck.yml"
PLAIN="quality_reports/zz-korean-gate-probe.md"
tmp="$(mktemp -d)"
trap 'rm -rf "$tmp" "$PROBE_QMD" "$PROBE_CFG" "$PAPER_QMD" "$PAPER_CFG" "$PLAIN"' EXIT

fail=0

# Korean assembled from escapes so this file itself stays pure ASCII and does
# not trip the very hook it is testing. Written with literal Hangul first,
# which the hook promptly rejected -- the escapes are not decoration.
korean="$(python3 -c 'print("\uc774\uac83\uc740 \ud55c\uad6d\uc5b4 \uc2ac\ub77c\uc774\ub4dc \ubcf8\ubb38\uc785\ub2c8\ub2e4.")')"

# Exactly N Hangul syllables (no spaces), for the allowance arithmetic.
hangul_n() {
  python3 -c 'import sys; print("\uac00" * int(sys.argv[1]))' "$1"
}

write_probe_deck() {
  mkdir -p "$(dirname "$PROBE_QMD")"
  printf '## %s\n\n- %s\n' "$korean" "$korean" > "$PROBE_QMD"
}

# An English lecture deck carrying exactly N Hangul characters on one slide.
# Hangul goes only in the body: a notes div would be stripped by the clean
# filter before the hook sees it, which is the point of counting the staged
# blob.
write_probe_deck_n() {
  mkdir -p "$(dirname "$1")"
  printf '## An English slide\n\n- Body text with a gloss: %s\n' "$(hangul_n "$2")" > "$1"
}

# 400 Hangul characters beats every profile allowance (lecture says 300), so
# the declaration tests below hold regardless of which profile the probe
# deck resolves to.
write_probe_deck_over() {
  write_probe_deck_n "$PROBE_QMD" 400
}

stage() {
  export GIT_INDEX_FILE="$tmp/index"
  rm -f "$GIT_INDEX_FILE"
  git read-tree HEAD
  git add -- "$@"
}

run_hook() {
  bash scripts/check-korean-pre-commit.sh >"$tmp/out" 2>&1
  echo $?
}

expect() {
  local label="$1" want="$2" got="$3"
  if [ "$want" = "$got" ]; then
    echo "  ok    $label"
  else
    echo "  FAIL  $label (hook exited $got, expected $want)"
    sed 's/^/          /' "$tmp/out"
    fail=1
  fi
}

echo "0. The hook git actually runs is the script this repo maintains"
# git runs .git/hooks/pre-commit, a copy. Editing the script under scripts/
# changes nothing until setup-git-filters.sh copies it over, so every test
# below could pass against a stale hook. Ask this first.
if [ ! -x .git/hooks/pre-commit ]; then
  echo "  FAIL  no pre-commit hook installed -- run scripts/setup-git-filters.sh"
  fail=1
elif cmp -s .git/hooks/pre-commit scripts/check-korean-pre-commit.sh; then
  echo "  ok    installed hook matches scripts/check-korean-pre-commit.sh"
else
  echo "  FAIL  installed hook is stale -- run scripts/setup-git-filters.sh"
  echo "        Until you do, your edits to the gate are not in effect."
  fail=1
fi

echo "1. A deck with Korean slides and no declaration is blocked"
write_probe_deck_over
stage "$PROBE_QMD"
expect "Korean slide text over the allowance blocks the commit" 1 "$(run_hook)"

echo "2. The same deck passes once its config declares Korean slides"
cat > "$PROBE_CFG" <<'YML'
profile: lecture
title: "Korean gate probe"
language:
  slides: ko
  notes: ko
YML
stage "$PROBE_QMD" "$PROBE_CFG"
expect "language.slides: ko allows it" 0 "$(run_hook)"

echo "3. Declaring English again puts the deck back under the gate"
cat > "$PROBE_CFG" <<'YML'
profile: lecture
title: "Korean gate probe"
language:
  slides: en
  notes: ko
YML
stage "$PROBE_QMD" "$PROBE_CFG"
expect "language.slides: en blocks it again" 1 "$(run_hook)"

echo "4. The exemption does not leak to files that are not decks"
mkdir -p "$(dirname "$PLAIN")"
printf '# probe\n\n%s\n' "$korean" > "$PLAIN"
stage "$PLAIN"
expect "a Korean report is still blocked" 1 "$(run_hook)"

echo "5. An English deck is unaffected"
printf '## A slide\n\n- Body text.\n' > "$PROBE_QMD"
rm -f "$PROBE_CFG"
stage "$PROBE_QMD"
expect "English slides pass" 0 "$(run_hook)"

echo "6. An English lecture deck may carry a little Hangul (korean_allowance)"
# The config omits korean_allowance on purpose: the lecture profile's 300
# must be what applies, and the deck must not need to repeat it.
cat > "$PROBE_CFG" <<'YML'
profile: lecture
title: "Korean gate probe"
language:
  slides: en
  notes: ko
YML
write_probe_deck_n "$PROBE_QMD" 10
stage "$PROBE_QMD" "$PROBE_CFG"
expect "10 Hangul characters pass under the lecture allowance of 300" 0 "$(run_hook)"
if grep -q "10 Hangul characters within the allowance of 300" "$tmp/out"; then
  echo "  ok    the hook reports count and allowance"
else
  echo "  FAIL  the hook did not report '10 Hangul characters within the allowance of 300'"
  sed 's/^/          /' "$tmp/out"
  fail=1
fi

echo "7. The same lecture deck is blocked once it exceeds the allowance"
write_probe_deck_n "$PROBE_QMD" 400
stage "$PROBE_QMD" "$PROBE_CFG"
expect "400 Hangul characters are blocked against 300" 1 "$(run_hook)"
if grep -q "400 Hangul characters on the slides, allowance is 300" "$tmp/out"; then
  echo "  ok    the block message states count vs allowance"
else
  echo "  FAIL  the block message does not state '400 ... allowance is 300'"
  sed 's/^/          /' "$tmp/out"
  fail=1
fi

echo "8. A deck-level korean_allowance overrides the profile"
cat > "$PROBE_CFG" <<'YML'
profile: lecture
title: "Korean gate probe"
language:
  slides: en
  notes: ko
  korean_allowance: 5
YML
write_probe_deck_n "$PROBE_QMD" 10
stage "$PROBE_QMD" "$PROBE_CFG"
expect "10 Hangul characters are blocked against a deck allowance of 5" 1 "$(run_hook)"
sed -i.bak 's/korean_allowance: 5/korean_allowance: 20/' "$PROBE_CFG" && rm -f "$PROBE_CFG.bak"
stage "$PROBE_QMD" "$PROBE_CFG"
expect "the same 10 pass against a deck allowance of 20" 0 "$(run_hook)"

echo "9. A paper deck has no allowance: one Hangul character is blocked"
# The config omits korean_allowance; paper-review.yml says 0, so 0 applies.
cat > "$PAPER_CFG" <<'YML'
profile: paper-review
title: "Korean gate probe (paper)"
language:
  slides: en
  notes: ko
YML
write_probe_deck_n "$PAPER_QMD" 1
stage "$PAPER_QMD" "$PAPER_CFG"
expect "1 Hangul character on a paper deck is blocked" 1 "$(run_hook)"
if grep -q "1 Hangul characters on the slides, allowance is 0" "$tmp/out"; then
  echo "  ok    the allowance resolved to 0 from the profile"
else
  echo "  FAIL  expected 'allowance is 0' for a paper deck without a deck-level value"
  sed 's/^/          /' "$tmp/out"
  fail=1
fi
allowance_seen=$(python3 scripts/deckprofile.py "$PAPER_QMD" --field korean_allowance 2>/dev/null)
if [ "$allowance_seen" = "0" ]; then
  echo "  ok    deckprofile reports korean_allowance 0 for the paper deck"
else
  echo "  FAIL  deckprofile reported korean_allowance '$allowance_seen' for the paper deck"
  fail=1
fi

echo "10. Hangul inside speaker notes never counts (the clean filter strips it)"
cat > "$PROBE_CFG" <<'YML'
profile: paper-review
title: "Korean gate probe"
language:
  slides: en
  notes: ko
YML
printf '## An English slide\n\n- Body text.\n\n::: {.notes}\n%s\n:::\n' "$(hangul_n 50)" > "$PROBE_QMD"
stage "$PROBE_QMD" "$PROBE_CFG"
expect "50 Hangul characters in notes pass at allowance 0" 0 "$(run_hook)"

unset GIT_INDEX_FILE
echo
if [ "$fail" -eq 0 ]; then
  echo "PASS"
else
  echo "FAIL"
fi
exit "$fail"
