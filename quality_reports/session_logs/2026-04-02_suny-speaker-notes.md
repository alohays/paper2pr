# Session Log: SUNY Speaker Notes Generation + ClawTeam Review

**Date:** 2026-04-02
**Goal:** Generate English speaker notes (verbatim reading script) for all 62 slides of the SUNY Career Talk, then review and polish via ClawTeam multi-agent pipeline.

---

## Key Context

- **File:** `Quarto/SUNY.qmd` — "Career Roadmap for AI Researchers: From Papers to Products"
- **Event:** STEM Career Sprint 2026, SUNY Korea, April 4, 2026
- **Duration:** 90 min (70 min lecture + 20 min integrated Q&A)
- **Language:** English
- **Speaker:** Yunsung Lee, Head of Research, WoRV @ Maum.ai

---

## Phase 1: Generation

- Used `/write-speaker-notes 2604-SUNY --en` skill
- 6 batches via `script-writer` subagents (sequential for transition coherence)
- Batches 1-2: Claude subagents (returned text, not inserted)
- Batch 3: Claude subagent (inserted directly into QMD for slides 21-30)
- Batches 4-6: launched in parallel (2 Claude + 1 Codex), returned text only
- Python insertion script (`/tmp/suny_notes_insert.py`) handled bulk insertion for 52 remaining slides
- Initial word count: 8,934 words — within target range (8,000-9,000)
- Quarto render: success, 62 `<aside class="notes">` verified in HTML

## Phase 2: ClawTeam Multi-Agent Review

- Team: `suny-review` with 4 parallel agents
- **spoken-quality** (Claude Opus): Found slides 51-62 had 0% contractions (stalled before writing report, but finding captured from tmux)
- **data-accuracy** (Claude Opus): 4 discrepancies found — 1 HIGH (slide 33 GINT timeline), 2 MEDIUM (slide 54 Google attribution, slide 33 project name), 1 LOW (slide 2 citation count)
- **flow-transitions** (Codex gpt-5.4): 53 SMOOTH / 8 ADEQUATE transitions, energy arc mapped, top 5 flow improvements identified
- **audience-impact** (Codex gpt-5.4): Overall 82/100, top 10 high-impact notes, top 10 needing improvement, 5 rewrite suggestions

## Phase 3: Polish

25 edits applied:
- 3 factual corrections (slide 33 timeline, slide 54 attribution, slide 2 citations)
- 12 slides converted from formal to spoken English (contractions for slides 51-62)
- 5 weak notes rewritten with stronger hooks (slides 3, 11, 25, 47, 50)
- 5 transition bridges added at ADEQUATE-rated boundaries (slides 5, 6, 9, 49, 51)

## Final Metrics

| Metric | Value |
|--------|-------|
| Words | 8,819 |
| Target | 8,000-9,000 |
| Speaking time | ~68 min |
| Q&A buffer | ~22 min |
| Coverage | 62/62 (100%) |
| Render | Success |

## Decisions Made

- **90-min scaling:** Default skill targets 30-min talks. Scaled word budget proportionally to ~8,500 midpoint based on 65 min estimated speaking time.
- **Batch 3 direct insertion:** script-writer agent edited the QMD directly despite instructions. Accepted the edits and adjusted line numbers for subsequent batches.
- **Codex vs Claude for review:** Used Codex (gpt-5.4) for flow-transitions and audience-impact reviews for fresh perspective. Both produced high-quality reports.
- **Spoken-quality agent stall:** Agent found the critical contraction issue but stalled before writing its report. Captured finding from tmux output and applied fix manually.

## Open Items

- [ ] Manual speaker view check (press S in browser)
- [ ] Presenter rehearsal to verify pacing feels natural
- [ ] Backup notes before git operations: `python3 scripts/backup_notes.py backup SUNY`
