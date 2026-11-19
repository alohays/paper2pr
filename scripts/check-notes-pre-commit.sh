#!/bin/bash
# Inspect the staged blobs. --all checks the full index, including a fresh
# CI checkout whose author bypassed local hooks. Never print note contents.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"

if [[ -z "$(git config --get filter.strip-speaker-notes.clean || true)" ||
      "$(git config --bool --get filter.strip-speaker-notes.required || true)" != true ]]; then
  echo "error: speaker-note filtering must be configured and required. Run bash scripts/setup-git-filters.sh." >&2
  exit 1
fi

decks=':(glob)Quarto/**/*.qmd'
presenter_paths=(.speaker-notes/ Quarto/_script/)
if [[ "$#" == 1 && "$1" == --all ]]; then
  files=(git ls-files --cached -z -- "$decks" "${presenter_paths[@]}")
elif [[ "$#" == 0 ]]; then
  # A rename into Quarto also introduces a new deck. Treat it as an add.
  files=(git diff --cached --no-renames --name-only -z --diff-filter=ACMT -- "$decks" "${presenter_paths[@]}")
else
  echo "Usage: bash scripts/check-notes-pre-commit.sh [--all]" >&2
  exit 2
fi

"${files[@]}" | while IFS= read -r -d '' file; do
  case "$file" in
    .speaker-notes/*|Quarto/_script/*)
      echo "error: a local-only presenter file was added to the index" >&2
      exit 1 ;;
  esac
  attribute="$(git check-attr --cached filter -- "$file")"
  if [[ "${attribute##*: }" != strip-speaker-notes ]]; then
    echo "error: the staged attributes do not cover $file with the speaker-note filter" >&2
    exit 1
  fi
  if ! git show ":$file" | python3 scripts/strip_qmd_notes.py --check; then
    echo "error: inspect speaker notes in the staged blob of $file" >&2
    exit 1
  fi
done
