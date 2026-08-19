---
name: slide-excellence
description: The one review fan-out for a deck - visual audit, pedagogical review (with the devil's-advocate questions), and proofreading run as parallel subagents, then synthesized. Use for a comprehensive quality check before milestones, or when the user says "review the deck", "proofread", "pedagogy review", or "challenge the slides".
argument-hint: "[DeckName]"
allowed-tools: ["Read", "Grep", "Glob", "Write", "Bash", "Task"]
context: fork
---

# Slide Excellence Review

Run a comprehensive multi-dimensional review of a Quarto deck. Three agents
analyze the deck independently and in parallel, then the results are
synthesized into one summary. The former standalone proofreading, pedagogy,
and devil's-advocate skills were folded in here: one invocation, one fan-out.

**Read-only.** No agent edits a source file. Fixes are applied separately after
the presenter reviews the reports.

## Steps

### 1. Resolve the deck

`$ARGUMENTS` is a deck name (bare name or `genre/name`). Resolve paths through
the script, never by hand:

```bash
python3 scripts/deckpath.py <Deck> --field qmd      # the file to review
python3 scripts/deckpath.py <Deck> --field genre
python3 scripts/deckpath.py --list                   # if the name is unknown
```

Then load the deck's resolved profile (audience, duration, language, the
density budget the gate enforces):

```bash
python3 scripts/deckprofile.py <Deck>
```

Every agent receives that profile output as context together with the QMD
path, so the review is graded against the deck's declared audience and not
against a default one. (WP6 wires more of `deck.yml` into the agents; for now
the profile dump is the contract.)

If the deck predates `/new-deck` and has no `deck.yml`, say so and let the
agents fall back to the genre's default profile.

### 2. Launch three review agents in parallel

Launch all three in one message. Each gets: the QMD path, the profile output,
the genre, and its report path.

**Agent 1: Visual audit** (`slide-auditor`)
- Density against the profile budget, overflow, font consistency
  (`.smaller`/`.smallest`, inline font-size overrides), box fatigue, centering,
  image and figure paths, Plotly chart quality
- Legacy decks pinned to `clean-academic-legacy.scss` get the legacy checks
  only (overflow, spacing), not the main-theme density limits
- Report: `quality_reports/<Deck>_visual_audit.md`

**Agent 2: Pedagogical review** (`pedagogy-reviewer`)
- The 13 pedagogical patterns, plus deck-level checks: narrative arc, pacing,
  visual rhythm, notation consistency, pre-empting student concerns
- Audience taken from the profile output and `<deck>.deck.yml` (`audience`), not assumed
- Additionally answers the devil's-advocate question list below and appends
  the answers to its report as a "Challenges" section
- Report: `quality_reports/<Deck>_pedagogy_report.md`

**Agent 3: Proofreading** (`proofreader`)
- Grammar (agreement, articles, prepositions, tense), typos
  (misspellings, duplicated words, search-and-replace artefacts), overflow
  risk (too many bullets, inline font-size overrides below 0.85em),
  consistency (citation format `@key` vs `[@key]`, notation, terminology,
  box usage), academic quality (informal language, missing words, claims
  without citations, citation keys that point at the wrong paper in
  `Bibliography_base.bib`)
- Every finding carries: location (line number or slide title), current
  text, proposed fix, category, severity
- Report: `quality_reports/<Deck>_qmd_report.md`

### 3. Devil's-advocate questions (given to the pedagogy reviewer)

Philosophy: the best deck comes out of active dialogue. The pedagogy reviewer
generates 5-7 specific challenges from these categories, each with a suggested
resolution, and answers them in its report:

1. **Ordering** - "Could the audience understand this better if X came before Y?"
2. **Prerequisites** - "Does this audience (per the profile) have the background for this notation at this point?"
3. **Gaps** - "Should an intuitive example come before this formal statement?"
4. **Alternative presentation** - "Here are two other ways to visualize or present this concept."
5. **Notation conflicts** - "This symbol conflicts with earlier usage in the deck or the series."
6. **Cognitive load** - "This slide introduces too many new symbols. Can it be split?"
7. **Standalone value** - "If this section were read on its own (handout, course page), does it stand?"

Challenge format, inside the pedagogy report:

```markdown
## Challenges

### Challenge 1: [Category] - [Short title]
**Question:** [the specific pedagogical question]
**Why it matters:** [what could go wrong]
**Suggested resolution:** [specific action]
**Slides affected:** [numbers or titles]
**Severity:** [High / Medium / Low]

## Challenge Verdict
**Strengths:** [2-3 things done well]
**Critical changes:** [0-2 changes before presenting]
**Suggested improvements:** [2-3 nice-to-have changes]
```

Principles for the challenges: be specific (exact slides and notation), be
constructive (every challenge has a resolution), be honest (if the deck is
good, say so), prioritize notation conflicts over missed metaphors, and think
like the audience the profile describes - where do they get lost?

### 4. Synthesize the combined summary

Write `quality_reports/<Deck>_slide_excellence.md`:

```markdown
# Slide Excellence Review: <Deck>

**Profile:** [profile name, audience prior, duration]

## Overall Quality Score: [EXCELLENT / GOOD / NEEDS WORK / POOR]

| Dimension | Critical | Medium | Low |
|-----------|----------|--------|-----|
| Visual/Layout | | | |
| Pedagogical (incl. challenges) | | | |
| Proofreading | | | |

### Critical Issues (Immediate Action Required)
### Medium Issues (Next Revision)
### Recommended Next Steps
```

Then present to the user: the score, the per-dimension counts, the top
critical issues, and the three report paths.

## Quality Score Rubric

| Score | Critical | Medium | Meaning |
|-------|----------|--------|---------|
| Excellent | 0-2 | 0-5 | Ready to present |
| Good | 3-5 | 6-15 | Minor refinements |
| Needs Work | 6-10 | 16-30 | Significant revision |
| Poor | 11+ | 31+ | Major restructuring |

## Notes

- For a layout-only pass, `/visual-audit` is the standalone skill; it renders
  the deck and walks it in a browser, which this fan-out does not.
- Substantive fact-checking against the deck's sources is the
  `domain-reviewer` agent; it is not part of this fan-out yet (WP6).
