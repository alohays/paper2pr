#!/bin/bash
# Upload a deck's trimmed clips and posters to its GitHub Release, then verify.
#
# The media a deck shows never enters git (Figures/**/videos/ is ignored); it
# lives on a public GitHub Release tagged media-<deck>, the way the SUNY deck's
# clips live on media-v1. scripts/media_prep.py writes the files and the lock
# file (videos.json) whose release_url / poster_url already point at this tag;
# this script makes those URLs true.
#
#   bash scripts/media_release.sh <Deck>            create the release if it is
#                                                   missing, upload every
#                                                   <slug>.mp4 and
#                                                   <slug>-poster.jpg listed in
#                                                   videos.json (--clobber), then
#                                                   verify each URL answers 200
#   bash scripts/media_release.sh <Deck> --check    verify only; exit 1 and list
#                                                   every asset that is missing
#
# <Deck> is anything scripts/deckpath.py accepts for the media fields: a bare
# name, genre/name, a videos.yml path or its directory (the fixture under
# Quarto/_fixtures/video/ releases as media-fixture-video).
#
# Refuses to run when videos.json is older than videos.yml (the manifest
# changed and media_prep.py has not been run) and when any entry's "cut"
# record in videos.json disagrees with its manifest fields (media_prep.py
# --only skipped it after a segment / keep_audio / source change): in both
# cases the files on disk may not be what the deck will ask for, and the
# Release must never carry the old cut under the new caption.
#
# Releases are public as soon as the media is ready (presenter, 2026-08-19);
# the notes name the manifest so a reader can find the publisher of every
# third-party clip. Needs gh (authenticated) and curl.

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
    *) echo "unknown option: $arg" >&2; exit 2 ;;
  esac
done

MANIFEST=$(python3 scripts/deckpath.py "$DECK" --field videos-manifest)
LOCK=$(python3 scripts/deckpath.py "$DECK" --field videos-lock)
VIDEOS_DIR=$(python3 scripts/deckpath.py "$DECK" --field videos-dir)
TAG=$(python3 scripts/deckpath.py "$DECK" --field release-tag)
SLUG=$(python3 scripts/deckpath.py "$DECK" --field media-slug)
NAME="${TAG#media-}"

[ -f "$MANIFEST" ] || { echo "error: no manifest at $MANIFEST" >&2; exit 1; }
[ -f "$LOCK" ] || { echo "error: no lock file at $LOCK (run: python3 scripts/media_prep.py $DECK)" >&2; exit 1; }
if [ "$LOCK" -ot "$MANIFEST" ]; then
  echo "error: $LOCK is older than $MANIFEST; run: python3 scripts/media_prep.py $DECK" >&2
  exit 1
fi

# Every file the lock lists, plus the URL it promises for each, as
# "file|url" lines (bash 3.2 on macOS has no mapfile; a while-read loop over
# a temp file keeps the array in the parent shell).
ROWS_FILE=$(mktemp)
trap 'rm -f "$ROWS_FILE"' EXIT
python3 - "$LOCK" "$DECK" > "$ROWS_FILE" <<'PY'
import json, sys
sys.path.insert(0, "scripts")
import media_prep
lock = json.load(open(sys.argv[1]))
bad = media_prep.lock_mismatches(lock)
if bad:
    print("error: the files on disk were not cut with what the manifest says now:", file=sys.stderr)
    for line in bad:
        print("  " + line, file=sys.stderr)
    print(f"run: python3 scripts/media_prep.py {sys.argv[2]}   (without --only)", file=sys.stderr)
    sys.exit(1)
for v in lock["videos"]:
    print(f"{v['file']}|{v['release_url']}")
    print(f"{v['poster_file']}|{v['poster_url']}")
PY
ROWS=()
while IFS= read -r line; do
  [ -n "$line" ] && ROWS+=("$line")
done < "$ROWS_FILE"
[ ${#ROWS[@]} -gt 0 ] || { echo "error: $LOCK lists no videos" >&2; exit 1; }

if [ "$CHECK" -eq 0 ]; then
  if grep -q '"local_only": true' "$LOCK"; then
    echo "note: $LOCK was written with --local; uploading anyway, but re-run" >&2
    echo "      media_prep.py without --local before the deck is deployed." >&2
  fi

  FILES=()
  for row in "${ROWS[@]}"; do
    file="${row%%|*}"
    [ -f "$VIDEOS_DIR/$file" ] || { echo "error: $VIDEOS_DIR/$file is missing; run media_prep.py" >&2; exit 1; }
    FILES+=("$VIDEOS_DIR/$file")
  done

  if gh release view "$TAG" >/dev/null 2>&1; then
    echo "release $TAG exists"
  else
    echo "creating release $TAG"
    MANIFEST_REL=$(python3 -c "import os,sys; print(os.path.relpath(sys.argv[1], sys.argv[2]))" "$MANIFEST" "$REPO_ROOT")
    gh release create "$TAG" \
      --title "Media: $NAME" \
      --notes "Trimmed clips and posters for the $NAME deck. Third-party clips are quoted from the publishers listed in $MANIFEST_REL for teaching; see the manifest for sources." \
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

echo "verifying $SLUG assets on $TAG"
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
