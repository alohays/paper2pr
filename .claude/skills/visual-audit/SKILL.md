---
name: visual-audit
description: Perform adversarial visual audit of Quarto RevealJS slides checking for density violations, overflow, font consistency, box fatigue, and centering issues, on full-deck screenshots from scripts/shoot_slides.py.
argument-hint: "[DeckName]"
allowed-tools: ["Read", "Grep", "Glob", "Write", "Bash", "Task"]
---

# Visual Audit of Slide Deck

Perform a thorough visual layout audit of a slide deck, on the source and on
the rendered pixels.

## Steps

1. **Resolve the deck** named in `$ARGUMENTS` and load its premises:

   ```bash
   python3 scripts/deckpath.py $ARGUMENTS --field qmd            # the source
   python3 scripts/deckprofile.py $ARGUMENTS                     # resolved profile JSON
   cat "$(python3 scripts/deckpath.py $ARGUMENTS --field config)"  # <deck>.deck.yml
   ```

   The density numbers below come from the profile JSON (`bullets_max`,
   `bullets_max_with_figure`, `bullets_max_two_line`, `box_density`,
   `max_nesting`); quote the deck's own budget in every density finding.

2. **Determine the ruleset:**
   - Main theme (`clean-academic.scss`) -> full design-principles audit
     (`.claude/rules/slide-design-principles.md`)
   - Legacy theme (`clean-academic-legacy.scss`) or SUNY's own theme ->
     legacy audit only (overflow, spacing); skip density limits

3. **Screenshot every slide:**

   ```bash
   python3 scripts/shoot_slides.py $ARGUMENTS --out /tmp/$ARGUMENTS-shots
   ```

   This renders the html first when it is missing or older than the qmd,
   then writes one 1280x720 PNG per slide in reading order (vertical stacks
   included). Read every PNG - the pixels catch what the source hides:
   real overflow, wrapped bullets, a figure that failed to load, a video
   slide stuck on a black frame. (`bash scripts/preview.sh <name>` still
   opens the deck in a browser when you need to interact with a slide.)

4. **Audit every slide for:**

   **DENSITY (new decks, budgets from the profile JSON):** >1 core message,
   more bullets than `bullets_max` (`bullets_max_with_figure` with a figure;
   one less again if any bullet wraps to two lines), more wrapped bullets
   than `bullets_max_two_line`, any three-line bullet, more colored boxes
   than `box_density`, nesting deeper than `max_nesting`
   **OVERFLOW:** Content exceeding slide boundaries - confirm on the PNGs
   **FONT CONSISTENCY:** Any `.smaller`/`.smallest` in a new deck (forbidden),
   inline font-size overrides below 1em
   **CENTERING (new decks):** ad-hoc positioning fighting the theme,
   unjustified `{.top-align}` or `{.left}`, missing `auto-stretch: false`
   **BOX FATIGUE:** more boxes on one slide than the budget, wrong box types
   **LAYOUT:** Missing transitions, missing framing sentences, semantic colors

5. **Produce a report** organized by slide with severity and
   recommendations, its header stating the profile, the audience (from
   `deck.yml`, else the profile), and the budget applied

6. **Follow the split-first principle:**
   1. Split into two slides (the default answer)
   2. Cut content (move to speaker notes)
   3. Two columns (only for genuinely side-by-side pairings)
   4. Reduce image/SVG size
   5. Font size reduction - never recommend it
