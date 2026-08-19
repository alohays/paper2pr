# AGENTS.md -- Paper2PR: presentation framework

**Project:** Paper2PR
**Presenter:** Yunsung Lee
**Institution:** WoRV, MaumAI
**Branch:** main

---

## Core Principles

- **Plan first** -- enter plan mode before non-trivial tasks; save plans to `quality_reports/plans/`
- **Verify after** -- compile/render and confirm output at the end of every task
- **Single source of truth** -- Quarto `.qmd` is the only source; there is no other export format. Presentations are delivered from the rendered RevealJS HTML
- **Design principles** -- extreme minimalism, big type, centered content; see `.claude/rules/slide-design-principles.md` (mandatory for new decks)
- **Quality gates** -- nothing ships below 80/100
- **[LEARN] tags** -- when corrected, save `[LEARN:category] wrong → right` to MEMORY.md
- **English only** -- all content committed to git must be in English (see Language Policy below)

---

## Language Policy

**All content pushed to GitHub must be in English.** This includes documentation, session logs, commit messages, comments, and slide content.

**Exceptions:**
- `.claude/skills/` and `.claude/agents/` may contain Korean examples for bilingual functionality
- Speaker notes in QMD files are automatically stripped by the git clean filter (see Speaker Notes below)
- A deck that declares `language.slides: ko` in its own `<deck>.deck.yml`. That is the supported way to get Korean slides -- per deck, written on purpose. Do not add a path exemption for it; a directory exemption covers every future deck in that directory, including the ones that should stay English.

**Enforcement:**
- Pre-commit hook (`scripts/check-korean-pre-commit.sh`) blocks Korean text in staged files
- Exempt paths: `.claude/skills/`, `.claude/agents/`
- git runs a *copy* at `.git/hooks/pre-commit`. Editing the script does nothing until `bash scripts/setup-git-filters.sh` reinstalls it -- `scripts/test_korean_gate.sh` checks the two match before checking anything else

## Speaker Notes Policy

Speaker notes (`::: {.notes}` blocks in QMD) are **local-only** and never reach git:

1. **Git clean filter** strips notes from QMD before staging (`.gitattributes` + `scripts/strip_qmd_notes.py`)
2. **CI/CD pipeline** strips notes from HTML during GitHub Actions deployment (`scripts/strip_speaker_notes.py`)
3. **Backup/restore** via `python3 scripts/backup_notes.py backup|restore [Deck]`; backups land in `.speaker-notes/` (gitignored)
4. **Setup** (run once after clone): `bash scripts/setup-git-filters.sh`

```bash
./scripts/setup-git-filters.sh                 # one-time, after clone
python3 scripts/backup_notes.py backup DreamZero    # insurance against git checkout
python3 scripts/backup_notes.py restore DreamZero   # after clone or accidental checkout
```

- **Never maintain separate branches** for notes vs no-notes; the filter and CI strip are the only mechanism

---

## Project Scope

**Every presentation Yunsung gives is built here** -- paper reviews, invited talks, and course lectures. The name is historical; the repo is a framework, and it keeps the name because published slide URLs depend on it.

Decks live at `Quarto/<genre>/<name>.qmd`, where genre is one of the lines in `Quarto/_genres.txt`. A deck's figures, speaker-note backups, and presenter scripts are scoped the same way, so one rule finds everything a deck owns.

Each deck declares its own premises in `<deck>.deck.yml` -- who is listening, for how long, what they have already seen, which language the slides and notes are in. Those are not documentation. `quality_score.py` reads them to pick a bullet budget and decide which checks apply, and the Korean gate reads them to decide whether this deck may carry non-English slides. Start a deck with `/new-deck`, which interviews for exactly those answers.

| Genre | Profile | Audience | Length |
|-------|---------|----------|--------|
| `papers` | `paper-review` | knows deep learning | ~30 min |
| `talks` | `invited-talk` | varies, declare it | varies |
| `lectures` | `lecture` | no background | ~60 min |

Paper reviews: each paper is reviewed from its arXiv or PDF source, which the presenter supplies; nothing copyrighted is checked in. A review deck runs 40-60 slides (minimalist slides mean more, lighter slides; splitting beats packing) covering main ideas, technical details, and personal insight. When official code is available, include implementation-level observations.

## Slide Design Principles (new decks)

