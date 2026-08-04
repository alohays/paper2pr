# AGENTS.md -- Paper2PR: presentation framework

**Project:** Paper2PR
**Presenter:** Yunsung Lee
**Institution:** WoRV, MaumAI
**Branch:** main

---

## Core Principles

- **Plan first** -- enter plan mode before non-trivial tasks; save plans to `quality_reports/plans/`
- **Verify after** -- compile/render and confirm output at the end of every task
- **Single source of truth** -- Quarto `.qmd` is authoritative; Beamer `.tex` is an optional export (reversed 2026-07 — presentations are delivered from Quarto)
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
3. **Backup/restore** via `python3 scripts/backup_notes.py backup|restore [PaperName]`
4. **Setup** (run once after clone): `bash scripts/setup-git-filters.sh`

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

Paper reviews: each paper in `target-papers/` gets a deck (40-60 slides — minimalist slides mean more, lighter slides; splitting beats packing) covering main ideas, technical details, and personal insight. When official code is available, include implementation-level observations.

## Slide Design Principles (new decks)

Shared core: `.claude/rules/slide-design-principles.md`. Per-genre budgets and extra checks: `.claude/rules/slide-profiles/<profile>.yml`. The short version of the core:

1. **Extreme minimalism** -- one idea per slide; ≤5 one-line bullets (≤3 with a figure), ≤1 colored box; a bullet that wraps to two lines costs a slot and only one is allowed per slide; split rather than pack
2. **Big type** -- 40px root font; `.smaller`/`.smallest` and font-size overrides are forbidden in new decks (quality gate deducts -5 each)
3. **Filled frame** -- title pinned at top, content centered vertically and horizontally (theme does this; escape hatches: `{.top-align}`, `{.left}`, `{.statement}`)

New decks use `clean-academic.scss` with `center: false` and `auto-stretch: false`. Legacy decks (DreamZero, DreamDojo, RoboTTT) are pinned to `clean-academic-legacy.scss` and exempt from the new rules.

## Folder Structure

```
paper2pr/
├── AGENTS.md                    # Canonical agent instructions for this repo
├── .claude/                     # Rules, skills, agents, hooks
├── target-papers/               # Source papers (paper/ + code/ per entry)
│   └── YYMM-papername/
│       ├── paper/               # LaTeX source, figures, bib
│       └── code/                # Official implementation (if available)
├── Bibliography_base.bib        # Centralized bibliography (grows per paper)
├── Figures/<genre>/<deck>/      # PDF (Beamer) + SVG (Quarto)
├── Preambles/header.tex         # Shared Beamer preamble
├── Slides/                      # Beamer .tex files (optional export)
├── Quarto/
│   ├── _genres.txt              # Which directories publish. Single source of truth
│   ├── clean-academic*.scss     # Shared themes
│   ├── _widgets/ _script/       # Shared includes; presenter scripts (gitignored)
│   ├── _fixtures/               # design-test.qmd -- not a genre, never published
│   └── <genre>/                 # <deck>.qmd + <deck>.deck.yml + per-deck assets
├── .speaker-notes/<genre>/      # Note backups (gitignored -- notes never enter git)
├── pages/index.html             # Landing page, GENERATED by scripts/build_landing.py
├── scripts/                     # Utility scripts. Python here is stdlib-only
│                                #   on purpose -- see scripts/minyaml.py
├── quality_reports/             # Plans, session logs, merge reports
├── explorations/                # Research sandbox
└── templates/                   # Session log, quality report templates
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

# LaTeX (optional Beamer export only; 3-pass, XeLaTeX)
cd Slides && TEXINPUTS=../Preambles:$TEXINPUTS xelatex -interaction=nonstopmode PaperName.tex
BIBINPUTS=..:$BIBINPUTS bibtex PaperName
TEXINPUTS=../Preambles:$TEXINPUTS xelatex -interaction=nonstopmode PaperName.tex
TEXINPUTS=../Preambles:$TEXINPUTS xelatex -interaction=nonstopmode PaperName.tex

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

# Optional tools (install via: bash scripts/setup-optional-tools.sh --all)
diff-pdf old.pdf new.pdf                    # Visual PDF regression test
diff-pdf --output-diff=diff.pdf old.pdf new.pdf  # Save diff as PDF
tex-fmt --check Slides/PaperName.tex        # Check LaTeX formatting
tex-fmt Slides/PaperName.tex                # Format LaTeX in-place
chktex -q Slides/PaperName.tex              # LaTeX semantic lint (advisory)
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
| `/compile-latex [file]` | 3-pass XeLaTeX + bibtex |
| `/deploy [PaperName]` | Render Quarto + deploy (CI/CD on push) |
| `/proofread [file]` | Grammar/typo/overflow review |
| `/visual-audit [file]` | Slide layout audit |
| `/pedagogy-review [file]` | Narrative, notation, pacing review |
| `/qa-quarto [PaperName]` | Adversarial Quarto vs Beamer QA (imported decks only) |
| `/slide-excellence [file]` | Combined multi-agent review |
| `/translate-to-quarto [file]` | Beamer → Quarto import (legacy decks only) |
| `/validate-bib` | Cross-reference citations |
| `/devils-advocate` | Challenge slide design |
| `/new-deck [topic]` | Interview, scaffold, and author a new deck of any genre |
| `/commit [msg]` | Stage, commit, PR, merge |
| `/review-paper [file]` | Manuscript review |
| `/data-analysis [dataset]` | End-to-end R data analysis workflow |
| `/extract-tikz [PaperName]` | Extract TikZ diagrams → PDF → SVG |
| `/interview-me [topic]` | Interactive interview to formalize research idea |
| `/lit-review [topic]` | Structured literature search and synthesis |
| `/research-ideation [topic]` | Generate research questions and strategies |
| `/review-r [file]` | R code review for quality and reproducibility |
| `/learn [skill-name]` | Extract discovery into persistent skill |
| `/context-status` | Show session health + context usage |
| `/write-speaker-notes [Deck] [--lang en\|ko]` | Generate presentation script (speaker notes) for Quarto slides |
| `/new-deck [topic]` | Interview a new deck's premises, then scaffold it |
| `/deep-audit` | Repository-wide consistency audit |
| `/pdf-diff [PaperName] [branch]` | Visual PDF regression test vs baseline |

---

## Beamer Custom Environments

| Environment | Effect | Use Case |
|-------------|--------|----------|
| `methodbox` | Blue-bordered box | Technical details, architecture descriptions |
| `keybox` | Gold-bordered box | Key insights, important takeaways |
| `highlightbox` | Yellow-bordered box | Notable findings, emphasis points |
| `assumptionbox` | Gold full-border box | Assumptions, hypotheses |
| `quotebox` | Italic with quote mark | Direct quotes from papers |
| `resultbox` | Gold-bordered with shadow | Main experimental results |
| `eqbox` | Subtle blue background | Key equations |
| `softbox` | Subtle gold italic | Side remarks, intuition |

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
| `.smaller` | 85% font size | Dense content slides |
| `.smallest` | 80% font size | Very dense content |
| `.compact` | Tighter spacing | Lists needing more items |
| `.footnote` | Bottom-positioned small text | Source attributions |
| `.methodbox` | Blue-bordered div | Technical details |
| `.keybox` | Gold-bordered div | Key insights |
| `.highlightbox` | Yellow-bordered div | Notable findings |
| `.resultbox` | Gold-bordered with shadow | Main results |

---

## Speaker Notes Policy

Speaker notes (`::: {.notes}`) live in the working directory QMD only. Two layers of protection:

| Layer | What | How |
|-------|------|-----|
| **Git** | QMD committed without notes | `git clean filter` via `.gitattributes` |
| **Deploy** | HTML deployed without notes | `strip_speaker_notes.py` via GitHub Actions CI/CD |

```bash
# One-time setup (after clone)
./scripts/setup-git-filters.sh

