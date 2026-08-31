# Deployment Readiness Audit: dgist-2026f-w02

**Date:** 2026-08-30
**Branch policy:** remain on `w02-authoring`; do not merge or deploy before the media-hosting decision
**Media policy:** local-only authoring; `media_release.sh` was not run

## Actual Local-Only State

- Rendered all five repository decks in a disposable working-tree copy.
- Stripped speaker notes; W02 removed 47 note carriers (title plus 46 slide notes).
- Assembled the site with the same scripts used by CI.
- `check_site_assets.py` failed on exactly 24 W02 references: 12 mp4 files and 12 posters under `Figures/lectures/dgist-2026f-w02/videos/`.
- No non-media asset failed. This is the expected authoring-mode deployment guard.

## Shadow Release-State Proof

- Generated the release-mode media payload in memory with `dry_run=True` and `local=False`.
- The payload differed from the real lock only by removing 12 `local_only` keys.
- No encode, poster extraction, size warning, or cut mismatch was requested.
- Replaced the lock only in the disposable copy and removed its local video directory to model CI.
- Re-rendered W02, stripped notes, assembled a second site, and passed all 233 local asset references.
- Structurally inspected Release URLs without making HTTP requests: exactly 24 W02 URLs matched the 12 expected clips and 12 expected posters, all referenced only by `slides/lectures/dgist-2026f-w02.html`.

## Remaining External Prerequisite

The repository-side transition is fully characterized, but remote availability cannot be proven while public media publication is forbidden. Before a future merge to `main`:

1. Approve the public-media decision.
2. Publish the 24 assets to `media-dgist-2026f-w02` using the repository workflow.
3. Confirm every Release URL answers 200.
4. Re-run `media_prep.py dgist-2026f-w02` without `--local` to write the release-mode lock.
5. Re-run the normal site and Release-media gates, then merge.

Until those steps are authorized, the correct deploy-ready state is this audited `w02-authoring` branch with an intentionally active local-media guard.
