---
name: slide-excellence
description: The one review fan-out for a deck - visual audit, pedagogical review (with the devil's-advocate challenges), proofreading, fact check against the deck's declared sources, and a render audit of full-deck screenshots, run as parallel subagents and synthesized. Use for a comprehensive quality check before milestones, or when the user says "review the deck", "proofread", "pedagogy review", "fact check", or "challenge the slides".
argument-hint: "[DeckName]"
allowed-tools: ["Read", "Grep", "Glob", "Write", "Bash", "Agent"]
context: fork
---

# Slide Excellence Review

Run a comprehensive multi-dimensional review of a Quarto deck. Up to five
components run independently and in parallel, then the results are
synthesized into one summary. This is the one fan-out: the former standalone
proofreading, pedagogy, and devil's-advocate skills were folded in here, and
the fact check and render audit joined in WP6.

**Read-only.** No agent edits a source file. Fixes are applied separately
after the presenter reviews the reports.

## Steps

### 1. Resolve the deck and capture its premises

`$ARGUMENTS` is a deck name (bare name or `genre/name`). Resolve paths
through the scripts, never by hand, and capture three things every agent
will receive:

```bash
QMD=$(python3 scripts/deckpath.py <Deck> --field qmd)
PROFILE_JSON=$(python3 scripts/deckprofile.py <Deck>)          # resolved profile, as JSON
DECK_YML=$(cat "$(python3 scripts/deckpath.py <Deck> --field config)")   # <deck>.deck.yml verbatim
```

If the deck predates `/new-deck` and has no `deck.yml`, `DECK_YML` is empty:
say so, and the agents review against the genre's default profile (the
profile JSON still resolves).

Set `DATE` to today as `YYYY-MM-DD`. All reports for this run go under
`quality_reports/reviews/` (`mkdir -p` it):

| Component | Report |
|---|---|
| slide-auditor | `quality_reports/reviews/<Deck>-visual-<DATE>.md` |
| pedagogy-reviewer | `quality_reports/reviews/<Deck>-pedagogy-<DATE>.md` |
| proofreader | `quality_reports/reviews/<Deck>-proofread-<DATE>.md` |
| domain-reviewer (fact check) | `quality_reports/reviews/<Deck>-factcheck-<DATE>.md` |
| render audit | `quality_reports/reviews/<Deck>-render-<DATE>.md` |
| synthesis (this skill) | `quality_reports/reviews/<Deck>-<DATE>.md` |

### 2. Decide which components run (by profile)

Read `profile` and `sources` from `PROFILE_JSON`:

- **`lecture`**: all five components run, always. A lecture with an empty
  `sources` list still gets the fact-check agent - its report saying "no
  sources declared, these claims are unverifiable" is exactly the warning a
  lecture needs.
- **`paper-review`, `invited-talk`, anything else**: slide-auditor,
  pedagogy-reviewer, proofreader and the render audit run; the fact check
  runs only when `sources` is non-empty (a paper review's source of record
  is the paper itself - declare it in `deck.yml: sources:` to opt in).
- A deck may force a component either way when the presenter asks; say so
  in the synthesis.

### 3. Launch the review agents in parallel

Launch every selected agent in one message. **Each agent's prompt
contains, verbatim:** the deck name, the qmd path, the full `PROFILE_JSON`,
the full `DECK_YML` (fenced, labelled "deck.yml"), and its report path from
the table above. The agents also re-run `deckprofile.py` themselves as their
own step 0; passing the JSON in the prompt is what lets them start reading
slides immediately and keeps one source of truth if the two ever disagree
(the fresh run wins).

**slide-auditor** - density against the deck's own budget (it must quote
`bullets_max` etc. from the profile JSON), overflow, font consistency, box
fatigue, centering, image and figure paths.

**pedagogy-reviewer** - the 13 patterns, deck-level arc and pacing, the
prior-session callback checked against `prior_session` from the profile
JSON, and the devil's-advocate challenges. The challenge list lives in
`.claude/agents/pedagogy-reviewer.md` and only there; do not restate it in
the prompt.

**proofreader** - grammar, typos, overflow against the profile budget,
consistency (citations against `Bibliography_base.bib`), register for the
declared audience.

**domain-reviewer (fact check)** - reads every entry of `sources` (vault
paths and URLs alike), compares each date, number, name and autonomy label
on the slides against them, checks `<deck>.forbidden.txt` in spirit, flags
unsourced claims.

### 4. Render audit

Screenshot the whole deck (this renders the html first when it is stale):

```bash
python3 scripts/shoot_slides.py <Deck> --out /tmp/<Deck>-shots
```

Then launch one **general-purpose** agent whose prompt contains: the shot
directory, `PROFILE_JSON`, `DECK_YML`, and the report path. Its instructions:
Read every PNG in order and report, per slide (the `-NN` index in the file
name), anything a human in row 30 would notice:

- overflow: text or figures clipped at a slide edge
- missing posters: a video slide showing a black or empty frame
- illegible text: too small for the room, or low contrast on its background
- broken layout: overlapping elements, unstyled raw HTML, empty slides,
  a figure that failed to load
- wrong theme: a slide that visibly escapes the deck's theme

Same report shape as the auditor (slide, issue, severity, recommendation),
saved to its report path. Read-only: it never edits and never re-renders.

### 5. Synthesize the combined summary

Write `quality_reports/reviews/<Deck>-<DATE>.md`:

```markdown
# Slide Excellence Review: <Deck>

**Date:** <DATE> | **Profile:** [name] | **Audience:** [from deck.yml / the profile]
**Components run:** [list; name any skipped and why, e.g. "fact check skipped: no sources declared"]

## Overall Quality Score: [EXCELLENT / GOOD / NEEDS WORK / POOR]

| Dimension | Critical | Medium | Low |
|-----------|----------|--------|-----|
| Visual/Layout | | | |
| Pedagogical (incl. challenges) | | | |
| Proofreading | | | |
| Fact check | | | |
| Render audit | | | |

### Critical Issues (Immediate Action Required)
### Medium Issues (Next Revision)
### Recommended Next Steps
```

Then present to the user: the score, the per-dimension counts, the top
critical issues, and every report path.

## Quality Score Rubric

| Score | Critical | Medium | Meaning |
|-------|----------|--------|---------|
| Excellent | 0-2 | 0-5 | Ready to present |
| Good | 3-5 | 6-15 | Minor refinements |
| Needs Work | 6-10 | 16-30 | Significant revision |
| Poor | 11+ | 31+ | Major restructuring |

Any CRITICAL fact-check finding (a wrong fact, an autonomy mismatch, a
forbidden-term near-miss) caps the score at NEEDS WORK regardless of the
counts: a beautiful deck that says a teleoperated demo was autonomous is
not "Good".

## Notes

- `/visual-audit` remains the standalone layout-only pass; it uses the same
  `scripts/shoot_slides.py` screenshots.
- The devil's-advocate question list has one home: the pedagogy agent
  (`.claude/agents/pedagogy-reviewer.md`).
