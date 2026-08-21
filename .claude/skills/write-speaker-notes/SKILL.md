---
name: write-speaker-notes
description: Generate speaker notes (presentation script) for Quarto RevealJS slides - paper reviews, course lectures, and invited talks. Supports English and Korean. Use when user asks to "write speaker notes", "add presentation script", "speaker script", "발표 스크립트", or "스피커 노트".
argument-hint: "[DeckName] [--lang en|ko to override the deck's config]"
allowed-tools: ["Read", "Write", "Edit", "Bash", "Grep", "Glob", "Agent"]
---

# Speaker Notes (Presentation Script) Workflow

Generate a verbatim reading script for a deck. The presenter reads these
notes as-is during the talk, so every note is the actual sentences to say
aloud, in the language the deck declares.

**CRITICAL: These are presentation scripts (대본), NOT talking points.** Full
spoken sentences that flow naturally when read aloud.

The deck's genre decides what a good script is. Never guess the genre: read
the resolved profile first (Phase 0B) and apply the matching genre section
below. The mechanics (where notes live, the three privacy layers) are the
same for every genre.

---

## Phase 0: Pre-Flight Checks

### 0A. Identify Target File
Decks live at `Quarto/<genre>/<name>.qmd`. Resolve the argument rather than
building a path by hand:

```bash
python3 scripts/deckpath.py [Deck] --field qmd
```

A bare name works; `genre/name` disambiguates if two genres ever share one.
If no argument, ask the user. `python3 scripts/deckpath.py --list` shows what
exists.

### 0B. Read the Deck's Premises (profile + deck.yml)

Everything the script depends on is declared, not guessed. Read both, first
thing:

```bash
python3 scripts/deckprofile.py [Deck]                       # resolved config, JSON
cat "$(python3 scripts/deckpath.py [Deck] --field config)"  # the raw deck.yml
```

From the resolved JSON:

- `profile` - which genre section below applies: `paper-review`, `lecture`,
  or `invited-talk`
- `notes_language` - `ko` (280 Hangul syllables/min) or `en` (130 words/min)
- `speaking_min` - the minutes the presenter actually talks
- `prior_session` - for a lecture in a series: the previous session's title,
  week, date and presenter. The opening note names it (see Genre: Lecture)
- `sources` - what technical claims in the notes are checked against

From the raw deck.yml: `audience.assumes`, `audience.size`, `audience.prior`
and `delivery` - review-agent context the resolved JSON does not carry; the
invited-talk section depends on it.

**Budget = `speaking_min` x 280 Hangul syllables (ko) or x 130 words (en).**

`speaking_min` is derived by `deckprofile.py` as
`duration_min - video_min - qa_min` (floored at 0): the minutes the
presenter actually talks, not the wall-clock slot. A 60-minute lecture with
10 minutes of clips and 5 of questions is a 45-minute script, ~12,600 Hangul
syllables in Korean or ~5,850 words in English; a 30-minute paper review
with neither is ~8,400 / ~3,900. Deriving it from the declared numbers is
the point - a hardcoded budget silently belongs to whichever genre it was
written for, and a budget on the slot length over-writes every deck that
plays video.

`--lang` still overrides, for the one-off case where the notes are being
written in a different language from what the deck will normally use. Say so
explicitly when you override, so the mismatch with the config is visible.

If the deck has no config (no tracked deck is in that state today), fall
back to asking the user.

### 0C. Check for Existing Notes
Search the QMD for `::: {.notes}` blocks and a front matter `data-notes:`.
- If notes already exist: warn user and ask whether to overwrite or skip slides that have notes.
- If no notes: proceed.

### 0D. Locate Source Materials
1. **QMD file** - primary source (must exist)
2. **Deck sources** - whatever `<deck>.deck.yml` names under `sources:` (a
   paper PDF, a vault research note, a reference list) or the presenter
   supplies in the conversation

Report what sources are available. Notes live only inline in the QMD (see
below); there is no separate presenter-script file to read or write.

---

## Where Notes Live (same for every genre)

Inline, one block per slide, at the end of the slide's content:

```markdown
::: {.notes}
The sentences to say on this slide.
:::
```

