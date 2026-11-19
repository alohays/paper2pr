---
paths:
  - "Quarto/**/*.qmd"
  - "Quarto/**/*.scss"
---

# Slide Design Principles (MANDATORY for new decks)

Three principles govern every new slide deck. The main theme
(`Quarto/clean-academic.scss`) enforces the layout; this rule governs the
content decisions the theme cannot make for you.

Legacy decks pinned to `clean-academic-legacy.scss` (DreamZero, DreamDojo,
RoboTTT) and SUNY's own theme are exempt — do not retrofit them.

> **This file is the shared core. The numbers below are the paper-review
> defaults.** What actually applies to a given deck comes from its profile in
> `.claude/rules/slide-profiles/<profile>.yml` — `paper-review`, `lecture`, or
> `invited-talk` — which sets the bullet budget and turns on genre-specific
> checks. A deck picks its profile in `<deck>.deck.yml`, and a deck without
> one inherits its genre's default.
>
> The three principles here do not vary by genre. The budgets do, because the
> budgets follow from who is in the room and how long you have. A lecture for
> first-years gets four bullets, not five, and owes every acronym an
> expansion; a paper review owes neither. Run
> `python3 scripts/deckprofile.py <deck>` to see what a deck is actually held
> to, and `python3 scripts/test_profiles.py` to confirm the profiles still
> grade differently from each other. Punctuation and character-based wrap estimates are editorial feedback. Inspect the rendered frame for actual clipping.

---

## 1. Extreme Minimalism — one idea per slide

**Never pack much content onto one slide.** When content does not fit, split
the slide — do not compress.

Use the deck profile's limits for bullet count, nesting and callouts. Prefer short lines and give a figure room to teach. The length of a source line cannot tell how it wraps in the delivery font, especially beside a diagram or in the DGIST caption room. Check the final fragments in the rendered audience view. Split a slide when its ideas compete for space.

A ~30 min talk may run 40–60 slides. Splitting is always preferred over
cutting, and cutting is always preferred over cramming.

## 2. Big Type — never shrink text to fit

The root font is 40px. That is the point: it caps how much fits.

- **NEVER** use `.smaller` / `.smallest` in new slides. They exist only so
  legacy decks keep rendering. The quality gate penalizes each use (-5).
- **NEVER** use inline `font-size` overrides below 1em to make content fit.
- If text overflows: split the slide → cut content → restructure
  (columns/tabsets) — in that order. Font reduction is not on the list.

## 3. Filled Frame — center the main content

The title stays pinned at the top; everything under it centers vertically in
the remaining space. Horizontal centering is element-wise:

| Element | Default |
|---------|---------|
| Figures, tables, display math, videos | fully centered |
| Standalone paragraphs, h3/h4 | fully centered (text too) |
| Bullet lists | block centered, text left-aligned |
| Colored boxes | box hugs content and centers, text left-aligned |

The theme does all of this automatically. Escape hatches:

- `## Title {.top-align}` — anchor content under the title (full-bleed
  figures, stepper widgets).
- `::: {.left}` — force left alignment inside the div.
- `[Big claim.]{.statement}` — oversized centered declaration.

## Required YAML for new decks

Decks live at `Quarto/<genre>/<name>.qmd`, so the shared theme is one level
up. `/new-deck` writes this for you.

```yaml
# Full-bleed title gradient as a reveal background.
title-slide-attributes:
  data-background-gradient: "linear-gradient(180deg, #ffffff 0%, #E8EDF5 100%)"
format:
  revealjs:
    theme: [default, ../clean-academic.scss]
bibliography: ../../Bibliography_base.bib
```

That is the whole of it. The 1280x720 canvas, `margin: 0`, `center: false`,
`auto-stretch: false`, slide numbers, the pinned KaTeX, the slide-types
filter, the video and series shortcodes and the Pretendard link are project
defaults in `Quarto/_quarto.yml`; a deck must not repeat them. Fixtures under
`Quarto/_fixtures/` are the exception - Quarto treats an underscore directory
as outside the project, so each fixture qmd carries what it needs.

## Review priority (split-first, replaces spacing-first)

When a slide has too much content, fix in this order:

1. **Split into two slides** (default answer)
2. Cut content (move detail to speaker notes)
3. Two columns (only when the pairing is genuinely side-by-side)
4. Reduce image width
5. ~~Font size reduction~~ — never
