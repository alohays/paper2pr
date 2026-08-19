---
name: write-speaker-notes
description: Generate speaker notes (presentation script) for Quarto RevealJS slides. Supports English and Korean. Use when user asks to "write speaker notes", "add presentation script", "speaker script", "발표 스크립트", or "스피커 노트".
argument-hint: "[DeckName] [--lang en|ko to override the deck's config]"
allowed-tools: ["Read", "Write", "Edit", "Bash", "Grep", "Glob", "Agent"]
---

# Speaker Notes (Presentation Script) Workflow

Generate a verbatim reading script for Quarto RevealJS slides. The presenter should be able to read these notes as-is during the talk.

**CRITICAL: These are presentation scripts (대본), NOT talking points.** Full spoken sentences that flow naturally when read aloud.

---

## Phase 0: Pre-Flight Checks

### 0A. Identify Target File
Decks live at `Quarto/<genre>/<name>.qmd`. Resolve the argument rather than
building a path by hand:

```bash
python3 scripts/deckpath.py [PaperName] --field qmd
```

A bare name works; `genre/name` disambiguates if two genres ever share one.
If no argument, ask the user. `python3 scripts/deckpath.py --list` shows what
exists.

### 0B. Language Selection
The deck already declared this. Read it, do not ask:

```bash
python3 scripts/deckprofile.py [PaperName] --field notes_language
python3 scripts/deckprofile.py [PaperName] --field speaking_min 2>/dev/null
```

- `ko` - Korean script, 280 Hangul syllables/min
- `en` - English script, 130 words/min

Multiply by the deck's `speaking_min` for the budget. `speaking_min` is
derived by `deckprofile.py` as `duration_min - video_min - qa_min` (floored
at 0): the minutes the presenter actually talks, not the wall-clock slot. A
60-minute lecture with 10 minutes of clips and 5 of questions is a
45-minute script, ~12,600 Hangul syllables in Korean or ~5,850 words in
English; a 30-minute paper review with neither is ~8,400 / ~3,900. Deriving
it from the declared numbers is the point - a hardcoded budget silently
belongs to whichever genre it was written for, and a budget on the slot
length over-writes every deck that plays video.

`--lang` still overrides, for the one-off case where the notes are being
written in a different language from what the deck will normally use. Say so
explicitly when you override, so the mismatch with the config is visible.

If the deck has no config (the four decks that predate `/new-deck`), fall
back to asking the user.

### 0C. Check for Existing Notes
Search the QMD for `::: {.notes}` blocks.
- If notes already exist: warn user and ask whether to overwrite or skip slides that have notes.
- If no notes: proceed.

### 0D. Locate Source Materials
1. **QMD file** — primary source (must exist)
2. **Deck sources** — whatever `<deck>.deck.yml` names under `sources:` (a
   paper PDF, a vault research note, a reference list) or the presenter
   supplies in the conversation

Report what sources are available. Notes live only as inline `::: {.notes}`
blocks in the QMD; there is no separate presenter-script file to read or
write.

---

## Phase 1: Read & Analyze Slides

1. Read the complete QMD file
2. Count total slides (level-2 headings `##`) and sections (level-1 headings `#`)
3. Identify slide structure: which slides are content-heavy, which are light
4. Note section boundaries for narrative arc planning
5. Calculate target total budget based on language selection

Report to user:
- Total slides found
- Section breakdown
- Target script length
- Source materials available

---

## Phase 2: Batch Generation

Delegate to the `script-writer` agent in batches of 8–10 slides.

For each batch, provide the agent with:
1. The QMD content for those slides
2. The overall presentation context (paper title, what came before, what comes after)
3. The language setting
4. Approximate per-batch budget (total budget / number of batches, adjusted for content density)
5. Relevant source paper sections (for technical slides only)

**Batch sequencing:**
- Process batches sequentially (each batch needs context from previous batches for transitions)
- After each batch, verify the notes were properly inserted with `::: {.notes}` syntax
- Track running word/char count

