---
paths:
  - "Quarto/**/*.qmd"
---

# Quality Gates & Scoring Rubrics

## Thresholds

- **80/100 = Commit** -- good enough to save
- **90/100 = PR** -- ready for deployment
- **95/100 = Excellence** -- aspirational

## Quarto Slides (.qmd)

Design-principle deductions apply to decks on the main theme
(`clean-academic.scss`). Legacy decks pinned to `clean-academic-legacy.scss`
are graded without them. See `.claude/rules/slide-design-principles.md`.

The bullet and density numbers below are the **paper-review defaults**. The
numbers a given deck is actually held to come from its profile in
`.claude/rules/slide-profiles/<profile>.yml` (`paper-review`, `lecture`,
`invited-talk`), selected by `<deck>.deck.yml` and read via
`python3 scripts/deckprofile.py <deck>`. `quality_score.py` applies the
profile's budgets, not this table, when they differ.

| Severity | Issue | Deduction |
|----------|-------|-----------|
| Critical | Render failure (`quarto render`) | -100 |
| Critical | Equation overflow | -20 |
| Critical | Broken citation | -15 |
| Critical | Typo in equation | -10 |
| Major | Text overflow | -5 |
| Major | `.smaller`/`.smallest` or font-size override used to fit content | -5 per slide |
| Major | >5 bullets on a slide (>3 with a figure; one less again if a bullet wraps to two lines) | -3 per slide |
| Major | >1 two-line bullet on a slide, or any bullet running past two lines | -3 per slide |
| Major | >1 colored box on a slide | -3 per slide |
| Major | Notation inconsistency | -3 |
| Minor | List nesting deeper than 1 sub-level | -1 per slide |
| Minor | Long lines (>100 chars) | -1 (EXCEPT documented math formulas) |

## Enforcement

- **Score < 80:** Block commit. List blocking issues.
- **Score < 90:** Allow commit, warn. List recommendations.
- User can override with justification.

## Quality Reports

Generated **only at merge time**. Reports are free-form markdown saved under
`quality_reports/merges/YYYY-MM-DD_[branch-name].md` (score, blocking issues,
recommendations, what was verified).
