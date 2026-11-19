#!/bin/bash
# Upload a deck's trimmed clips and posters to its GitHub Release, then verify.
#
# bash scripts/media_release.sh <Deck-or-videos.yml> [--check]
# Compare the lock to the current manifest, then upload the approved MP4 and
# poster for each release entry. --check probes those URLs without any writes.
# An all-classroom deck succeeds without contacting a remote service.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"

if [ $# -lt 1 ]; then
  echo "usage: bash scripts/media_release.sh <Deck> [--check]" >&2
  exit 2
fi
DECK="$1"; shift
CHECK=0
for arg in "$@"; do
  case "$arg" in
    --check) CHECK=1 ;;
    *) echo "error: unsupported release option" >&2; exit 2 ;;
  esac
done

# Write validated rows before invoking gh. Process substitution would hide
# the Python process's failure from Bash 3.2.
ROWS_FILE=$(mktemp)
trap 'rm -f "$ROWS_FILE"' EXIT
python3 - "$DECK" > "$ROWS_FILE" <<'PYTHON'
import sys
sys.path.insert(0, "scripts")
import deckpath, media_prep
from private_terms import contains_private, private_terms

try:
    terms = private_terms()
except ValueError:
    sys.exit("error: cannot read the external private denylist")

def protected(value):
    return contains_private(value, terms)

try:
    home = deckpath.find_media(sys.argv[1])
    assets = media_prep.release_assets(home)
except (deckpath.DeckNotFound, deckpath.AmbiguousDeck, media_prep.ManifestError) as exc:
    message = str(exc)
    sys.exit(1 if protected(message) else f"error: {message}")
except (OSError, KeyError, ValueError, TypeError):
    sys.exit("error: invalid or missing media lock; run media_prep.py")

if assets:
    public = [home.release_tag] + [value for row in assets for value in row]
    if any(protected(value) for value in public):
        message = "error: a private term occurs in public release metadata"
        sys.exit(1 if protected(message) else message)
    # Emit the entire validated plan together. The directory is local input
    # to gh and must never be included in public notes or progress messages.
    if "\n" in str(home.videos_dir):
        sys.exit("error: media directory must fit on one line")
    print(home.release_tag)
    print(home.videos_dir)
    for filename, url in assets:
        print(f"{filename}|{url}")
PYTHON
if [ ! -s "$ROWS_FILE" ]; then
  echo "No clips approved for release."
  exit 0
fi
ROWS=()
{
  IFS= read -r TAG
  IFS= read -r VIDEOS_DIR
  while IFS= read -r line; do ROWS+=("$line"); done
} < "$ROWS_FILE"
NAME="${TAG#media-}"
if [ "$CHECK" -eq 0 ]; then
  FILES=()
  for row in "${ROWS[@]}"; do
    file="${row%%|*}"
    [ -f "$VIDEOS_DIR/$file" ] || { echo "error: prepared $file is missing; run media_prep.py" >&2; exit 1; }
    FILES+=("$VIDEOS_DIR/$file")
  done

  if gh release view "$TAG" >/dev/null 2>&1; then
    echo "release $TAG exists"
  else
    echo "creating release $TAG"
    gh release create "$TAG" \
      --title "Media: $NAME" \
      --notes "Approved clips and posters for the $NAME deck. See the presentation for publisher credits." \
      --latest=false
  fi

  echo "uploading ${#FILES[@]} file(s) to $TAG"
  gh release upload "$TAG" "${FILES[@]}" --clobber
fi

# GitHub answers a release asset with a 302 to a signed CDN URL; follow it.
# A freshly uploaded asset can 404 on the public URL for a few minutes while
# the API already reports it as "uploaded" (measured 2026-08-19: about three
# minutes), so right after an upload each URL is polled for up to ten
# minutes. --check asks once: it is a verdict, not a wait.
if [ "$CHECK" -eq 0 ]; then TRIES=40; else TRIES=1; fi
status_of() {
  local url="$1" code="" try=0
  while [ $try -lt $TRIES ]; do
    code=$(curl -sIL -o /dev/null -w '%{http_code}' "$url" || echo 000)
    [ "$code" = "200" ] && break
    try=$((try + 1))
    [ $try -lt $TRIES ] && sleep 15
  done
  echo "$code"
}

echo "verifying assets on $TAG"
missing=0
for row in "${ROWS[@]}"; do
  url="${row#*|}"
  code=$(status_of "$url")
  if [ "$code" = "200" ]; then
    echo "  200  $url"
  else
    echo "  $code  $url   MISSING"
    missing=$((missing + 1))
  fi
done

if [ "$missing" -gt 0 ]; then
  echo "$missing asset(s) missing from $TAG" >&2
  exit 1
fi
echo "all ${#ROWS[@]} assets answer 200"
