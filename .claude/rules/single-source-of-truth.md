---
paths:
  - "Figures/**/*"
  - "Quarto/**/*.qmd"
  - "Slides/**/*.tex"
---

# Single Source of Truth: Enforcement Protocol

**The Quarto `.qmd` file is the authoritative source for ALL content.**
Presentations are delivered from Quarto; everything else is derived.

> Historical note: before 2026-07 the Beamer `.tex` was authoritative and
> Quarto was the derived copy. That direction is now reversed. Beamer is an
> optional export produced only when a PDF deck is explicitly needed.

## The SSOT Chain

```
Quarto .qmd (SOURCE OF TRUTH)
  ├── rendered HTML → GitHub Pages (derived, via CI/CD)
  ├── Beamer .tex (OPTIONAL derived export — only on request)
  ├── Bibliography_base.bib (shared)
  └── Figures/PaperName/*.rds → plotly charts (data source)

NEVER edit derived artifacts independently.
ALWAYS propagate changes from source → derived.
```

## Rules

1. **Author in Quarto.** New decks start as `.qmd` files following
   `.claude/rules/slide-design-principles.md`.
2. **Beamer only on request.** Do not create or update a `.tex` twin unless
   the user asks for a PDF export. When one exists and the user is
   maintaining it, propagate Quarto → Beamer (see `beamer-quarto-sync.md`).
3. **Never edit rendered HTML** — it is a build artifact.

## TikZ Diagrams

TikZ diagrams (compiled via `Figures/PaperName/extract_tikz.tex` → PDF → SVG)
remain a legitimate way to produce vector figures for Quarto slides. The
`extract_tikz.tex` file is the source for those diagrams:

1. Edit the TikZ code in `extract_tikz.tex`
2. Recompile and regenerate SVGs (`/extract-tikz`)
3. Reference the SVG in the QMD

If a legacy Beamer deck also embeds the same TikZ code, treat
`extract_tikz.tex` as the diagram source and update the Beamer copy only if
that deck is still being maintained.

## Content Fidelity Checklist (when a Beamer export exists)

```
[ ] Slide count: Quarto slides == Beamer frames
[ ] Math check: every equation appears with identical notation
[ ] Citation check: every @key in Quarto has a \cite in Beamer
[ ] Environment check: every Quarto box class has a Beamer environment
[ ] No drift: neither file has content the other lacks
```
