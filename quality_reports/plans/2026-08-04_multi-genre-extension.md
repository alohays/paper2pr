# Multi-genre extension: paper2pr as the base for every deck

**Date:** 2026-08-04
**Status:** design, not yet implemented
**Trigger:** six DGIST HSS118 lecture decks land between Sep and Dec 2026

---

## Why now

The repo describes itself as "AI/ML Paper Review Presentations" and its scope
line reads "Ongoing multi-paper review project. Each paper in `target-papers/`
gets its own slide deck." That has already stopped being true. `SUNY.qmd` is a
career talk with its own `suny-career.scss`; it sits in the same flat namespace
as three paper reviews with nothing marking it as a different kind of thing.

Six lecture decks are about to arrive. Adding them to the flat namespace makes
ten decks with three genres and no way to tell them apart, and the design rules
that govern all of them are tuned for one genre only: a thirty-minute paper
review for an audience that already knows deep learning. A DGIST general
education lecture is sixty minutes for first- and second-year students with no
background. Same minimalism, different budget.

**Decision: paper2pr becomes the framework for every presentation Yunsung
gives.** The repo name stays (published URLs and existing links keep working);
the scope statement, the directory layout, and the quality gate all widen.

---

## 1. Genre subdirectories

```
Quarto/
├─ papers/     DreamDojo · DreamZero · RoboTTT
├─ talks/      SUNY
└─ lectures/   dgist-2026f-w02 … w14

Figures/<genre>/<deck>/
.speaker-notes/<genre>/<deck>.json
→ published at /slides/<genre>/<deck>.html
```

`Quarto/_extensions`, `_widgets`, `_script`, `fonts`, and the shared `.scss`
files stay at `Quarto/` root — they are shared infrastructure, not decks.

### What breaks, in the order it will hurt

**1. `.gitattributes` — speaker notes leak.** This is the one that matters.

```
Quarto/*.qmd filter=strip-speaker-notes
```

A gitattributes pattern containing a slash is anchored, not recursive.
`Quarto/*.qmd` does **not** match `Quarto/lectures/w02.qmd`. The moment a deck
moves into a subdirectory the clean filter stops firing and speaker notes —
which the repo treats as local-only and never-in-git — get committed silently.
Nothing fails, nothing warns; the notes are simply in the history.

Fix before moving a single file: `Quarto/**/*.qmd`, then re-run
`scripts/setup-git-filters.sh` and verify with `git check-attr filter` on a
nested path. Add a test to `scripts/` that asserts the filter resolves for a
nested deck, so this cannot regress.

**2. `.github/workflows/deploy.yml`** — four flat globs:

| Line | Current | Needs |
|---|---|---|
| render loop | `cd Quarto; for qmd in *.qmd` | recursive find, genre-aware |
| strip notes | `for html in Quarto/*.html` | recursive |
| assemble | `for html in Quarto/*.html` + `Quarto/${name}_files` | preserve `<genre>/` into `_site/slides/` |
| loose assets | `find Quarto -maxdepth 1 -type f -name '*.js'` | `-maxdepth 1` misses every genre dir |

The existing skip-list (`design-test.qmd`, `*_backup*`) gets simpler: put the
theme regression fixture in a `_fixtures/` directory that the render loop
ignores by convention rather than by name.

**3. `scripts/`** — `quality_score.py`, `preview.sh`, `sync_notes.py`,
`build_widgets.py`, `sync_to_docs.sh`, `backup_notes.py` all take a bare deck
name and assume `Quarto/<name>.qmd`. Resolve a bare name by searching the genre
directories and erroring on ambiguity, so `preview.sh w02` keeps working.

**4. `scripts/check_site_assets.py`** — relative asset paths from a nested deck
gain one `../` level. Verify against a real nested render, not by reading.

**5. `pages/index.html`** — the landing page lists decks flat. Group by genre.

### Published URLs

Moving the three existing paper decks changes `/slides/DreamDojo.html` to
`/slides/papers/DreamDojo.html`. Open question, needs a call before migration:

- **Move everything** — one consistent scheme, old links 404.
- **New genres only** — existing four stay at `Quarto/` root, lectures and
  future talks go into subdirectories. No breakage, permanently inconsistent.
- **Move plus redirect stubs** — a one-line meta-refresh HTML at each old path.
  Costs four small files and keeps every shared link alive.

