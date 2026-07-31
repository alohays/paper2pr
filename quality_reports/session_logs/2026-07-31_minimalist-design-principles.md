# Session Log: Minimalist Design Principles + Quarto-First Pivot

**Date:** 2026-07-31
**Plan:** `quality_reports/plans/2026-07-31_minimalist-design-principles.md`

## Goal

Embed three design principles into paper2pr infrastructure: (1) extreme
minimalism — one idea per slide; (2) bigger type than feels natural — never
shrink to fit; (3) title pinned at top with content centered vertically and
horizontally so the frame feels full.

## Key Decisions (from 11 AskUserQuestion answers)

- Full-infrastructure scope: theme + rules/agents/skills + quality gate + docs
- **Quarto becomes the source of truth going forward** (presentations are
  delivered from Quarto); Beamer demoted to optional export, files kept
- Title fixed at top, content centered below (not revealjs center:true)
- Element-wise horizontal centering (figures/tables/math/statements fully
  centered; lists and boxes block-centered with left text)
- Root font 30px → 40px; `.smaller`/`.smallest` kept but forbidden in new
  decks (-5 each in the gate); density budget: ≤5 bullets (≤3 with figure),
  ≤1 box, ≤1 sub-level nesting; 40–60 slides allowed per ~30 min talk
- Existing decks pinned to `clean-academic-legacy.scss` (no retrofit)
- Incremental commits, no push

## What Changed

1. `Quarto/clean-academic-legacy.scss` — snapshot; DreamZero/DreamDojo/
   RoboTTT repointed (commit ad476a3)
2. `Quarto/clean-academic.scss` — rebuilt: 40px root, flex layout with
   auto-margin vertical centering under a pinned h2, element-wise horizontal
   centering, `.statement`/`.left`/`.top-align` utilities, r-stretch
   neutralized, image caps that tighten when lists share the slide
   (commit 53709e4). `Quarto/design-test.qmd` added as a rendering fixture.
3. Rules/agents/skills — new `slide-design-principles.md`; Quarto-first
   rewrites of `single-source-of-truth.md` and `beamer-quarto-sync.md`
   (with legacy deck inventory); split-first priority in slide-auditor and
   /visual-audit; /translate-to-quarto retagged legacy import; /qa-quarto
   scoped to imports; /create-lecture authors in Quarto (commit 9ea34aa)
4. `scripts/quality_score.py` — density + font-shrink checks, legacy-theme
   exemption (commit d4d85eb)
5. `AGENTS.md` — principles section, Quarto-first commands, updated deck
   table with themes (+ RoboTTT row, previously missing)

## Verification Evidence

- DreamZero renders unchanged on the legacy theme
- design-test.qmd verified in-browser at 1280×720: bullets/statement/box/
  figure/figure+bullets/columns/table/math/top-align/untitled/footnote/
  section/title slides all center correctly, no overflow
- Violations fixture scored 85/100 with all five new deductions firing on
  the correct slides; DreamDojo (legacy, 6× .smaller) and design-test.qmd
  both score 100/100
- Found during testing: Quarto auto-stretch conflicts with the centered
  flex layout (r-stretch height resolves to 0) → neutralized in the theme
  and `auto-stretch: false` made part of the required YAML

## Open Questions / Follow-ups

- First real deck on the new theme will be the true stress test; the
  design-test fixture covers layout patterns, not real content pressure
- `pages/` landing page and CI deploy untouched (no theme references there)
