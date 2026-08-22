---
paths:
  - "Quarto/**/*.qmd"
---

# Quality Gates & Scoring Rubrics

## Thresholds

- **80/100 = Commit** -- good enough to save
- **90/100 = PR** -- ready for deployment
- **95/100 = Excellence** -- aspirational

## Quarto Slides (.qmd)

Design-principle deductions apply to decks on the main theme
(`clean-academic.scss`). Legacy decks pinned to `clean-academic-legacy.scss`
are graded without them. See `.claude/rules/slide-design-principles.md`.

The bullet and density numbers below are the **paper-review defaults**. The
numbers a given deck is actually held to come from its profile in
`.claude/rules/slide-profiles/<profile>.yml` (`paper-review`, `lecture`,
`invited-talk`), selected by `<deck>.deck.yml` and read via
`python3 scripts/deckprofile.py <deck>`. `quality_score.py` applies the
profile's budgets, not this table, when they differ.

| Severity | Issue | Deduction |
|----------|-------|-----------|
| Critical | Render failure (`quarto render`) | -100 |
| Critical | Equation overflow | -20 |
| Critical | Broken citation | -15 |
| Critical | Typo in equation | -10 |
| Major | Text overflow | -5 |
| Major | `.smaller`/`.smallest` or font-size override used to fit content | -5 per slide |
| Major | >5 bullets on a slide (>3 with a figure; one less again if a bullet wraps to two lines) | -3 per slide |
| Major | >1 two-line bullet on a slide, or any bullet running past two lines | -3 per slide |
| Major | >1 colored box on a slide | -3 per slide |
| Major | Notation inconsistency | -3 |
| Major | Unexpanded acronym on first appearance (profiles with `expand_acronyms`) | -2 each |
| Major | No callback to the previous session in the first three slides (`prior_session_callback`, `series_index` != 1) | -3 |
| Major | Dash expression in visible text: `---`, `--`, a literal em/en dash, or an `&mdash;`/`&ndash;` entity (`dash_lint`) | -2 each, cap 10 |
| Major | Third-party figure shown without its source on the slide (`attribution`) | -5 each, cap 20 |
| Minor | List nesting deeper than 1 sub-level | -1 per slide |

### Citations

Both citation scans (`\cite{key}` and Quarto's `@key`) read the deck source
with the contexts that cannot hold a citation removed: fenced and raw blocks,
`{{< >}}` shortcode calls and, for the Quarto scan, attribute blocks. That is
what keeps `## {.video-full video="@hook"}` from being read as a citation to
`hook` and billed -15 -- which it was, on every deck using the media pipeline
as documented. Speaker notes stay in scope: pandoc resolves citations there.

A deck may list keys the scan must skip anyway:

```yaml
citations:
  ignore:
    - some-at-form-this-repo-has-not-met
```

### Visible text

Every text check reads the same thing: the slide body outside fenced code
blocks, outside `::: {.notes}` divs, outside the YAML front matter and
outside HTML comments. A raw block (```` ```{=html} ````) is not a code
block: its content reaches the screen as written, so the dash lint, the
forbidden-term scan and the attribution check read it too (tags stripped,
`<style>`/`<script>` bodies blanked). The level-1 check does not read raw
blocks: a `# ` there is literal text, not a heading. The front-matter
`title:`/`subtitle:` are on the title slide and are scanned for forbidden
terms.

### Dash lint

Quarto's smart punctuation turns `---` into an em dash and `--` into an en
dash on render. The presenter writes a plain hyphen instead, everywhere. A
line that is only a rule (`---` slide break, a table delimiter row) and the
inside of display math are syntax, not text, and are not counted.

### Attribution

Only when `Figures/<genre>/<deck>/figures.yml` exists (a `figures.yml` next
to the qmd is accepted as a fallback, which is how the fixtures under
`Quarto/_fixtures/` carry one; absent file = check skipped silently). It is a
list under `figures:` of `{file, source, licence, third_party}`:

```yaml
figures:
  - file: helix-bedroom.jpg
    source: Figure AI
    licence: educational quotation
    third_party: true
  - file: scaling-curve.svg
    source: own work
    licence: repo
    third_party: false
```

Every slide that shows a `third_party: true` file (matched by basename, via
`![](..)`, `<img src>`, a `poster=`/`video=` attribute, a `background-image=`
header attribute, a `data-background-*`, or `{{< video >}}`) must contain the
entry's `source` string, case-insensitively, inside a `.footnote` div, a
`.video-caption` div, a figure caption (image alt text, `<figcaption>`) or a
`[..]{.footnote}` span. A manifest that exists but cannot be parsed is
reported as a missing attribution, not skipped.

## BLOCKERS

Two findings are not deductions. Any hit forces the score to **0**, the
status to `BLOCKED`, and a non-zero exit, and `--summary` prints every
`BLOCKER` line; the deck is either leaking or mis-rendering and nothing else
about it matters until that is fixed.

- **Forbidden term** (`forbidden_terms`). When `Quarto/<genre>/<deck>.forbidden.txt`
  exists, any term in it that appears in visible text is reported as
  `file:line` plus the term. File format: one term per line, `#` starts a
  comment, blank lines are ignored, matching is a case-insensitive substring
  match on visible text and the front-matter title, never on speaker notes.
  Seed it with internal project names, unpublished numbers, anything that
  must not reach a public page. Absent file = nothing to check.
- **Level-1 heading** (`level1_heading: fail`). Any line starting with `# `
  after the front matter (outside fences, raw blocks, notes and comments).
  Quarto turns a level-1 heading into a vertical stack and every following
  slide nests under it, so the deck's navigation and slide count silently
  change. Section dividers are written as `## {.divider}` (see
  `Quarto/_fixtures/design-test.qmd`). A deck that wants stacks on purpose
  sets, in its `deck.yml` (block form; `minyaml` reads no flow mappings):

  ```yaml
  checks:
    level1_heading: off
  ```

  The two legacy NVIDIA paper decks (DreamZero, DreamDojo) do.

## Per-profile defaults

What each shipped profile switches on (`checks:` in the profile yml; a deck
may override any key in its own `deck.yml`):

| Check | `paper-review` | `invited-talk` | `lecture` |
|-------|----------------|----------------|-----------|
| `expand_acronyms` | off | off | off (D17: the matcher cannot tell a model name from a term) |
| `prior_session_callback` | off | off | on |
| `dash_lint` | on | on | on |
| `attribution` | off (paper figures are quoted and cited in the text) | on | on |
| `forbidden_terms` | on | on | on |
| `level1_heading` | fail | fail | fail |
| `language.korean_allowance` | 0 | 0 | 300 |

`korean_allowance` is not a scorer check: the Korean pre-commit gate reads it
(`scripts/check-korean-pre-commit.sh`, run from `scripts/pre-commit.sh` after
the speaker-note gate) and blocks a staged deck qmd whose
Hangul character count, after the notes filter, exceeds it.

## Running it

Scoring renders the deck (that is the compile check), so it writes
`<deck>.html` and `<deck>_files` next to the qmd. `--no-render` skips both.
A render that does not finish inside `QUALITY_RENDER_TIMEOUT` seconds
(default 300) is reported as `INCONCLUSIVE`, not as a compilation failure:
the clock ran out, which says nothing about the deck. Exit stays 2, because
no score was produced.

## Enforcement

- **Any BLOCKER:** score 0, exit 1. Fix it first.
- **Score < 80:** Block commit. List blocking issues.
- **Score < 90:** Allow commit, warn. List recommendations.
- User can override with justification.

## Quality Reports

Merge-time quality reports: see `.claude/rules/session-logging.md`.
