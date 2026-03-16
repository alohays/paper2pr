# Visual Audit: DreamDojo.qmd

**Date:** 2026-03-17
**Reviewer:** slide-auditor agent
**File:** `Quarto/DreamDojo.qmd`

---

## Summary

| Severity | Count |
|----------|-------|
| Critical | 2 |
| Medium | 5 |
| Low | 4 |

---

## Critical Issues

### C1. Slide 1 (Title) -- Potential Vertical Overflow

The title slide uses `{background-color="white"}` with an untitled `##` heading, an 85%-width teaser SVG, AND a `<video>` element with `max-height: 300px`. Combined, these two media elements likely exceed the 720px slide height after accounting for heading space, margins, and padding.

**Fix:** Either reduce the teaser image width to ~60% or remove the video from the title slide and place it on a dedicated slide. Alternatively, set the video `max-height` to `200px`.

### C2. Slide 20 (Distillation Results) -- Dense Multi-Media Stacking

This slide has `.smaller` class but packs: a resultbox with a 7-column table, a `<video>` element at 300px height, AND a two-column image layout. This is extremely dense and risks vertical overflow on 720px slides.

**Fix:** Split into two slides: one for the table + video, one for the comparison images. Or remove the video and use it on the prior slide.

---

## Medium Issues

### M1. Video Elements Lack Fallback Text

Lines 33, 549, 665, 727: Four `<video>` tags use raw HTML with no fallback text for offline viewing or accessibility. If the remote URLs are unreachable, the viewer sees an empty box.

**Fix:** Add fallback text between `<video>` tags: `<video ...>Video: [description]</video>`.

### M2. Slide 6 (Three Data Sources) -- Column Width Inside Methodbox

Three-column layout inside a methodbox with 32% per column is tight at 85% font. The text "Apple Vision Pro, 194 skills, 5 scenes" may wrap awkwardly depending on font rendering.

**Fix:** Consider reducing to two columns or using `.smallest` class for the data mixture content.

### M3. Slides 28-31 (Code Insights) -- Box Fatigue

Four consecutive slides all use `methodbox` + `softbox` pattern. The visual rhythm becomes monotonous.

**Fix:** Vary the box types (use `keybox` for the most important finding) or use a different layout for one of the four.

### M4. design_compressed.svg Used Twice

The same figure (`design_compressed.svg`) appears on both Slide 13 (line 368) and Slide 24 (line 649) at different widths (80% vs 72%). Deliberate repetition is fine pedagogically but may confuse viewers who notice.

**Fix:** Add a caption or annotation distinguishing the two uses ("revisited with ablation context").

### M5. Citation Attribution on Slide 4 -- Raw Styling

Line 114: `[--- @gao2026dreamdojo]{style="display: block; text-align: right;"}` uses inline CSS. This works but is inconsistent with the `.footnote` class pattern used elsewhere in the project.

**Fix:** Use `.footnote` class or define a `.cite-right` utility class.

---

## Low Issues

### L1. Inconsistent Image Width Specifications

Images range from 70% to 100% width with no clear pattern. Most are 80-90%, but some columns use 100% which may look different from the majority.

### L2. No Slide Numbers in Section Dividers

Section divider slides (lines 210, 307, 477, 572, 747, 853) use `# Heading {background-color="..."}` which produces full-screen centered titles. Slide numbers are suppressed by default on these, which is fine but worth noting for navigation.

### L3. Video Element Inline Styles

Video elements use inline `style` attributes rather than CSS classes. The SCSS theme has `.reveal video` rules that should handle most styling, but `max-height: 300px` overrides the theme's `65vh` default.

### L4. Font Size Captions via Inline Style

Lines 175, 176, 555, 559: `{style="font-size: 0.75em;"}` is used for image captions. The theme's `figcaption` style handles this natively when using proper `<figure>` markup.

---

## Overall Visual Assessment

**GOOD** -- The deck is visually clean with good use of the box environment hierarchy. The main risks are two potentially overflowing slides (title and distillation results) and some monotony in the code insights section. All figures exist and reference correct SVG files.
