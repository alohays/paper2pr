---
paths:
  - "Slides/**/*.tex"
  - "Quarto/**/*.qmd"
---

# Quarto ↔ Beamer Sync Rule

**Quarto `.qmd` is the source of truth. Beamer `.tex` is an optional export.**
(Direction reversed 2026-07; presentations are delivered from Quarto.)

## The Rule

- Editing a Quarto `.qmd`: no Beamer sync is required. Only propagate
  Quarto → Beamer when the user is actively maintaining a PDF export of that
  deck and asks for it (or has asked for it as a standing request).
- Editing a Beamer `.tex` (rare, legacy maintenance): you MUST apply the
  equivalent change to the Quarto `.qmd` in the same task — the Quarto copy
  is what gets presented and deployed, and it must never lag.

## Deck Inventory

| Paper | Quarto (source) | Beamer (status) |
|-------|-----------------|-----------------|
| DreamZero | `Quarto/DreamZero.qmd` | `Slides/DreamZero.tex` (legacy, frozen) |
| DreamDojo | `Quarto/DreamDojo.qmd` | `Slides/DreamDojo.tex` (legacy, frozen) |
| RoboTTT | `Quarto/RoboTTT.qmd` | none |
| SUNY Career Sprint | `Quarto/SUNY.qmd` | none (career talk) |
<!-- Add rows as you create new decks. New decks default to "none". -->

## Quarto → LaTeX Translation Reference (for exports)

| Quarto | Beamer Equivalent |
| ------ | ----------------- |
| `[text]{style="color: #525252;"}` | `\muted{text}` |
| `[**text**]{.primarygold}` | `\key{text}` |
| `[text]{.positive}` | `\textcolor{positive}{text}` |
| `[text]{.negative}` | `\textcolor{negative}{text}` |
| `- text` | `\item text` |
| `::: {.highlightbox}` | `\begin{highlightbox}` |
| `::: {.methodbox}` | `\begin{methodbox}` |
| `$formula$` | `$formula$` (same) |

## When NOT to Sync

- The deck has no Beamer twin (the default for new decks)
- The Beamer twin is marked legacy/frozen in the inventory above
- Change is Quarto-only infrastructure (theme SCSS, YAML, widgets)

## Enforcement

Before marking a Beamer editing task complete, check:
> "Did I also update the Quarto file?"

If the answer is no and a Quarto file exists, **you are NOT done.**
