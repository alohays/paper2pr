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
PLAIN="quality_reports/zz-korean-gate-probe.md"
tmp="$(mktemp -d)"
trap 'rm -rf "$tmp" "$PROBE_QMD" "$PROBE_CFG" "$PLAIN"' EXIT

fail=0

# Korean assembled from escapes so this file itself stays pure ASCII and does
# not trip the very hook it is testing. Written with literal Hangul first,
# which the hook promptly rejected -- the escapes are not decoration.
korean="$(python3 -c 'print("\uc774\uac83\uc740 \ud55c\uad6d\uc5b4 \uc2ac\ub77c\uc774\ub4dc \ubcf8\ubb38\uc785\ub2c8\ub2e4.")')"

write_probe_deck() {
  mkdir -p "$(dirname "$PROBE_QMD")"
  printf '## %s\n\n- %s\n' "$korean" "$korean" > "$PROBE_QMD"
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
write_probe_deck
stage "$PROBE_QMD"
expect "Korean slide text blocks the commit" 1 "$(run_hook)"

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

unset GIT_INDEX_FILE
echo
if [ "$fail" -eq 0 ]; then
  echo "PASS"
else
  echo "FAIL"
fi
exit "$fail"
