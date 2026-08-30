# TTA 2026 Korean Speaker-Script Humanization Plan

**Status:** COMPLETED
**Date:** 2026-08-30
**Completed:** 2026-08-31
**Deck:** `Quarto/talks/tta-2026.qmd`
**Profile:** invited-talk
**Audience:** practitioner

The active goal authorizes direct improvement of the existing local-only Korean speaker script. Script length is measured for awareness but is not an acceptance gate for this pass.

## Requirements

- **MUST:** Review all 38 delivered-screen scripts: 37 note divs plus the title-slide note.
- **MUST:** Make every sentence immediately speakable when read verbatim at a podium.
- **MUST:** Remove AI-writing signals: inflated framing, forced groups of three, slogan-like metaphors, repetitive transition templates, staged punchlines, fake objections, and uniform mid-length cadence.
- **MUST:** Use warm formal Korean suitable for an invited technical seminar, with natural Korean-English code-mixing for established ML/robotics terms.
- **MUST:** Preserve every factual claim, number, date, model name, qualification, and public-scope constraint already cleared by the final fact audit.
- **MUST:** Add oral value beyond the visible slide: guide attention, explain why evidence matters, state caveats, and bridge to the next idea without rereading bullets.
- **MUST:** Use no em dash, en dash, or double-hyphen prose construction in speaker-note text.
- **MUST:** Preserve exact note syntax and the privacy boundary; back up notes after every writing pass.
- **SHOULD:** Allow uneven human rhythm: short reactions, occasional self-correction, and varied transitions where they fit the presenter's researcher voice.
- **SHOULD:** Keep the talk's one claim visible without mechanically restating it on every slide.
- **MAY:** Shorten or expand individual notes when oral clarity benefits. Total length is not a blocking criterion for this goal.

## Audit Lenses

1. **Humanizer lens:** scan for the explicit Humanizer pattern catalog and identify repeated AI-style constructions across the full script.
2. **Speakability lens:** read sentence rhythm as spoken Korean; flag breathless clauses, stacked modifiers, written-register endings, and awkward English insertion.
3. **Content-value lens:** compare every note with its slide; flag literal repetition, missing interpretation, weak visual guidance, and off-slide claims.
4. **Narrative lens:** check the title claim, section transitions, callbacks, contrast, and closing as one live seminar rather than 38 isolated paragraphs.

## Execution

1. Extract a numbered slide-to-note ledger from the current QMD and calculate baseline style statistics.
2. Run four independent read-only audits in parallel using the lenses above.
3. Rebut each proposal against the actual slide, audience, source-cleared claims, and surrounding transitions.
4. Rewrite the complete script in coherent batches, preserving facts while changing cadence and oral phrasing.
5. Perform a second Humanizer scan and a literal read-aloud pass on the final text.
6. Render the deck; verify 37 note asides plus one title note, all 47 slides, and no syntax/privacy regression.
7. Back up the final notes and update the timing/quality report with the humanization audit outcome.

## Verification

- 38/38 delivered screens retain complete Korean scripts.
- 0 malformed/unbalanced note fences; title note remains in YAML only.
- 0 em dashes, en dashes, or double-hyphen prose constructions inside note text.
- 0 unresolved High/Medium findings from the final Humanizer, speakability, content-value, and narrative passes.
- Render succeeds and local HTML contains 37 `<aside class="notes">` blocks plus one title `data-notes` payload.
- Git-filtered QMD remains free of notes and Hangul.
- Final note backup hash matches the working QMD.

## Files That May Change

- `Quarto/talks/tta-2026.qmd` (local-only note text; visible slide content should remain unchanged)
- `.speaker-notes/talks/tta-2026.json` (gitignored backup)
- `quality_reports/tta-2026_speaker_notes_report.md`
- `quality_reports/reviews/tta-2026-script-humanization-2026-08-30.md`
- `quality_reports/plans/2026-08-30_tta-2026-korean-script-humanization.md`

## Outcome

All requirements and verification checks passed on QMD SHA-256 `0da7de4c38ca0caf62a5aeb05ec1b30718fabfcae2a6084744429959a6758ed0`. The four independent final gates each reported High 0 / Medium 0. The deck rendered at 100/100, contained the expected 37 note asides plus one title-note payload, and produced a clean-filtered QMD with zero Hangul characters and zero note markers. The final local backup hashes match the current source and stripped source exactly.
