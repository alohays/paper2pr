# SUNY Speaker Script Compression Plan

Date: 2026-04-04
Target: reduce the SUNY speaker script from roughly 9,275 words to about 7,400 words for a 70-minute talk.

## Constraints

- Keep the slide order and core claims unchanged.
- Preserve the confident mentor tone.
- Remove repetition, excess framing, and over-explanation before cutting core evidence.
- Treat `.speaker-notes/SUNY.json` as the editable tracked source for note content.
- After integration, sync the compressed note content back into the local `Quarto/SUNY.qmd` working copy for presenter use.

## Parallel Work Split

1. Slides 1-16: current 2,510 words, target about 2,008.
2. Slides 17-32: current 2,730 words, target about 2,184.
3. Slides 33-48: current 2,371 words, target about 1,897.
4. Slides 49-62: current 1,664 words, target about 1,331.

## Execution

1. Spawn four Codex agents with ClawTeam, one per slide range, each editing only its assigned note range in `.speaker-notes/SUNY.json`.
2. Spawn one Codex review agent to audit global pacing, consistency, and over-compression risk after the chunk edits land.
3. Integrate the chunk commits into the main worktree.
4. Recompute total and per-section word counts.
5. Sync updated notes into the local `Quarto/SUNY.qmd`.
6. Render `Quarto/SUNY.qmd` and inspect the resulting timing numbers.

## Review Gates

- Most slides should land within roughly 75-85% of current length.
- Demo/transition slides can stay shorter if that improves pacing.
- High-density slides should be simplified, not just shortened.
- Final script should still sound spoken, not outline-like.
