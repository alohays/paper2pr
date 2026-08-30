# TTA 2026 Speaker-Script Review Deployment Plan

**Status:** READY FOR REMOTE DEPLOYMENT
**Date:** 2026-08-31
**Deck:** `Quarto/talks/tta-2026.qmd`
**Target:** GitHub Pages production deployment from `main`

## Requirements

- Preserve the complete Korean speaker script in the local QMD and its ignored backup.
- Commit no speaker-note text or Hangul from the English deck source.
- Commit only the English audit, timing, and plan records produced by the review.
- Use a new feature branch, an explicit file list, a merge commit, and the repository's standard PR workflow.
- Run the production-equivalent local site assembly before pushing.
- Wait for the `main` deployment workflow to complete successfully.
- Verify the public deck URL, asset availability, and absence of speaker notes in the deployed HTML.

## Execution

1. Reconfirm the clean-filter identity between the working QMD and `HEAD`.
2. Create a new `codex/` branch from the current reviewed deck state.
3. Run the production-equivalent local preview and asset checks.
4. Stage only the three English quality records and this deployment plan; confirm the QMD produces no staged change.
5. Commit, push, create a PR, and merge it to `main` with a merge commit.
6. Wait for GitHub Actions to render, strip notes, assemble, validate, and deploy the site.
7. Verify the production URL returns the final deck with zero note payloads, then record the deployment evidence.

## Verification

- Staged files contain no Hangul and no note markers.
- `git diff --cached --check` passes.
- The PR is merged to `main`.
- The GitHub Pages deployment workflow succeeds for the merge commit.
- The public deck returns HTTP 200.
- Public HTML contains 47 slide sections, zero `<aside class="notes">` blocks, and zero `data-notes` attributes.
- Local QMD and ignored backup retain 37 note divs plus the title note.

## Files Intended for Commit

- `quality_reports/plans/2026-08-30_tta-2026-korean-script-humanization.md`
- `quality_reports/plans/2026-08-31_tta-2026-script-deploy.md`
- `quality_reports/reviews/tta-2026-script-humanization-2026-08-30.md`
- `quality_reports/tta-2026_speaker_notes_report.md`

## Local Gate Evidence

- Production-equivalent preview rendered the deck and assembled `docs/` successfully.
- The assembled copy stripped 38 speaker-note payloads.
- All 206 local site references resolved.
- The public-form preview contains 47 slide sections and no speaker-note payloads.
