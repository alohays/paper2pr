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

---

## 1. Extreme Minimalism — one idea per slide

**Never pack much content onto one slide.** When content does not fit, split
the slide — do not compress.

Density budget (enforced by the quality gate):

| Limit | Value |
|-------|-------|
| Core message per slide | 1 |
| Bullets per slide | ≤ 5 (each ≤ 2 lines) |
| Bullets when a figure shares the slide | ≤ 3 |
| Colored boxes per slide | ≤ 1 |
| List nesting | ≤ 1 sub-level |

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

```yaml
format:
  revealjs:
    theme: [default, clean-academic.scss]
    width: 1280
    height: 720
    center: false          # theme handles centering; keep titles pinned
    auto-stretch: false    # r-stretch fights the centered flex layout
    html-math-method:
      method: katex
```

## Review priority (split-first, replaces spacing-first)

When a slide has too much content, fix in this order:

1. **Split into two slides** (default answer)
2. Cut content (move detail to speaker notes)
3. Two columns (only when the pairing is genuinely side-by-side)
4. Reduce image width
5. ~~Font size reduction~~ — never
