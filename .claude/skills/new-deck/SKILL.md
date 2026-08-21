---
name: new-deck
description: Start a new slide deck - paper review, invited talk, or course lecture. Interviews the presenter about the deck's premises, scaffolds it, and carries the authoring workflow through to the quality gate. This is the single entry point for creating a deck.
argument-hint: "[rough topic or deck name]"
allowed-tools: ["Read", "Grep", "Glob", "Write", "Edit", "Bash", "Agent", "AskUserQuestion"]
---

# Start a new deck

Decks in this repo are graded against a profile, and the profile only knows
what to enforce if someone writes down who is listening and for how long.
Before this skill existed those premises lived in the presenter's head, leaked
into the deck as inconsistencies, and were re-derived from scratch every time
anyone touched it. Ask once, write it down, and every downstream tool reads it
from the same place.

Two halves, deliberately: **you run the interview, `scripts/new_deck.py` writes
the files.** Ask the questions however the conversation needs them asked. The
scaffold stays byte-identical for the same answers.

## 1. Ask

Use `AskUserQuestion` — this is a set of judgment calls, not a form. Batch
related ones; do not ask about anything the user already told you. Lead with a
recommendation when there is an obvious default.

**Genre** — `papers`, `talks`, or `lectures`. Run
`python3 scripts/deckpath.py --genres` for the live list. This picks the
directory and, unless overridden, the profile.

**Audience prior knowledge** — `none`, `practitioner`, or `expert`. The single
most consequential answer: it sets which profile's bullet budget and checks
apply (and it is what the review agents read the deck against); guessing
`practitioner` for a room of first-years produces a deck that scores well and
lands badly. The acronym-expansion check is off for every shipped profile
(D17: the matcher cannot tell a model name from a term), so spelling terms
out is judgment, not a gate.

**Duration** in minutes, and roughly how many people. Then two optional
subtractions: **video_min** (minutes of clips that play without narration)
and **qa_min** (minutes reserved for questions). `deckprofile.py` derives
`speaking_min = duration_min - video_min - qa_min`, and that is what the
speaker-notes budget runs on; a 60-minute lecture with 10 minutes of video
is a 50-minute script, not a 60-minute one. Omit both when the deck is all
talk.

**Where it sits in a series** - for a lecture, which course series and which
session. Run `python3 scripts/series_assets.py --list` for the series files
(`Quarto/lectures/_series/<course>.yml`, one per course; `dgist-2026f` is the
DGIST HSS118 term). When the deck is a session of one:

- ask for the **series** and the **session index** (the week number, W02 = 2)
  and pass `--series <course> --series-index <NN>`: the scaffold takes the
  title, the date and the deck name `<course>-w<NN>` from the series file,
  writes `series:` and `series_index:` into `deck.yml` and `series: <course>`
  into the qmd front matter (what the series shortcodes read), and puts the
  four shared slides in the stub (`_series/<course>/semester-map.qmd`,
  `course-runs.qmd`, `ask-anytime.qmd` near the top, `qa.qmd` last) with a
  TODO notes block after each include;
- confirm the title from the series rather than re-asking it; a session
  whose index is not in the series file is refused, and a deck.yml that
  names one later fails loudly in `deckprofile.py`;
- the previous session comes from the series too (holiday and exam weeks
  are skipped; a guest or DGIST session counts), so the recap slide's TODO
  already names it and the gate's callback message does as well;
- if the series file does not exist yet, write it first (schema in the
  header of `dgist-2026f.yml`), run `python3 scripts/series_assets.py
  <course>` to build the lock, the QR and the semester maps, and add the
  shared slides under `Quarto/lectures/_series/<course>/`.

A lecture outside any series keeps the bare `--series-index`; `series_index:
1` exempts the deck from the prior-session callback check, anything else
requires it.

**Language** — slides default to English, notes to Korean, for every genre.
Confirm rather than re-derive. Non-English slides are allowed by declaring
`language.slides` here, which is why the Korean gate can stay strict
everywhere else instead of having a directory punched out of it. An English
deck may still carry a little Hangul (term glosses, Wooclap instructions):
the lecture profile allows 300 characters, the others 0, and a deck can set
its own `language.korean_allowance` by editing the generated `deck.yml` --
not an interview question unless the presenter raises it.

**Delivery** — `in-person`, `remote`, or `hybrid`. Remote changes what you can
rely on: no pointing at the screen, no reading the room, and a network that
may not hold.

**Sources** - paths or URLs the fact-check agent will compare the slides
against: a paper PDF, a vault research note, a reference list. Optional, a
list; it can grow later. There is no publication question: merging to `main`
publishes (plan D11). Ask instead whether the deck will carry anything not
yet public, and if so seed `Quarto/<genre>/<name>.forbidden.txt` (one term
per line; any hit in visible slide text is a BLOCKER at the gate).

**Deck name** — kebab-case, unique across every genre, since the speaker-note
backups are keyed on it and `preview.sh <name>` takes a bare name. For a course series use `<venue>-<term>-w<NN>`, e.g.
`dgist-2026f-w02`.

