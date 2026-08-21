---
paths:
  - "Figures/**/*"
  - "Quarto/**/*.qmd"
  - "Quarto/**/*.deck.yml"
---

# Single Source of Truth: Enforcement Protocol

**The Quarto `.qmd` file is the only source for slide content.**
Presentations are delivered from Quarto; everything else is derived.

## The SSOT Chain

```
Quarto/<genre>/<deck>.qmd (SOURCE OF TRUTH)
  ├── Quarto/<genre>/<deck>.deck.yml   per-deck config (profile, audience, language)
  ├── Quarto/_quarto.yml               project defaults (canvas, katex, filters, fonts)
  ├── Quarto/clean-academic.scss       theme for new decks
  ├── Quarto/clean-academic-legacy.scss theme for pinned legacy decks
  ├── Bibliography_base.bib            shared bibliography
  ├── Figures/<genre>/<deck>/          SVG/PNG figures (data source for images)
  ├── Figures/<genre>/<deck>/videos.yml    clip manifest, hand-written
  │     -> videos.json + videos/<slug>.mp4, <slug>-poster.jpg (derived by
  │        scripts/media_prep.py; the media go to the GitHub Release
  │        media-<deck> via scripts/media_release.sh, never into git)
  ├── Quarto/lectures/_series/<course>.yml course manifest, hand-written
  │     -> Figures/lectures/_series/<course>/series.json, semester-map*.svg,
  │        qr-qa.png|svg (derived by scripts/series_assets.py)
  └── rendered HTML -> docs/ -> GitHub Pages (derived, via sync_to_docs.sh / CI)

NEVER edit derived artifacts independently.
ALWAYS propagate changes from source -> derived.
```

## Rules

1. **Author in Quarto.** New decks start as `.qmd` files under
   `Quarto/<genre>/` following `.claude/rules/slide-design-principles.md`;
   `/new-deck` scaffolds the `.qmd` and its `.deck.yml` together.
2. **Per-deck config lives in `<deck>.deck.yml`.** Project-wide defaults live
   in `Quarto/_quarto.yml`; a deck's front matter overrides them. Do not
   duplicate defaults into individual decks.
3. **One theme per deck.** New decks use `clean-academic.scss`. Legacy decks
   pinned to `clean-academic-legacy.scss` stay pinned; do not retrofit them.
4. **Figures are SVG or PNG** under `Figures/<genre>/<deck>/`, referenced from
   the deck by relative path. Edit the figure's own source (notebook, script,
   drawing tool) and re-export; never hand-edit a rendered copy in `docs/`.
   The same directory also holds `figures.yml` (attribution manifest),
   `videos.yml` (clip manifest) and `videos.json` (the lock), all committed,
   plus `videos/` - the trimmed mp4s and JPG posters, gitignored and served
   from the deck's GitHub Release.
5. **Never edit rendered HTML** (`Quarto/**/*.html`, `docs/**`) - it is a
   build artifact.