The spelling must be exactly `::: {.notes}`. Variants Quarto accepts
(`:::{.notes}`, `::: notes`) render fine but the git clean filter does not
match them, which means those notes would be committed. Plain text only
inside the block: no nested `:::` divs (the filter's closing match stops at
the first `:::` line), no markdown emphasis, no links.

The title slide is generated from the front matter, so a notes div cannot
attach to it. Its notes go in the front matter instead:

```yaml
title-slide-attributes:
  data-notes: |
    The opening lines, spoken before the first slide change.
```

Shared include slides (series lectures): the note goes in the deck right
after the `{{< include >}}` line. Everything before the next `##` belongs to
the included slide, and the shared `_series/` file itself carries no notes.

---

## Phase 1: Read & Analyze Slides

1. Read the complete QMD file
2. Count total slides (level-2 headings `##`) and any `{{< include >}}`
   slides (each include is one slide that needs a deck-side note)
3. Identify slide structure: which slides are content-heavy, which are light
4. For lectures, also mark the special slides: video slides (`.video-full`,
   `video-card`), question slides (hand-raise, Wooclap), shared includes -
   each has its own note shape (see Genre: Lecture)
5. Note section boundaries for narrative arc planning
6. Calculate target total budget from Phase 0B

Report to user:
- Total slides found
- Section breakdown
- Target script length
- Source materials available

---

## Phase 2: Batch Generation

Delegate to the `script-writer` agent in batches of 8-10 slides.

For each batch, provide the agent with:
1. The deck name and the resolved profile JSON from Phase 0B, verbatim
2. The raw `<deck>.deck.yml` content
3. The QMD content for those slides
4. The overall context (deck title, what came before, what comes after, and
   the final note of the previous batch for the transition)
5. Approximate per-batch budget (total budget / number of batches, adjusted
   for content density)
6. Relevant source excerpts (for technical slides only)
7. Lecture decks: the running gloss list - technical terms already glossed
   in earlier batches. The agent glosses only first appearances and reports
   which terms it glossed; append those to the list before the next batch.

**Batch sequencing:**
- Process batches sequentially (each batch needs context from previous batches for transitions)
- After each batch, verify the notes were properly inserted with `::: {.notes}` syntax
- Track running word/char count

**Notes placement rule:**
- Place `::: {.notes}` at the end of each slide, before the next `##` heading
- Include slides: the note goes right after the `{{< include >}}` line
- Section dividers (`## {.divider}`) get brief transition notes
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

   For a 30-minute paper review that is 8,400 syllables / 3,900 words. A
   60-minute lecture with no video is twice that, a 20-minute conference
   talk is a third of it, and a lecture that plays clips is budgeted on the
   minutes left after them.
3. If outside acceptable range:
   - **Too long:** identify the longest notes and ask the script-writer agent to trim
   - **Too short:** identify slides with thin notes and ask for expansion
   - Re-count after adjustment

---

## Phase 4: Render & Verify

1. Run `quarto render "$(python3 scripts/deckpath.py [Deck] --field qmd)"`
2. Verify render succeeds without errors
3. Check the HTML output for `<aside class="notes">` elements (and
   `data-notes` on the title section, if the deck has title notes)
4. Report number of slides with notes vs total slides
5. Suggest the presenter open the local HTML and press `S`: reveal's
   speaker view shows the notes, a timer, and the next slide. The
   dual-display leak test for the deployed page is in AGENTS.md
   (Speaker Notes Policy); run it before presenting from a new deploy.

---

## Phase 5: Timing Report

Generate a timing report and save to `quality_reports/[Deck]_speaker_notes_report.md` using the template at `templates/speaker-notes-report.md`.

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

## Genre: Paper Review (`paper-review`)

The audience is working ML people (the profile says so). The value of the
script is judgment, not coverage - the room can read the abstract itself.

- The title-slide note states the paper being reviewed (venue, group, why it
  earned a session) and sets the talk's scope and duration.
- Results and figure notes compare to baselines out loud: name the number
  worth remembering and say whether it survives scrutiny.
- "My Take" notes are personal and opinionated, with the reasoning behind
  the opinion; they are the memorable part of the talk.
- When official code exists, at least one note says something
  implementation-level that is not in the paper's text.

## Genre: Lecture (`lecture`)

First- and second-year students, most of them non-majors, and they HEAR the
notes: for `notes: ko` each note is the actual Korean sentences to say
aloud, not an English summary of what to cover. If a note cannot be read
verbatim to a student who has never seen a loss curve, it is wrong.

