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
> grade differently from each other.

---

## 1. Extreme Minimalism — one idea per slide

**Never pack much content onto one slide.** When content does not fit, split
the slide — do not compress.

Density budget (enforced by the quality gate):

| Limit | Value |
|-------|-------|
| Core message per slide | 1 |
| Bullets per slide | ≤ 5, all on one line |
| Bullets when a figure shares the slide | ≤ 3 |
| Two-line bullets | ≤ 1 per slide, **and it costs a slot** (cap drops by 1) |
| Three-line bullets | never |
| Colored boxes per slide | ≤ 1 |
| List nesting | ≤ 1 sub-level |

**Write one-line bullets.** A bullet that wraps is a bullet that is doing too
much — cut it or split the slide. One wrapped bullet per slide is tolerated,
not encouraged, and it takes the place of another bullet: five one-liners is
fine, four bullets with one wrapped is fine, five with one wrapped is not.
With a figure the same arithmetic applies from a base of 3.

At 1280×720 on the 40px root font, a bullet fits on one line up to about
**70 characters** of rendered text (markup like `[x]{.hi}` and links do not
count). 71–137 characters wrap to two lines; past that it is three, which the
frame cannot absorb.

> This replaces the original "≤5 bullets, each ≤2 lines". That budget did not
> fit: five two-line bullets overflow the 720px canvas by 38px and the surplus
> is silently clipped by `overflow: hidden`, while the gate scored the slide
> 100/100. Measured, not estimated.

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
