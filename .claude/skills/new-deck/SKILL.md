---
name: new-deck
description: Interview the presenter about a new deck's premises, then scaffold it. Use when starting any new slide deck - paper review, invited talk, or course lecture.
argument-hint: "[rough topic or deck name]"
allowed-tools: ["Read", "Bash", "AskUserQuestion"]
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
most consequential answer. `none` turns on the acronym-expansion check and
tightens the bullet budget; guessing `practitioner` for a room of first-years
produces a deck that scores well and lands badly.

**Duration** in minutes, and roughly how many people.

**Where it sits in a series** — for a lecture, which session number and what
the audience has already seen. `series_index: 1` exempts the deck from the
prior-session callback check; anything else requires it.

**Language** — slides default to English, notes to Korean, for every genre.
Confirm rather than re-derive. Non-English slides are allowed by declaring
`language.slides` here, which is why the Korean gate can stay strict
everywhere else instead of having a directory punched out of it.

**Delivery** — `in-person`, `remote`, or `hybrid`. Remote changes what you can
rely on: no pointing at the screen, no reading the room, and a network that
may not hold.

**Publication** — `web`, `pdf-only`, or `private`. Ask directly if the deck
will carry anything not yet public. See `.claude/rules/` on internal content.

**Deck name** — kebab-case, unique across every genre, since the speaker-note
backups and presenter scripts are keyed on it and `preview.sh <name>` takes a
bare name. For a course series use `<venue>-<term>-w<NN>`, e.g.
`dgist-2026f-w02`.

## 2. Show the answers back

Before writing anything, run the scaffold with `--dry-run` and show the
resulting `deck.yml`. It is short, and it is what the deck will be graded
against — cheaper to correct now than after six decks exist.

## 3. Scaffold

```bash
python3 scripts/new_deck.py \
  --name dgist-2026f-w02 --genre lectures \
  --title "The Paradigm Shift Toward Embodied AI" \
  --audience none --duration 60 --series-index 2 \
  --delivery in-person --publish web
```

Or pass the whole answer set as JSON on stdin with `--from-answers -`.

It refuses to overwrite an existing file and refuses a name already taken in
another genre. Both are hard errors, not prompts.

## 4. Hand off

Tell the user what to run next:

```bash
bash scripts/preview.sh <name>
python3 scripts/quality_score.py Quarto/<genre>/<name>.qmd --summary
```

Then read `.claude/rules/slide-design-principles.md` for the shared core and
`.claude/rules/slide-profiles/<profile>.yml` for what this deck specifically
owes — the profile carries genre guidance alongside its numbers.

## Changing the premises later

Edit `<deck>.deck.yml`. It changes how the deck is graded, so edit it when the
premise actually changed — the talk moved from 45 minutes to 20, the audience
turned out to be undergraduates. Editing it to silence a warning is the one
use that defeats the point.