## 2. Show the answers back

Before writing anything, run the scaffold with `--dry-run` and show the
resulting `deck.yml`. It is short, and it is what the deck will be graded
against — cheaper to correct now than after six decks exist.

## 3. Scaffold

```bash
# a session of a course series: name, title and date come from the series file
python3 scripts/new_deck.py \
  --series dgist-2026f --series-index 2 \
  --audience none --duration 60 --video-min 10 --qa-min 5 \
  --delivery in-person \
  --sources ../vault/1-projects/dgist/w02-research.md

# a lecture outside any series, or a talk / paper review
python3 scripts/new_deck.py \
  --name some-talk --genre talks \
  --title "A talk" --audience practitioner --duration 30
```

Or pass the whole answer set as JSON on stdin with `--from-answers -`.

It refuses to overwrite an existing file and refuses a name already taken in
another genre. Both are hard errors, not prompts.

## 4. Write the deck

The scaffold is two slides and a config. Authoring is the rest, and it is a
collaborative, iterative process: **the presenter drives the vision, you are a
thinking partner.** Work in batches of 5-10 slides and share each batch for
feedback — do not bulk-dump a finished deck.

Read first, in this order:

- `.claude/rules/slide-design-principles.md` — the shared core
- `.claude/rules/slide-profiles/<profile>.yml` — this deck's budget *and* its
  prose guidance; the numbers there are the ones the gate enforces
- previous decks in the same genre, and for a lecture series, where the last
  session ended

Non-negotiable while drafting, whatever the genre:

1. **Motivation before formalism.** No exceptions.
2. **A worked example within two slides of every definition.**
3. **Check every new symbol against the notation already in use** in the
   series, so the same thing does not get two names across sessions.
4. **Transition slides at major conceptual pivots.**
5. **Density budget on every slide as you write it**, from the profile — not
   from memory, and not from another genre's numbers.
6. **Never shrink fonts to fit.** Split the slide instead. `.smaller` and
   `.smallest` are worth -5 each at the gate.
7. **Every citation resolves** against `Bibliography_base.bib`.

Figures: inline SVG, a matplotlib script, or a generated image, chosen per
figure by judgment. They live under `Figures/<genre>/<name>/`; browsers cannot
render PDF inline, so export vector figures as SVG. Keep
`Figures/<genre>/<name>/figures.yml` alongside them (`file`, `source`,
`licence`, `third_party` per figure): every `third_party: true` figure must
name its `source` in a `.footnote` or caption on the slide that shows it, or
the gate deducts.

Videos: declare every clip once in `Figures/<genre>/<name>/videos.yml`, then
run `python3 scripts/media_prep.py <name>` to cut and lock them and `bash
scripts/media_release.sh <name>` to publish them on the deck's GitHub Release.
Slides place a clip with `{{< video-card slug >}}` or
`## {.video-full video="@slug"}`, never by URL. The manifest schema and the
rest of the pipeline are in AGENTS.md, Videos.

Write a plain hyphen, never `---` or `--` (Quarto renders them as em and en
dashes; the gate deducts), and never a level-1 `#` heading after the title
(Quarto stacks every following slide under it; the gate blocks). Section
breaks are `## {.divider}` slides.

## 5. Verify before calling it done

```bash
bash scripts/preview.sh <name>            # walk every slide in a browser
python3 scripts/quality_score.py "$(python3 scripts/deckpath.py <name> --field qmd)" --summary
```

Rendering is not verification. Overflow does not raise, and the gate cannot
see a slide that is technically legal and pedagogically empty. Walk it.

```
[ ] Renders without errors
[ ] No slide overflows at 1280x720
[ ] All citations resolve
[ ] Every definition has motivation + a worked example
[ ] Density budget respected -- the profile's numbers, not five by habit
[ ] No .smaller/.smallest anywhere
[ ] Transition slides are ## {.divider} slides, no level-1 heading anywhere
[ ] No ---, --, or literal em/en dash in slide text
[ ] Third-party figures name their source on the slide (figures.yml)
[ ] Every clip declared in videos.yml, encoded, and live on the deck's Release
[ ] No term from <name>.forbidden.txt in slide text
[ ] Score >= 80 to commit, >= 90 to ship
[ ] /slide-excellence run (visual, pedagogy incl. challenges, proofreading,
    fact check, render audit)
```

For a lecture, additionally: an opening slide that names where the previous
session ended (the gate checks it for decks on the `lecture` profile with
`series_index` other than 1, and names the session the series file expects),
and terms spelled out on first appearance by judgment, with the Korean gloss
in the notes. For a session of a series, keep the four shared includes where
the scaffold put them; the semester map, the QR and the rules come from the
series lock, so a date or a code is changed in the series yml and
`series_assets.py` is re-run, never on the slide (the Wooclap URL and code
are PLACEHOLDER until the event exists).

## Changing the premises later

Edit `<deck>.deck.yml`. It changes how the deck is graded, so edit it when the
premise actually changed — the talk moved from 45 minutes to 20, the audience
turned out to be undergraduates. Editing it to silence a warning is the one
use that defeats the point.
