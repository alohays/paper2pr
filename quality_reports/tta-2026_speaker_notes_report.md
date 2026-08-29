# Speaker Notes Timing Report: tta-2026

**Date:** 2026-08-29
**Language:** Korean (280 Hangul syllables per minute planning rate; measured with `say -v Yuna`)
**Coverage:** 38 / 38 main-deck slides with notes (37 `::: {.notes}` blocks + title `data-notes`). The 9 appendix slides intentionally carry no notes: they are Q&A backup, not part of the timed talk.

## Budget Summary

| Section | Slides | Hangul Syllables | Notes |
|---|---:|---:|---|
| Opening (title + intro) | 2 | ~400 | one-claim statement planted in the title note |
| Act I: VLA today | 8 | ~1,130 | ends on the teleop bottleneck (the talk's setup) |
| Act II: World models | 8 | ~1,220 | pivot at "Two paradigms, one team" |
| Act III: WAM + climax | 12 | ~2,120 | Dyna-2 scale beat, data race, 1M divider, ICL wave |
| Act IV: Synthesis + closing | 8 | ~1,370 | closing note restates the one claim verbatim |
| **Total** | **38** | **6,237** | target 6,160 (22 speaking min x 280), band 5,544-6,776 |

## Measured Timing

- `say -v Yuna` on the full extracted script: **1,450.8 s = 24.2 min** of narration.
- Against the 22-minute speaking budget this is +10%, at the edge of tolerance.
- Live delivery adds slide transitions and clip-breathing beats (~2-3 min), but a
  large share of the video-slide notes are spoken OVER looping clips, which
  reclaims part of the 8-minute video budget. Realistic wall-clock estimate:
  **28-30 min for the 30-minute talk portion**, with the 10-minute Q&A as buffer.
- Recommendation: during the 8/30 rehearsal, if the first full run exceeds 30 min,
  trim the two longest notes (Five architectures ~261 syl, Zero-WAM ~238 syl) first.

## Quality Checklist

- [x] Verbatim spoken-Korean scripts (not talking points); formal hamnida register with a light haeyo mix
- [x] One claim threaded: title note -> slide 7 bottleneck -> DreamDojo/Two-paradigms -> closing sentence
- [x] Batch transitions chain (each batch opened by answering the previous batch's closing question)
- [x] Technical terms and proper nouns kept in English per the deck's ko-en convention
- [x] Facts follow the corrected slides (Elo 1736/1609 as of Aug 29; GEN-1.5 <0.15%; no stale numbers)
- [x] Forbidden content absent from notes: no consortium, no Yangjae, no "first in Korea", no internal names, no recruiting
- [x] Video-full notes include a clip-breathing beat
- [x] Render verified: 37 `<aside class="notes">` + 1 title `data-notes` in the HTML
- [x] Notes backed up: `.speaker-notes/talks/tta-2026.json` (gitignored); clean-filter leak check passed (filtered diff = blank lines only, committed once as normalization)