- **Open by naming the prior session.** `deckprofile.py` prints
  `prior_session` (title, week, date, presenter). The first content note
  reconnects by name: what that session was about, where it stopped, what
  today adds. A guest session counts and is credited to its presenter.
- **Gloss every technical term in Korean in the note the FIRST time the
  term appears** in the deck; after that, use the term plainly. Slides stay
  English; the gloss lives in the note (the lecture profile's guidance says
  the same). Track first uses across batches (Phase 2).
- **Bridge by reuse**: "you already know X, and this is X reused" is the
  reliable move for this audience - diffusion they have seen making images
  is the same machinery generating actions. Reach for that bridge before
  reaching for a new abstraction.
- **Video slides**: the note has two labeled parts. Before play: the
  sentences to say before pressing play - what to watch for and why this
  clip. During: what to point at while it runs, or that silence is fine.
  Anything to say after the clip belongs to the next slide's note.
- **Question slides** (hand-raise, Wooclap): the note contains the exact
  question sentence to ask, verbatim, plus a follow-up line for each
  outcome (most hands up / a few / none), so the moment never stalls.
- **Shared include slides**: notes go after the include line in the deck
  (see Where Notes Live). The semester map, course rules and QR slides get
  short per-deck notes - what today's position on the map means, not a
  re-reading of the rules.

## Genre: Invited Talk (`invited-talk`)

The room varies by invitation, which is exactly why the profile declares
less: read `audience.assumes`, `audience.size` and the audience description
from the deck.yml before writing a word. The same slide gets a different
sentence for practitioners than for a mixed or executive room. A talk
carries one claim; the notes keep returning to it, and the closing note
states it in a single sentence a listener could repeat afterwards.

---

## Privacy: The Three Layers

Notes are local-only, presenter-screen-only, and never reach git or the
deployed page (plan D13). Three independent layers enforce it: a git clean
filter strips them before staging, a CI strip removes them from every
rendered deck HTML at deploy, and `backup_notes.py` keeps a gitignored copy
as insurance against a `git checkout` smudging the note-free blob over the
working file. Mechanism, file names and the one-time setup command are in
AGENTS.md, Speaker Notes Policy.

Two rules this workflow owns: **back up after every writing session**
(`python3 scripts/backup_notes.py backup [Deck]`), and **never maintain
separate branches** for notes vs no-notes - a notes branch leaks on the
first merge.

---

## Non-Negotiable Constraints

1. **Script, not notes.** Every note must be a complete, speakable script in the deck's notes language.
2. **No verbatim repetition.** Notes must add value beyond the slide content.
3. **Transitions matter.** Each note should flow naturally from the previous slide.
4. **Budget compliance.** Total must fall within ±10% of target.
5. **Proper syntax.** Exactly `::: {.notes}` with a matching `:::` closure; title notes only via `title-slide-attributes: data-notes:`.
6. **No notes on References slide.** Skip it entirely.

---

## Examples

### Example 1: First-time script generation
**User says:** `/write-speaker-notes DreamZero`
**Actions:**
1. `deckpath.py DreamZero --field qmd` → `Quarto/papers/DreamZero.qmd`
2. `deckprofile.py DreamZero` → profile `paper-review`, notes `ko`, speaking_min 30 → target ~8,400 syllables
3. Read QMD, count slides, locate source paper
4. Generate notes in 4-5 batches via script-writer agent (paper-review genre)
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

### Example 4: A 60-minute lecture in a series
**User says:** `/write-speaker-notes dgist-2026f-w02`
**Actions:**
1. `deckprofile.py` → profile `lecture`, notes `ko`, duration 60 with
   `video_min: 10` and `qa_min: 5` → speaking_min 45 → target ~12,600
   syllables; `prior_session` names the W01 session and its presenter
2. Half again a paper review's script, not double: the clips and the
   questions are not narrated. Budget the batches for it rather than
   writing a 60-minute script and calling the deck overlong.
3. The first content note names the prior session and where it stopped;
   every technical term gets its Korean gloss at first appearance; video
   notes split into before-play and during; question slides carry the exact
   question sentence and per-outcome follow-ups; the four shared include
   slides get their notes right after the include lines.