Shared core: `.claude/rules/slide-design-principles.md`. Per-genre budgets and extra checks: `.claude/rules/slide-profiles/<profile>.yml`. The short version of the core:

1. **Extreme minimalism** -- one idea per slide; ≤5 one-line bullets (≤3 with a figure), ≤1 colored box; a bullet that wraps to two lines costs a slot and only one is allowed per slide; split rather than pack
2. **Big type** -- 40px root font; `.smaller`/`.smallest` and font-size overrides are forbidden in new decks (quality gate deducts -5 each)
3. **Filled frame** -- title pinned at top, content centered vertically and horizontally (theme does this; escape hatches: `{.top-align}`, `{.left}`, `{.statement}`)
4. **Slide types** -- dividers, full-bleed video, inline video, charts, formula legends, timelines are theme classes, not hand-built layouts; see the Quarto CSS Classes table below and `Quarto/_fixtures/design-test.qmd` for a rendered example of each

New decks use `clean-academic.scss` with `center: false` and `auto-stretch: false`. Legacy decks (DreamZero, DreamDojo, RoboTTT) are pinned to `clean-academic-legacy.scss` and exempt from the new rules.

## Folder Structure

```
paper2pr/
├── AGENTS.md                    # Canonical agent instructions for this repo
├── .claude/                     # Rules, skills, agents, hooks
├── Bibliography_base.bib        # Centralized bibliography (grows per paper)
├── Figures/<genre>/<deck>/      # Per-deck figures, SVG/PNG only
├── Quarto/
│   ├── _genres.txt              # Which directories publish. Single source of truth
│   ├── _quarto.yml              # Project defaults for every deck (canvas, filter, fonts)
│   ├── _filters/slide-types.lua # .divider / .video-full -> reveal background attributes
│   ├── clean-academic*.scss     # Shared themes (main + legacy)
│   ├── fonts/                   # Pretendard (Hangul fallback), linked by _quarto.yml
│   ├── _widgets/ _script/       # Shared includes; presenter scripts (gitignored)
│   ├── _fixtures/               # design-test.qmd + theme-mockups/ -- not a genre, never published
│   └── <genre>/                 # <deck>.qmd + <deck>.deck.yml + per-deck assets
├── .speaker-notes/<genre>/      # Note backups (gitignored -- notes never enter git)
├── pages/index.html             # Landing page, GENERATED by scripts/build_landing.py
├── scripts/                     # Utility scripts. Python here is stdlib-only
│                                #   on purpose -- see scripts/minyaml.py
├── quality_reports/             # Plans, session logs, merge reports (history, never edited)
└── templates/                   # Session log and speaker-notes report templates
```

---

## Commands

```bash
# Start a new deck (interviews for the premises, then scaffolds)
/new-deck

# Quarto render (primary workflow -- decks are authored and delivered in Quarto)
quarto render Quarto/<genre>/<Deck>.qmd

# Where does this deck keep its things? (bare name resolves the genre)
python3 scripts/deckpath.py <Deck> --field figures --relative
python3 scripts/deckpath.py --list

# What is this deck graded against?
python3 scripts/deckprofile.py <Deck>

# Deploy to GitHub Pages (automatic via CI/CD on push to main)
git push  # GitHub Actions renders Quarto, strips notes, deploys

# Local deploy preview -- renders, assembles exactly as CI does, then checks assets
./scripts/sync_to_docs.sh [Deck]

# Regression tests
bash scripts/test_note_filter.sh    # the note filter still covers every depth
python3 scripts/test_profiles.py    # the profiles still grade differently
python3 scripts/test_minyaml.py     # the config parser still agrees with PyYAML
bash scripts/test_korean_gate.sh    # the Korean gate still blocks, and still exempts

# Quality score
python scripts/quality_score.py Quarto/<genre>/<Deck>.qmd

# Theme fixture: one slide per layout rule and slide type (outside the Quarto project,
# so it repeats the _quarto.yml defaults itself)
cd Quarto/_fixtures && quarto render design-test.qmd
```

---

## Quality Thresholds

| Score | Gate | Meaning |
|-------|------|---------|
| 80 | Commit | Good enough to save |
| 90 | PR | Ready for deployment |
| 95 | Excellence | Aspirational |

---

## Skills Quick Reference