Third option is cheap and reversible; recommend it unless the old links were
never shared.

---

## 2. Genre profiles

Today `.claude/rules/slide-design-principles.md` encodes one genre's rules as
universal law, and `quality_score.py` scores against them. Split into a shared
core plus per-genre overrides.

**Shared across all genres** (non-negotiable): one idea per slide, big type,
40px root, filled frame, no `.smaller` escape hatches, split rather than pack.

**Per genre:**

| | `paper-review` | `lecture` | `invited-talk` |
|---|---|---|---|
| Audience | knows deep learning | no background | varies |
| Length | ~30 min | ~60 min | varies |
| Bullets/slide | ≤5 | ≤4 | ≤5 |
| Jargon | assumed | Korean gloss required on first use | declared per deck |
| Structure | motivation → method → results | recap of last session → one idea → where it lands | declared per deck |
| Gate | 80 commit / 90 PR | same | same |

`lecture` adds two checks the paper-review gate has no reason to have: every
acronym expanded on first appearance, and a callback to the previous session in
the opening. Both are mechanically checkable and both are exactly what a
sixteen-week course for non-majors lives or dies on.

Profile is declared once in the deck's own config and read by the gate — not
inferred from the directory, so a deck can sit in `lectures/` and still be
scored as a talk if that is what it is.

---

## 3. Deck-init interview

New requirement, and the piece that makes the rest hold together. Today the
premises of a deck (who is listening, how long, what they already know, what
language) live in the author's head and leak into the deck as inconsistencies.
Ask them up front, once, and write them down.

`/new-deck` runs a short interview and emits a config the whole toolchain reads:

```yaml
deck: dgist-2026f-w02
genre: lecture
title: The Paradigm Shift Toward Embodied AI
audience:
  level: no-background          # no-background | practitioner | expert
  size: ~100
  prior: [w01]                  # sessions/decks they have already seen
duration_min: 60
language:
  slides: en                    # default
  notes: ko                     # default
delivery: in-person             # in-person | remote | hybrid
publish: web                    # web | pdf-only | private
```

Defaults come from the genre profile, so the interview is mostly confirming.
Slides default to English and notes to Korean for every genre; the interview
is where that gets changed rather than a policy anyone has to remember.

Downstream consumers:

- `quality_score.py` — picks the profile and the bullet budget
- theme selection — genre `.scss` unless the deck declares its own
- `/write-speaker-notes` — takes `language.notes` instead of a `--lang` flag
- the Korean pre-commit gate — reads `language.slides`, so a deck that
  legitimately needs Korean slides is allowed by declaration rather than by
  punching a permanent hole in the gate

That last point is the reason to build the config before the lectures rather
than after. The alternative is exempting a directory, and a directory exemption
never gets narrowed again.

---

## 4. Language policy, restated

The repo's English-only rule stands. It was never in tension with Korean
delivery:

- **Slides: English.** Also the DGIST syllabus principle — English titles double
  as search keywords, delivery is in Korean.
- **Speaker notes: Korean.** Never reach git; the clean filter strips them
  (see item 1 above — this only remains true if the pattern is fixed first).
- **Everything else committed: English.**

---

## 5. Order of work

1. Fix `.gitattributes` to `Quarto/**/*.qmd`, re-run the filter setup, verify
   `git check-attr` on a nested path. **Before any file moves.**
2. Create the three genre directories, move the four existing decks, add
   redirect stubs.
3. Update the workflow globs; render all four decks in CI and diff the output
   against the current live site.
4. Update the scripts' path resolution.
5. Split the design rules into core plus profiles; teach `quality_score.py` to
   read the profile.
6. Build `/new-deck` and the config schema.
7. Regroup the landing page.

Steps 1–4 are the migration and must land together. Steps 5–7 are additive and
can follow.

## 6. Verification

Not "it renders". Specifically:

- `git check-attr filter Quarto/lectures/x.qmd` resolves to
  `strip-speaker-notes`, and a deck with a `::: {.notes}` block staged from a
  nested path shows no notes in `git show`.
- All four migrated decks render in CI and their `_files` directories land at
  the right nested paths.
- `check_site_assets.py` passes on the assembled `_site`.
- Every old `/slides/<Name>.html` still resolves.
- `quality_score.py` scores a lecture deck against the lecture profile and a
  paper deck against the paper profile, with different bullet budgets applied.