# Backup notes (insurance against git checkout)
python3 scripts/backup_notes.py backup DreamZero

# Restore notes (after clone or accidental checkout)
python3 scripts/backup_notes.py restore DreamZero
```

- **Never maintain separate branches** for notes vs no-notes
- Notes backup: `.speaker-notes/` (gitignored)

---

## ClawTeam Multi-Agent Coordination (Optional, Experimental)

[ClawTeam](https://github.com/HKUDS/ClawTeam) (v0.2.0) is a multi-agent coordination CLI that spawns AI agents in tmux panes with inter-agent messaging and task management. It is available for ad-hoc experimentation but **not integrated into standard workflows** -- existing skills (`/slide-excellence`, `/qa-quarto`, etc.) remain the primary multi-agent approach.

**What it offers:** True OS-level process parallelism (each agent gets its own context window), visual tmux monitoring, git worktree workspace isolation per agent.

**Why not deeply integrated yet:** ClawTeam v0.2.0 templates require inline prompts (no `prompt_file` support), which would duplicate agent definitions from `.claude/agents/` and violate Single Source of Truth. Revisit when ClawTeam supports external prompt file references.

```bash
# Ad-hoc usage examples
clawteam spawn claude -t review -n auditor --task "Review Slides/SUNY.tex for visual overflow"
clawteam spawn claude -t review -n pedagogy --task "Check narrative arc in Slides/SUNY.tex"
clawteam board show review              # Kanban view of team tasks
clawteam inbox send review auditor "Check slide 15 font size"
clawteam team status review             # Team member status

# Built-in templates (generic, not paper2pr-specific)
clawteam template list                  # hedge-fund, software-dev, research-paper, code-review, strategy-room
clawteam launch research-paper          # Launch a pre-configured research team
```

---

## Current Project State

| Paper | Quarto (source) | Theme | Beamer | Key Content |
|-------|-----------------|-------|--------|-------------|
| DreamZero | `DreamZero.qmd` | legacy | `DreamZero.tex` (frozen) | NVIDIA — World Action Models as Zero-shot Policies |
| DreamDojo | `DreamDojo.qmd` | legacy | `DreamDojo.tex` (frozen) | NVIDIA — A Generalist Robot World Model from Large-Scale Human Videos |
| RoboTTT | `RoboTTT.qmd` | legacy | none | NVIDIA GEAR — Context Scaling for Robot Policies (PR-561) |
| SUNY Career Sprint | `SUNY.qmd` | own (suny-career) | none (career talk) | Career Roadmap for AI Researchers: From Papers to Products (April 4, 2026) |

New decks: main theme (`clean-academic.scss`) + `.claude/rules/slide-design-principles.md`. "legacy" = pinned to `clean-academic-legacy.scss`, exempt from the design principles.
