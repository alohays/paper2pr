# Speaker Notes Timing Report: tta-2026

**Date:** 2026-08-29
**Language:** Korean (280 Hangul syllables per minute planning rate; measured with `say -v Yuna`)
**Coverage:** 38 / 38 main-deck slides with notes (37 `::: {.notes}` blocks + title `data-notes`). The 9 appendix slides intentionally carry no notes: they are Q&A backup, not part of the timed talk.

## Budget Summary

| Section | Slides | Hangul Syllables | Notes |
|---|---:|---:|---|
| Opening (title + intro) | 2 | 419 | one-claim statement planted in the title note |
| Act I: VLA today | 6 | 898 | ends on the teleop bottleneck (the talk's setup) |
| Act II: World models | 9 | 1,404 | pivots through DreamDojo and DreamZero |
| Act III: WAM + in-context learning | 15 | 2,515 | scoped WAM definition, Dyna-2, data race, ICL wave |
| Act IV: Synthesis + closing | 6 | 694 | comparison, public team coda, CostNav, and Q&A |
| **Total** | **38** | **5,930** | target 6,160 (22 speaking min x 280), band 5,544-6,776 |

## Measured Timing

- `say -v Yuna` on the final extracted script: **1,434.8 s = 23.91 min** of narration.
- Against the 22-minute speaking budget this is +8.7%, inside the +/-10% planning tolerance.
- Live delivery adds slide transitions and clip-breathing beats (~2-3 min), but a
  large share of the video-slide notes are spoken OVER looping clips, which
  reclaims part of the 8-minute video budget. Realistic wall-clock estimate:
  **28-30 min for the 30-minute talk portion**, with the 10-minute Q&A as buffer.
- Recommendation: during the 8/30 rehearsal, if the first full run exceeds 30 min,
  trim the two longest remaining notes (Zero-WAM ~237 syllables and Dyna-2 hero ~233) first.

## Quality Checklist

- [x] Verbatim spoken-Korean scripts (not talking points); formal hamnida register with a light haeyo mix
- [x] One claim threaded: title note -> slide 7 bottleneck -> DreamDojo/Two-paradigms -> closing sentence
- [x] Batch transitions chain (each batch opened by answering the previous batch's closing question)
- [x] Technical terms and proper nouns kept in English per the deck's ko-en convention
- [x] Facts follow the corrected slides (dated Elo snapshot without a false rank; scoped WAM/latency claims; Dyna pretraining and ROI qualifiers; GEN-1.5 <0.15%)
- [x] Forbidden content absent from notes: no consortium, no Yangjae, no "first in Korea", no internal names, no recruiting
- [x] Video-full notes include a clip-breathing beat
- [x] Render verified: 37 `<aside class="notes">` + 1 title `data-notes` in the HTML
- [x] Notes backed up: `.speaker-notes/talks/tta-2026.json` (gitignored); clean-filter leak check passed (filtered diff = blank lines only, committed once as normalization)
