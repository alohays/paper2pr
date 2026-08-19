---
paths:
  - "Quarto/**/*.qmd"
  - "docs/**"
---

# Task Completion Verification Protocol

**At the end of EVERY task, Claude MUST verify the output works correctly.** This is non-negotiable.

## For Quarto/HTML Slides:
1. Run `bash scripts/sync_to_docs.sh` (or `bash scripts/sync_to_docs.sh DeckName`) to render and assemble
2. Run `python3 scripts/check_site_assets.py docs` (sync_to_docs.sh already runs it; re-run it if you touched docs/ afterwards)
3. Run `python3 scripts/quality_score.py Quarto/<genre>/DeckName.qmd` and report the score
4. Open the HTML in browser: `open docs/slides/<genre>/DeckName.html` (macOS) or `xdg-open` (Linux).
   `python3 scripts/deckpath.py DeckName --field genre` if you are unsure which genre it landed in.
5. Verify images display by reading 2-3 image files to confirm valid content
6. Check HTML source for correct image paths
7. Check for overflow by scanning dense slides
8. Report verification results

## For Scripts and Hooks:
1. Run the repo tests: `python3 scripts/test_profiles.py`, `python3 scripts/test_minyaml.py`,
   `bash scripts/test_note_filter.sh`, `bash scripts/test_korean_gate.sh`
2. All four must pass before the task is reported done

## Common Pitfalls:
- **PDF images in HTML**: Browsers don't render PDFs inline -> export figures as SVG (or PNG for photos)
- **Relative paths**: a deck at `Quarto/<genre>/` reaches figures as `../../Figures/<genre>/<deck>/`, and that same prefix has to resolve from `docs/slides/<genre>/` after assembly -> use `sync_to_docs.sh`, which runs `check_site_assets.py` over the result. A missing asset renders fine and 404s in the browser
- **Assuming success**: Always verify output files exist AND contain correct content

## Verification Checklist:
```
[ ] Output file created successfully
[ ] No render errors
[ ] Images/figures display correctly
[ ] Paths resolve in deployment location (docs/)
[ ] Opened in browser/viewer to confirm visual appearance
[ ] Reported results to user
```
