# TTA 2026 Final Audit and Deployment Plan

**Status:** APPROVED
**Date:** 2026-08-30
**Deck:** `Quarto/talks/tta-2026.qmd`
**Worktree:** `/Users/iyunseong/maangeek/paper2pr-tta`
**Branch:** `feat/tta-2026-deck`

The explicit goal objective authorizes this plan through production deployment. No additional scope clarification is required.

## Requirements

- **MUST (CLEAR):** Preserve all local-only speaker notes before repository work and never switch branches, check out files, or use stash operations in this worktree.
- **MUST (CLEAR):** Treat the existing deck as authored content. Challenge every new audit finding first and modify only findings that survive evidence-based rebuttal.
- **MUST (CLEAR):** Run the five independent slide-excellence components: source/layout audit, pedagogy and devil's-advocate review, proofreading, fact-checking against all 53 sources resolved from the current deck config, and a pixel-level render audit of every slide. The objective's source count of 52 is stale; fresh repository output is authoritative.
- **MUST (CLEAR):** Confirm every visible number is traceable to a declared source and that no confidential WoRV material, unpublished idea, internal project or dataset name, or hiring language is public.
- **MUST (CLEAR):** Render and score at least 95/100 with zero blockers, verify all released media, and validate the 22-minute speaking budget against the existing timing report and current notes.
- **MUST (CLEAR):** Reproduce the CI pipeline locally, prove the assembled site contains no speaker notes or leaked Korean note text, and verify site assets and release media.
- **MUST (CLEAR):** Commit only explicit English-language files, excluding `Figures/talks/tta-2026/videos`, push the existing branch, create and merge a PR server-side with `--repo alohays/paper2pr`, and never change the local branch.
- **MUST (CLEAR):** Wait for GitHub Actions deployment success, then verify the production deck, RevealJS navigation, video behavior, and landing-page entry in a real browser.
- **MUST (CLEAR):** Export the final PDF with the repository script, verify no Korean note leakage, and reconcile the existing offline kit with the final source.
- **MUST (CLEAR):** Report the live URL and absolute PDF path first, followed by measured gates, adopted fixes, rejected findings and reasons, and unresolved uncertainty.
- **MUST (CLEAR):** Do not send messages or email to any person.

## Guardrails

- Do not modify `Quarto/talks/tta-2026.deck.yml` merely to silence a gate.
- Do not stage the untracked `Figures/talks/tta-2026/videos` symlink or local media.
- Do not use `git checkout`, `git switch`, `git stash`, `git reset --hard`, or a local merge into `main`.
- Keep speaker-note backups in `.speaker-notes/`; they are local and gitignored.
- Keep all committed prose, report content, PR text, and commit messages in English.

## Execution

1. Capture the exact branch, worktree, clean-filter, note-backup, upstream, and GitHub state; compare the current deck with round-one reports and commits.
2. Resolve the deck profile and source-of-truth premises. Render and run the initial quality score and media release check.
3. Produce 1280x720 screenshots for all 47 rendered screens (title plus 46 authored slides) and launch five read-only review tracks in parallel. Each track receives the resolved profile, verbatim deck config, audience, report path, and its component-specific contract.
4. Audit current speaker-note timing, public-release restrictions, forbidden terms, the removed hiring chip, all visible numeric claims, figure attribution, and every rendered pixel.
5. Synthesize all reports into `quality_reports/tta-2026_slide_excellence.md`, explicitly rebut each proposed change, and classify it as adopted, rejected, or already satisfied.
6. Apply only adopted fixes using the QMD as the content source of truth. Re-back up notes after any QMD edit, then re-render, re-shoot affected/all slides, and repeat relevant checks.
7. Run the required local CI-equivalent pipeline into `_site`; inspect the assembled HTML for notes markers, note containers, Korean leakage, local-media references, RevealJS structure, and asset resolution.
8. Run final quality, media, proofreading, disclosure, source-traceability, and regression checks. Inspect the exact staged blobs to confirm notes and Korean text are absent before committing.
9. Commit the audit artifacts and any approved fixes on the existing branch, push it, create the PR against `main`, wait for checks, and merge server-side. Do not delete or change the local branch.
10. Wait for the deployment workflow, verify the production URL and landing page in-browser, test arrow-key navigation and representative video playback, and inspect production HTML for note leakage.
11. Export and inspect the final PDF. Compare hashes/content timestamps and deck revision metadata with the existing offline kit; regenerate the offline HTML/PDF only if it is stale, then re-verify it without committing local delivery artifacts.

## Files That May Change

- `quality_reports/plans/2026-08-30_tta-2026-final-audit-deploy.md`
- `quality_reports/reviews/tta-2026-*-2026-08-30.md`
- `quality_reports/reviews/tta-2026-2026-08-30.md`
- `quality_reports/tta-2026_slide_excellence.md`
- `Quarto/talks/tta-2026.qmd` only for findings that survive rebuttal
- Existing figure or manifest source files only if a surviving factual or rendering defect requires them
- Local-only outputs under `.speaker-notes/`, `_site/`, `exports/`, and `/Users/iyunseong/maangeek/tta-2026-media/offline-kit/`

## Verification Gates

- `python3 scripts/quality_score.py Quarto/talks/tta-2026.qmd --summary`: score at least 95, zero blockers.
- `python3 scripts/shoot_slides.py tta-2026 --out /tmp/tta-2026-shots`: all 47 rendered screens captured and visually inspected.
- `bash scripts/media_release.sh tta-2026 --check`: all declared release assets return 200.
- CI-equivalent local sequence: `render_decks.sh`, `strip_notes.sh Quarto`, `assemble_site.sh _site`, `check_site_assets.py _site`, `check_release_media.py _site`.
- Assembled-site scans: zero notes divs, `data-notes`, title-note attributes, Korean speaker-note leakage, or local video paths.
- `bash scripts/export_pdf.sh tta-2026`: successful PDF with valid page count and no leaked Korean note text.
- Git staged-blob audit: intended files only, QMD clean filter active, zero staged note blocks or disallowed Hangul.
- GitHub PR checks and Pages deployment workflow successful.
- Production HTTP/browser checks: deck URL 200 as RevealJS, keyboard navigation works, representative videos load/play, landing page links the deck, and public HTML has no notes.

## Completion Evidence

The final report will record command outputs, counts, hashes or paths where useful, the PR and workflow URLs, production checks, every adopted fix, every deliberately rejected finding with its rebuttal, and any residual risk.