| Command | What It Does |
|---------|-------------|
| `/new-deck [topic]` | Interview a new deck's premises, scaffold it, and carry authoring through the quality gate (the single entry point) |
| `/deploy [Deck]` | Render Quarto + deploy (CI/CD on push) |
| `/slide-excellence [Deck]` | The one review fan-out: slide-auditor + pedagogy-reviewer + proofreader (grammar, overflow, narrative, design challenge), one report per agent |
| `/visual-audit [Deck]` | Standalone adversarial layout audit (density, overflow, font, box fatigue, centering) |
| `/write-speaker-notes [Deck] [--lang en\|ko]` | Generate presentation script (speaker notes) for Quarto slides |
| `/validate-bib` | Cross-reference citations against `Bibliography_base.bib` |
| `/commit [msg]` | Stage, commit, PR, merge |
| `/learn [skill-name]` | Extract discovery into persistent skill |
| `/context-status` | Show session health + context usage |
| `/deep-audit` | Repository-wide consistency audit |

---

## Quarto CSS Classes

| Class | Effect | Use Case |
|-------|--------|----------|
| `.primaryblue` | Primary blue text | Headings, emphasis |
| `.primarygold` | Gold text | Secondary emphasis |
| `.primaryyellow` | Yellow text | Highlight markers |
| `.hi` | Bold primary blue | Inline key terms |
| `.hi-gold` | Bold gold | Inline secondary emphasis |
| `.hi-green` | Bold green | Positive results |
| `.hi-red` | Bold red | Negative results, limitations |
| `.positive` | Green + bold | Good outcomes in comparisons |
| `.negative` | Red + bold | Bad outcomes, limitations |
| `.neutral` | Gray | Context, reference values |
| `.compact` | Tighter spacing | Lists needing more items |
| `.footnote` | Bottom-positioned small text | Source attributions |
| `.methodbox` | Blue-bordered div | Technical details |
| `.keybox` | Gold-bordered div | Key insights |
| `.highlightbox` | Yellow-bordered div | Notable findings |
| `.resultbox` | Gold-bordered with shadow | Main results |
| `## {.divider}` | Navy full-bleed chapter block; `.divider-number` / `.divider-title` / `.divider-sub` stack | Section breaks |
| `## {.video-full video=".." poster=".."}` + `.video-caption` | Clip as the slide background (looped, muted, cover), slide chrome hidden, caption strip at the bottom | Hook clips, montages |
| `.video-inline` | 16:9 clip inside a normal content slide | A demo next to bullets |
| `figure.chart-figure` | Inline SVG chart at 64% width, bullets a notch smaller | One chart plus takeaways |
| `.formula-legend` | Centered symbol list under a 2em display formula | Hero equation slides |
| `.gloss` | Small gray line pinned to the bottom of the content area | Korean or plain-language gloss of a term |
| `.timeline` | `.tl-item` grid on a gold rail: one row up to six items, two rows of four from seven | Dated milestones |

`.smaller` and `.smallest` still exist in the theme for the legacy decks only; they are forbidden in new decks (quality gate deducts -5 each). `.divider` and `.video-full` get their full-bleed backgrounds from `Quarto/_filters/slide-types.lua`, which turns the class and its `video=` / `poster=` attributes into reveal `data-background-*` attributes; `Quarto/_quarto.yml` wires the filter for every deck under a genre directory. Each slide type has a rendered example in `Quarto/_fixtures/design-test.qmd`.

---

## Current Project State

| Deck | Quarto (source) | Theme | Key Content |
|------|-----------------|-------|-------------|
| DreamZero | `papers/DreamZero.qmd` | legacy | NVIDIA - World Action Models as Zero-shot Policies |
| DreamDojo | `papers/DreamDojo.qmd` | legacy | NVIDIA - A Generalist Robot World Model from Large-Scale Human Videos |
| RoboTTT | `papers/RoboTTT.qmd` | legacy | NVIDIA GEAR - Context Scaling for Robot Policies (PR-561) |
| SUNY Career Sprint | `talks/SUNY.qmd` | own (suny-career) | Career Roadmap for AI Researchers: From Papers to Products (April 4, 2026) |

New decks: main theme (`clean-academic.scss`) + `.claude/rules/slide-design-principles.md`. "legacy" = pinned to `clean-academic-legacy.scss`, exempt from the design principles.
