# Visual Audit Report: DreamZero

**Files Reviewed:** `Slides/DreamZero.tex` + `Quarto/DreamZero.qmd`
**Date:** 2026-03-15

---

## Summary

| Severity | Count |
|----------|-------|
| Critical | 1 |
| Medium   | 5 |
| Low      | 4 |

**Overall:** GOOD -- minor refinements needed

---

## Critical Issues

### C1. Slide 9b "AR vs. Bidirectional: My Take" is too sparse
- **Both .tex and .qmd:** This slide contains only a single `softbox` with one sentence.
- A full-screen slide with a single short remark feels like wasted vertical space.
- Same issue applies to: Slide 13b (GT Injection: My Take), Slide 23b (Cross-Embodiment: My Take), Slide 27b (VLA vs WAM: My Take).
- **Recommendation:** Consider merging "My Take" slides with their parent content slide, or adding a supporting visual/bullet to justify a standalone slide.

---

## Medium Issues

### M1. Potential overflow risk on Slide 26 (Ablation table)
- **Both files:** The ablation table has 5 columns and 8 data rows plus section headers.
- In Beamer (10pt), this table + the footnote ("All on PnP Easy...") is tight at the bottom margin.
- In Quarto, `.smaller` class is applied which helps, but the table still pushes close to the bottom.
- **Recommendation:** Verify rendered output; may need `\small` or `\footnotesize` wrapper in Beamer.

### M2. Slide 15 (38x Speedup) -- dense table
- Both files: 7-row table with 3 columns, plus a concluding line.
- Uses `\small` in Beamer and `.smaller` in Quarto.
- Bottom margin is tight -- the "Final: 14B at 7Hz..." line may clip in some aspect ratios.
- **Recommendation:** Test with actual rendering; consider `.smallest` in Quarto if needed.

### M3. Slide 23 (Cross-Embodiment Transfer) -- image + table combination
- Both files: An image at 75% width followed by a 3-row table.
- The combination of image + table on one slide could crowd the bottom.
- **Recommendation:** Verify rendered output for bottom-margin clearance.

### M4. Box fatigue pattern in Part 2 (Architecture)
- Slides 10-13 use: `methodbox`, `keybox`, `eqbox`, `eqbox`, `methodbox`, `methodbox`, `keybox` -- 7 consecutive boxes across 6 slides.
- This can create visual monotony where every slide looks "boxed."
- **Recommendation:** Consider removing boxes from one or two slides where the box adds only visual decoration, not semantic value (e.g., Slide 11c Notation Guide could use plain bullet list).

### M5. Image reuse: eval_bar_chart appears on both Slide 4b and Slide 19
- Same figure (`eval_bar_chart.pdf`/`.svg`) is used on two slides with different captions.
- Slide 4b: "VLA from-scratch at ~0% on diverse data"
- Slide 19: Full DreamZero results context
- **Recommendation:** Acceptable pedagogically (first as motivation, then as evidence), but consider adding a visual annotation or highlight to differentiate the second usage.

---

## Low Issues

### L1. No `\vfill` before attribution lines in Quarto
- Beamer uses `\hfill` before "--- Jim Fan" or "--- Joel Jang" attributions. In Quarto, these appear as plain left-aligned lines ("--- Jim Fan").
- The em-dash before the name renders correctly, but left-alignment differs from Beamer's right-alignment.
- **Recommendation:** Add `{style="text-align: right;"}` to attribution lines in Quarto for visual parity.

### L2. Section divider slides use `#` (h1) in Quarto vs `\begin{frame}[plain]` in Beamer
- Quarto section dividers use `# Title {background-color="#E8EDF5"}` which creates a level-1 heading slide.
- Beamer uses `\begin{frame}[plain]` with manual centering.
- Both render correctly, but the Quarto version includes a subtitle line ("Architecture & Training") as plain text below the h1, while Beamer uses `\higold{...}`.
- **Recommendation:** Wrap subtitle text in `[**Architecture & Training**]{.hi-gold}` in Quarto for color parity.

### L3. Quarto image heights not constrained
- Beamer uses `height=0.45\textheight,keepaspectratio` to prevent vertical overflow.
- Quarto only specifies `width="XX%"` without height constraints.
- Most figures appear fine due to aspect ratios, but tall/narrow figures could overflow.
- **Recommendation:** Add `height="auto" max-height="55%"` via style attributes for safety on image-heavy slides.

### L4. Font weight consistency in column layouts
- In Beamer columns (Slides 8, 9, 17a, 17b, 27, 34), headers use `\hi{Inputs:}` which renders as bold+blue.
- In Quarto, `[**Inputs:**]{.hi}` achieves the same effect.
- Consistent across both -- no action needed, but worth noting for future audits.

---

## Figures Audit

| Figure | Beamer (PDF) | Quarto (SVG) | Status |
|--------|:---:|:---:|:---:|
| dreamzero-header-v2 | OK | OK | OK |
| eval_bar_chart | OK | OK | OK |
| dreamzero_model | OK | OK | OK |
| bidiraug | OK | OK | OK |
| dreamzero_attention_figure | OK | OK | OK |
| dreamzero-flash_noise_distribution_comparison | OK | OK | OK |
| agibot_dc_envs | OK | OK | OK |
| agibot_stats_3 | OK | OK | OK |
| main_eval_setting | OK | OK | OK |
| unseen_success_rates | OK | OK | OK |
| dreamzero_gen | OK | OK | OK |
| posttrain | OK | OK | OK |
| embodiment_transfer | OK | OK | OK |
| yam_transfer | OK | OK | OK |
| free_form | OK | OK | OK |
| generated | OK | OK | OK |

All 16 figures have both PDF (Beamer) and SVG (Quarto) versions present.
