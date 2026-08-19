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
backups are keyed on it and `preview.sh <name>` takes a bare name. For a course series use `<venue>-<term>-w<NN>`, e.g.
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
render PDF inline, so export vector figures as SVG.

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
[ ] Transition slides between sections
[ ] Score >= 80 to commit, >= 90 to ship
[ ] /slide-excellence run (visual, pedagogy incl. challenges, proofreading)
```

For a lecture, additionally: every acronym expanded on first appearance, and
an opening slide that names where the previous session ended. The gate checks
both, but only for decks on the `lecture` profile.

## Changing the premises later

Edit `<deck>.deck.yml`. It changes how the deck is graded, so edit it when the
premise actually changed — the talk moved from 45 minutes to 20, the audience
turned out to be undergraduates. Editing it to silence a warning is the one
use that defeats the point.
