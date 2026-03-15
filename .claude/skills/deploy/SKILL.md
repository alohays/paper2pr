---
name: deploy
description: Render Quarto slides and sync to docs/ for GitHub Pages deployment. Use when deploying lecture slides after making changes.
argument-hint: "[PaperName or 'all']"
allowed-tools: ["Read", "Bash"]
---

# Deploy Slides to GitHub Pages

Render Quarto slides and sync all files to `docs/` for GitHub Pages deployment.

## Steps

1. **Run the sync script:**
   - If `$ARGUMENTS` is provided (e.g., "DreamZero"): `./scripts/sync_to_docs.sh $ARGUMENTS`
   - If no argument: `./scripts/sync_to_docs.sh` (syncs all lectures)

2. **Verify deployment:**
   - Check that HTML files exist in `docs/slides/`
   - Check that `_files/` directories were copied (RevealJS assets)
   - Check that `docs/Figures/` was synced from `Figures/`

3. **Verify interactive charts** (if applicable):
   - Grep rendered HTML for interactive widget count
   - Confirm count matches expected

4. **Verify TikZ SVGs** (if applicable):
   - Check that all referenced SVG files exist in `docs/Figures/PaperName/`

5. **Open in browser** for visual verification:
   - `open docs/slides/PaperName.html`          # macOS
   - `# xdg-open docs/slides/PaperName.html`    # Linux
   - Confirm slides render, images display, navigation works

6. **Report results** to the user

## What the sync script does:
- Renders all `.qmd` files in `Quarto/` (skips `*_backup*` files)
- Copies HTML and `_files/` directories to `docs/slides/`
- **Strips speaker notes** from deployed HTML (`scripts/strip_speaker_notes.py`)
- Copies Beamer PDFs from `Slides/` to `docs/slides/`
- Syncs `Figures/` to `docs/Figures/` using rsync

## Speaker Notes Policy
- QMD source always contains `::: {.notes}` blocks (single source of truth)
- **Local** (`Quarto/*.html`): notes included — press `S` for speaker view
- **Public** (`docs/slides/*.html`): notes stripped at deploy time
- No separate branches needed — `strip_speaker_notes.py` handles this automatically
