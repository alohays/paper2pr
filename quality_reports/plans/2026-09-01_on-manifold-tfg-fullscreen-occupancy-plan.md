# On-Manifold TFG Full-Screen Occupancy Plan

## Goal

Reduce excessive empty space in the 16-slide ECCV deck while keeping every
content element inside the 1280 x 720 Reveal canvas at full-screen aspect
ratios.

## Approach

1. Measure the fully revealed content bounds of every slide in normalized
   Reveal coordinates.
2. Preserve the 1920 x 1080 reference layout and apply conservative,
   slide-specific scaling to each centered content block.
3. Give sparse title, transition, takeaway, and closing slides more scale;
   keep dense result slides below their measured safe limit.
4. Re-render, capture every final fragment state, and reject any slide with
   clipping, overflow, overlap, or unintended text reflow.
5. Copy only the validated, note-free static bundle to the project-page
   worktree for a local Chrome preview before any deployment decision.

## Acceptance Criteria

- All 16 slides use visibly more of the canvas than the deployed baseline.
- No visible content crosses a 24 px canvas safety margin.
- No slide has horizontal or vertical overflow.
- Slide content, ordering, fragments, formulas, links, and notes remain
  unchanged.
- The public bundle contains zero speaker-note elements.
