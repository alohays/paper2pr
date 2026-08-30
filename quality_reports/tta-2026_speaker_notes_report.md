# Speaker Notes Timing Report: tta-2026

**Date:** 2026-08-31
**Language:** Korean (280 Hangul syllables per minute planning rate; measured with `say -v Yuna`)
**Coverage:** 38 / 38 main-deck slides with notes (37 `::: {.notes}` blocks + title `data-notes`). The 9 appendix slides intentionally carry no notes: they are Q&A backup, not part of the timed talk.

Timing is informational for rehearsal. It was not an acceptance gate for the humanization pass.

## Budget Summary

| Section | Slides | Hangul Syllables | Notes |
|---|---:|---:|---|
| Opening (title + intro) | 2 | 393 | warm PG1004 introduction and the data-source thesis |
| Act I: VLA today | 6 | 873 | VLA recipe, dual system, and the teleop constraint |
| Act II: World models | 9 | 1,369 | dynamics supervision through DreamDojo and DreamZero |
| Act III: WAM + in-context learning | 15 | 2,627 | WAM definition, Dyna-2, data race, and ICL evidence |
| Act IV: Synthesis + closing | 6 | 971 | model metadata, field metrics, CostNav, and Q&A |
| **Total** | **38** | **6,233** | target 6,160 (22 speaking min x 280), band 5,544-6,776 |

## Measured Timing

- `say -v Yuna` on the final extracted script: **1,416.414785 s = 23.61 min** of narration.
- Against the 22-minute speaking budget this is +7.3%, inside the +/-10% planning tolerance.
- Live delivery adds slide transitions and clip-breathing beats (~2-3 min), but a
  large share of the video-slide notes are spoken OVER looping clips, which
  reclaims part of the 8-minute video budget. Realistic wall-clock estimate:
  **28-30 min for the 30-minute talk portion**, with the 10-minute Q&A as buffer.
- The presenter can adjust pacing or trim to taste after rehearsal; no further cut is required by this review.

## Quality Checklist

- [x] Verbatim spoken-Korean scripts (not talking points); warm formal register suitable for a technical invited talk
- [x] Humanizer, speakability, content, and narrative final gates: High 0 / Medium 0 on the same QMD hash
- [x] One claim develops from the data-source shift to dynamics supervision, action anchoring, comparison metadata, and field metrics
- [x] Canonical technical terms and proper nouns retained in English; ordinary sentence scaffolding naturalized into Korean
- [x] 277 / 277 sentences immediately readable; longest sentence 79 characters; no sentence at least 80 characters
- [x] Facts follow the corrected slides (dated Elo snapshot without a false rank; scoped WAM/latency claims; Dyna pretraining and ROI qualifiers; GEN-1.5 <0.15%)
- [x] Forbidden content absent from notes: no consortium, no Yangjae, no "first in Korea", no internal names, no recruiting
- [x] All 7 video-full notes include a specific viewing cue and a post-video interpretation
- [x] Speaker-note prose contains no em dash, en dash, or double-hyphen construction
- [x] Render verified: 47 sections, 37 `<aside class="notes">` blocks, and 1 title `data-notes` payload
- [x] Quality gate verified: 100/100 with no critical issue
- [x] Clean-filter output verified: 0 Hangul characters and 0 note markers
- [x] Notes backed up to `.speaker-notes/talks/tta-2026.json` (gitignored); backup `original_sha1` and `stripped_sha1` exactly match the current QMD
