# DGIST W02 design pass (2026-09-02)

The deck `lectures/dgist-2026f-w02` was authored and published on 2026-08-31.
Viewed at 1280x720, several slides ran to the edge of the frame or into the
footnote, and running text broke with a single word stranded on the last line.
This pass fixes layout, alignment and sizing only; no number, source or claim
changes. Decisions were taken with the presenter on a rendered audit board
(current screenshot beside scaled mockups of each option).

## Method

- Every slide measured in headless Chrome at the 1280x720 canvas (all
  fragments revealed): section overflow, the lowest in-flow box against the
  footnote or the bottom padding, per-block line counts and last-line word
  counts, image natural vs rendered size. Script kept outside the repo.
- All 61 screenshots (47 slides plus fragment states) reviewed by eye.
- The TTA deck (`talks/tta-2026`, published) measured before and after the
  theme change, since it shares `clean-academic.scss`.

## Findings (before)

| Slide | Measured | Seen |
|---|---|---|
| S15 GPT | last line 9px into the footnote | answer "English." alone on a line |
| S17 DALL-E | captions 6px into the footnote | |
| S20 Atlas parkour | 9px past the bottom padding | video 512px wide, bullets at full size |
| S26 RT-2 | 25px past the bottom padding | last bullet under the slide number |
| S36 timeline | "36 months" 12px into the footnote | |
| S13 / S16 / S24 / S28 / S29 | charts linked as `<img>` SVG | Helvetica in the chart, Source Sans Pro around it; axis text 15-19px on screen |
| S06 / S46 QR fallback | | keybox wrapped "code announced in / class" |
| S09 / S22 / S37 / S42-S44 | one-word last lines | "hard." / "give it a body?" / "humanoid maker." / "video." |
| S37 industry | | three centred 40px paragraphs, six lines |
| S42-S44 roadmap | thumbnails 202x105 and 272x145 | contained images read as white boxes; text taller than the thumb; two-row slides 176px short of the footnote |
| S45 takeaways | | item 1 an `ol` with the orange marker, items 2-3 plain paragraphs |
| S08 | | title alone before the first click |

## Decisions (with the presenter)

1. CSS placement: generic rules in the theme (verified against the TTA deck),
   one-off geometry in `Quarto/lectures/dgist-2026f-w02.css`.
2. Video card plus bullets (S20, S26, S32): the theme's chart rule (bullets
   0.85em) extended to `figure.video-card`; the with-list video cap raised
   from 288px to 300px (a 533-wide clip). 315px was tried first and left S26
   10px over.
3. Roadmap (S42-S44): rows kept, thumbnails 300x160 (two-row slides 338x190),
   title 0.9em bold and description 0.8em; document-like images contained on a
   pale ground, photos cover-cropped.
4. Industry (S37): a label / text grid, left-aligned, text at 0.85em.
5. S08: a `.question-overlay` statement ("Hands up: did Atlas move on its
   own?") centred before the first click, fading out with the first fragment.
6. Charts: a new `{{< inline-svg >}}` shortcode inlines the five own-work SVGs
   (theme font, CSS variables reach the shapes); the files got id-scoped
   styles and unique title/desc ids; S13 and S16 at 60%, S24 and S28 at 100%,
   S29 at 92%.

## Changes

- `Quarto/clean-academic.scss`: `text-wrap: pretty` on p / li / figcaption,
  `text-wrap: balance` on h2 / `.statement` / standalone centred p;
  `$video-cap-with-list: 300px`; the 0.85em bullet rule covers
  `figure.video-card`; `figure.chart-figure > svg` sized like `svg.chart`;
  `.incremental` lists centred like top-level lists; `.qr-block > .keybox`
  nowrap and centred; `.question-overlay`.
- `Quarto/_filters/inline-svg.lua` (new), wired in `Quarto/_quarto.yml`.
- `Quarto/lectures/dgist-2026f-w02.css` (new): `.meta-line`, `.tight`,
  `.fact-grid`, `.roadmap`, `ol.takeaways`.
- `Quarto/lectures/dgist-2026f-w02.qmd`: S08 overlay and fragment indices,
  S09 / S15 / S22 sentence breaks, S13 / S16 / S24 / S28 / S29 inline charts,
  S17 image cap 330px, S36 timeline 94% wide with a tighter row gap, S37
  grid, S42-S44 roadmap rows, S45 one `ol` with fragment items.
- `Figures/lectures/dgist-2026f-w02/s{13,16,24,28,29}-*.svg`: root ids,
  scoped styles, unique ids; S28 arrows as real arrows.
- `AGENTS.md`: the shortcode, the overlay, the line-breaking rule.

## Verification

- W02: 47 slides, no overflow, every in-flow box at least 14px above the
  footnote and inside the bottom padding (S26 685 of 688, S20 678, S15 29px
  above the footnote, S36 15px). Screenshots of every changed slide reviewed.
- `quality_score.py`: 100/100, no blockers.
- TTA deck re-rendered on the new theme: no slide overflows (the on-disk
  render measured beforehand had three slides 9px past the bottom padding;
  that render predated the deck's last text edits, so per-slide line diffs
  between the two are not attributable to the theme). The 5px footnote
  collision on slide 25 predates this pass and is unchanged. Slides 13, 14,
  19, 21, 34 and 37 reviewed as screenshots: bullets under a video card sit
  at 0.85em, nothing is clipped.
- `test_profiles.py`, `test_series.py`, `test_media.py`, `test_minyaml.py`,
  `test_korean_gate.sh`, `test_note_filter.sh`: pass.
- `export_pdf.sh`: the handout exports with the inlined charts.

## Left alone

- The semester map (S03, S41) is a series asset shared by every lecture of
  the course; its type is 24-27px on screen and it stays as generated.
- The Wooclap fallback ("code announced in class") stays until the Message
  wall exists; `series_assets.py` then replaces it with the QR.
