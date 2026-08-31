# DGIST W02 Authoring Execution Ledger

This file does not replace or reinterpret the completed deck plan. It tracks implementation in the exact order of `deck-plan.md` section 5, with the section 1b audit ledger taking precedence over all lower-priority text.

## User-owned prerequisites and locked fallbacks

- Wooclap room: use the planned fallback text, `code announced in class`, until the real room exists.
- TA reply: omit the unconfirmed W01 recap sentence and use `See the LMS for the official breakdown` for any assessment detail that would otherwise depend on confirmation.

## Authoring sequence

1. Scaffold `dgist-2026f-w02` with the locked lecture, series, audience, timing, language, delivery, source, and forbidden-term premises.
2. Verify the `dgist-2026f` series assets.
3. Author the absolute-path video manifest, scrub the two required windows, and run local-only media preparation.
4. Author the five planned SVG/redraw assets.
5. Import, crop, convert, and register third-party figures, including a valid NVIDIA GR00T N1 newsroom hero.
6. Author the 44 canonical slots as 47 rendered pages: S30 expands to two full-bleed pages, S32 expands to three, and the audited S40 split adds one page. Render and reach the quality gate.
7. Run the excellence review and fix all blocker/major findings.
8. Render and inspect every slide, export and inspect the PDF handout, and audit local-serving and deployment readiness without releasing media, deploying, merging, or pushing.
9. Build and verify the portable classroom bundle.
10. Add Korean speaker notes and back them up locally.
11. Re-run the full review, verify the Wooclap fallback state explicitly, and commit on `w02-authoring` only when the score is at least 90.

## Explicit non-actions

- Do not run `scripts/media_release.sh`.
- Do not merge into `main`, push, publish, or deploy.
- Do not replace the QMD source with PPTX or any parallel slide source.

## Resolved probe decisions

- Rendered page count: 47, preserving every explicitly specified full-bleed video page.
- `pi05-unseen-bedroom`: source segment `91-136`, retained as a 45-second 10x unseen-home montage with an accurate strip title.
