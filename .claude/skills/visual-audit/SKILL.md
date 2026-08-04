---
name: visual-audit
description: Perform adversarial visual audit of Quarto or Beamer slides checking for density violations, overflow, font consistency, box fatigue, and centering issues.
argument-hint: "[QMD or TEX filename]"
allowed-tools: ["Read", "Grep", "Glob", "Write", "Task"]
---

# Visual Audit of Slide Deck

Perform a thorough visual layout audit of a slide deck.

## Steps

1. **Read the slide file** specified in `$ARGUMENTS`

2. **Determine the ruleset:**
   - Main theme (`clean-academic.scss`) → full design-principles audit
     (`.claude/rules/slide-design-principles.md`)
   - Legacy theme (`clean-academic-legacy.scss`) or SUNY's own theme →
     legacy audit only (overflow, parity, spacing); skip density limits

3. **For Quarto (.qmd) files:**
   - Render with `quarto render "$(python3 scripts/deckpath.py $ARGUMENTS --field qmd)"`
   - Open in browser to inspect each slide

4. **For Beamer (.tex) files:**
   - Compile and check for overfull hbox warnings

5. **Audit every slide for:**

   **DENSITY (new decks):** >1 core message, >5 bullets (>3 with a figure;
   one less again if any bullet wraps to two lines), >1 wrapped bullet,
   any three-line bullet,
   >1 colored box, nesting >1 sub-level
   **OVERFLOW:** Content exceeding slide boundaries
   **FONT CONSISTENCY:** Any `.smaller`/`.smallest` in a new deck (forbidden),
   inline font-size overrides below 1em
   **CENTERING (new decks):** ad-hoc positioning fighting the theme,
   unjustified `{.top-align}` or `{.left}`, missing `auto-stretch: false`
   **BOX FATIGUE:** 2+ colored boxes on one slide, wrong box types
   **LAYOUT:** Missing transitions, missing framing sentences, semantic colors

6. **Produce a report** organized by slide with severity and recommendations

7. **Follow the split-first principle:**
   1. Split into two slides (the default answer)
   2. Cut content (move to speaker notes)
   3. Two columns (only for genuinely side-by-side pairings)
   4. Reduce image/SVG size
   5. Font size reduction — never recommend it
