#!/usr/bin/env bash
# Fresh render of one QMD or all publishable decks using the verified toolchain.
# Usage: scripts/render_decks.sh [deck|file.qmd] [--delivery public|classroom]
set -euo pipefail
root="$(cd "$(dirname "$0")/.." && pwd)"
cd "$root"
export PATH="$root/.tools/quarto/bin:$PATH"
expected=$(cat .quarto-version)
actual=$(quarto --version 2>/dev/null || true)
if [[ "$actual" != "$expected" ]]; then
  echo "This checkout requires Quarto $expected. Install that version on PATH or in .tools/quarto/." >&2
  exit 1
fi
deck=""
delivery=public
while [[ $# -gt 0 ]]; do
  case "$1" in
    --delivery) delivery=${2:?Expected public or classroom}; shift 2 ;;
    *) [[ -z "$deck" ]] || { echo "Expected one deck" >&2; exit 2; }
       deck=$1; shift ;;
  esac
done
case "$delivery" in public|classroom) ;; *) echo "Invalid delivery" >&2; exit 2 ;; esac

render() {
  local qmd
  case "$1" in
    *.qmd) qmd=$1 ;;
    *) qmd=$(python3 scripts/deckpath.py "$1" --field qmd) ;;
  esac
  [[ -f "$qmd" ]] || { echo "Deck source is missing" >&2; return 1; }
  echo "Rendering $(basename "$qmd") for $delivery delivery"
  (cd "$(dirname "$qmd")" && quarto render "$(basename "$qmd")" --to revealjs -M "delivery:$delivery" --quiet)
}

if [[ -n "$deck" ]]; then
  render "$deck"
else
  # Capture the producer's exit status before entering the loop.
  decks=$(python3 scripts/deckprofile.py --list-publishable)
  while IFS= read -r slug; do
    [[ -z "$slug" ]] || render "$slug"
  done <<< "$decks"
fi