**Notes placement rule:**
- Place `::: {.notes}` at the end of each slide, before the next `##` heading
- Section dividers (`#`) get brief transition notes
- References slide: skip (no notes)

---

## Phase 3: Count Verification

After all batches are complete:

1. Count total script length:
   - **Korean:** count characters excluding spaces, punctuation, and markdown syntax
   - **English:** count words excluding markdown syntax
2. Compare against the target derived from the deck's own `speaking_min`
   (Phase 0B), not a fixed number:
   - Korean: `speaking_min × 280` Hangul syllables (±10%)
   - English: `speaking_min × 130` words (±10%)

   For the 30-minute paper reviews this skill was written against that is
   8,400 syllables / 3,900 words, which is where the old fixed figures came
   from. A 60-minute lecture with no video is twice that, a 20-minute
   conference talk is a third of it, and a lecture that plays clips is
   budgeted on the minutes left after them.
3. If outside acceptable range:
   - **Too long:** identify the longest notes and ask the script-writer agent to trim
   - **Too short:** identify slides with thin notes and ask for expansion
   - Re-count after adjustment

---

## Phase 4: Render & Verify

1. Run `quarto render "$(python3 scripts/deckpath.py [PaperName] --field qmd)"`
2. Verify render succeeds without errors
3. Check the HTML output for `<aside class="notes">` elements
4. Report number of slides with notes vs total slides

---

## Phase 5: Timing Report

Generate a timing report and save to `quality_reports/[PaperName]_speaker_notes_report.md` using the template at `templates/speaker-notes-report.md`.

The report should include:
- Per-section breakdown (section name, number of slides, word/char count, estimated time)
- Total estimated presentation time
- Quality checklist status

Present a summary to the user including:
- Total script length (words or chars)
- Estimated presentation time
- Coverage (slides with notes / total slides)
- Any quality concerns

---

## Non-Negotiable Constraints

1. **Script, not notes.** Every note must be a complete, speakable script.
2. **No verbatim repetition.** Notes must add value beyond the slide content.
3. **Transitions matter.** Each note should flow naturally from the previous slide.
4. **Budget compliance.** Total must fall within ±10% of target range.
5. **Proper syntax.** Every `::: {.notes}` must have a matching `:::` closure.
6. **No notes on References slide.** Skip it entirely.

---

## Examples

### Example 1: First-time script generation
**User says:** `/write-speaker-notes DreamZero`
**Actions:**
1. `deckpath.py DreamZero --field qmd` → `Quarto/papers/DreamZero.qmd`
2. `deckprofile.py DreamZero` → notes `ko`, speaking_min 30 → target ~8,400 syllables
3. Read QMD, count slides, locate source paper
4. Generate notes in 4-5 batches via script-writer agent
5. Verify total char count within range
6. Render and verify
7. Generate timing report

### Example 2: Adding notes to already-annotated file
**User says:** "Add speaker notes to the new slides I added"
**Actions:**
1. Find QMD, detect existing `::: {.notes}` blocks
2. Identify slides WITHOUT notes
3. Generate notes only for unannotated slides
4. Verify count and render

### Example 3: One-off language override
**User says:** "/write-speaker-notes DreamZero --lang en"
**Actions:**
1. Say plainly that the deck declares `notes: ko` and this run overrides it.
   If English is what the deck should use from now on, the fix is
   `language.notes` in `DreamZero.deck.yml`, not repeating the flag.
2. If Korean notes exist, warn and ask whether to replace
3. If replacing, remove all existing `::: {.notes}` blocks first
4. Generate English script targeting `speaking_min × 130` words
5. Verify and render

### Example 4: A 60-minute lecture
**User says:** `/write-speaker-notes dgist-2026f-w02`
**Actions:**
1. `deckprofile.py` → notes `ko`, duration 60 with `video_min: 10` and
   `qa_min: 5` → speaking_min 45 → target ~12,600 syllables
2. Half again a paper review's script, not double: the clips and the
   questions are not narrated. Budget the batches for it rather than
   writing a 60-minute script and calling the deck overlong.
