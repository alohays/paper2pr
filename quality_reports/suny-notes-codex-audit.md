# SUNY Speaker Notes Factual Audit (Codex)

Date: 2026-04-04
Auditor: `content-auditor`

## Inputs Reviewed

- `Quarto/SUNY.qmd` for the current 62-slide deck.
- Recovered 62-note dump from local Codex session artifact:
  `/Users/iyunseong/.codex/sessions/2026/04/02/rollout-2026-04-02T18-00-18-019d4d6c-06af-7632-844d-aad03c0c1213.jsonl`
- Cross-check reference:
  `quality_reports/suny_notes_review/02_data_accuracy.md`

## Note On Source Recovery

The working-tree `Quarto/SUNY.qmd` in this ClawTeam worktree does not currently contain literal `::: {.notes}` blocks because the repo clean filter strips speaker notes from tracked QMD content. To complete the audit without modifying `SUNY.qmd`, I used the April 2 Codex session artifact that printed all 62 note blocks directly from a note-bearing copy of `Quarto/SUNY.qmd`.

## Method

- Compared every recovered note against the current visible slide content in `Quarto/SUNY.qmd`.
- Focused on numbers, statistics, timelines, named entities, and explicit callbacks to other slides.
- Did not flag normal presenter elaboration unless it contradicted, overstated, or was no longer supported by the current slide.

## Summary

- Notes audited: 62 / 62
- Slides with no material factual mismatch found: 58
- Slides flagged: 4
- Total issues flagged: 6
- Severity mix: 1 high, 3 medium, 2 low

## Coverage Check

- Slides 1-10: only Slide 2 flagged
- Slides 11-32: no material mismatch found
- Slide 33: flagged
- Slides 34-53: no material mismatch found
- Slide 54: flagged
- Slides 55-59: no material mismatch found
- Slide 60: flagged
- Slides 61-62: no material mismatch found

## Findings

| Severity | Slide | Finding | Evidence |
| --- | --- | --- | --- |
| High | 33 | The note says the GINT pipeline starts in `early 2023`, reaches pilot in `early 2024`, and becomes commercial in `2024-2025`. The current slide shows `Lab 2024 Q3`, `Demo 2025 Q1-Q2`, `Pilot 2025 Q2-Q3`, and `Commercial 2025 Q4`. This is a direct on-screen timeline contradiction. | `Quarto/SUNY.qmd:3766`, `Quarto/SUNY.qmd:3793` |
| Medium | 33 | The note frames the slide as the GINT journey, but the current Lab-stage caption is `SketchDrive core research begins.` The slide itself mixes projects, so the note and slide are no longer aligned on what the first stage represents. | `Quarto/SUNY.qmd:3767` |
| Medium | 54 | The note says `41 percent of code at Google is now AI-generated`, but the actual slide carrying this stat says only `41% of all code is now AI-generated or AI-assisted`. The Google-specific attribution is not supported by the deck. | `Quarto/SUNY.qmd:4810` |
| Medium | 60 | The note tells the audience the QR code goes to a curated resource page with tools, guides, and communities. The current slide now shows a `LinkedIn` QR code and separate contact rows for LinkedIn, GitHub, and personal website. The spoken instruction is stale after the Slide 60 update. | `Quarto/SUNY.qmd:6874`, `Quarto/SUNY.qmd:6910` |
| Low | 2 | The note says `over 1,800 citations`, while the current slide chip says `1,850+ citations`. This is a minor rounding / undercount drift. | `Quarto/SUNY.qmd:303` |
| Low | 2 | The note still says the speaker `bounced between seven companies`, but the current slide redesign no longer visibly supports that count and instead emphasizes `10+ top-tier papers`, `1,850+ citations`, and `double-digit h-index`. Treat this as stale speaker-detail drift after the slide redesign. | `Quarto/SUNY.qmd:301`, `Quarto/SUNY.qmd:304` |

## Recommended Fix Order

1. Fix Slide 33 first. It contains the only hard timeline contradiction and is the most likely to visibly clash with the on-screen slide during delivery.
2. Update Slide 60 next. Audience behavior will diverge immediately if they scan the QR expecting a resource hub and land on LinkedIn instead.
3. Normalize the 41 percent attribution in Slide 54 so it matches the way Slide 42 presents the stat.
4. Clean up Slide 2's stale note details so the opening bio matches the redesigned slide.

## Residual Risk

- This audit used a recovered April 2 note dump because the current worktree has stripped notes. I did not restore notes into `Quarto/SUNY.qmd`.
- Slide 2 now embeds some speaker bio detail inside `speaker-profile-cards.png`, so the exact support level for every biography sub-detail depends partly on that image rather than plain QMD text. I only flagged the details that are clearly stale or no longer directly supported by the visible slide structure.
