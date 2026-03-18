# AGENTS.md -- Paper2PR: AI/ML Paper Review Presentations

**Project:** Paper2PR
**Presenter:** Yunsung Lee
**Institution:** WoRV, MaumAI
**Branch:** main

---

## Core Principles

- **Plan first** -- enter plan mode before non-trivial tasks; save plans to `quality_reports/plans/`
- **Verify after** -- compile/render and confirm output at the end of every task
- **Single source of truth** -- Beamer `.tex` is authoritative; Quarto `.qmd` derives from it
- **Quality gates** -- nothing ships below 80/100
- **[LEARN] tags** -- when corrected, save `[LEARN:category] wrong → right` to MEMORY.md
- **English only** -- all content committed to git must be in English (see Language Policy below)

---

## Language Policy

**All content pushed to GitHub must be in English.** This includes documentation, session logs, commit messages, comments, and slide content.

**Exceptions:**
- `.claude/skills/` and `.claude/agents/` may contain Korean examples for bilingual functionality
- Speaker notes in QMD files are automatically stripped by the git clean filter (see Speaker Notes below)

**Enforcement:**
- Pre-commit hook (`scripts/check-korean-pre-commit.sh`) blocks Korean text in staged files
- Exempt paths: `.claude/skills/`, `.claude/agents/`

## Speaker Notes Policy

Speaker notes (`::: {.notes}` blocks in QMD) are **local-only** and never reach git:

1. **Git clean filter** strips notes from QMD before staging (`.gitattributes` + `scripts/strip_qmd_notes.py`)
2. **CI/CD pipeline** strips notes from HTML during GitHub Actions deployment (`scripts/strip_speaker_notes.py`)
3. **Backup/restore** via `python3 scripts/backup_notes.py backup|restore [PaperName]`
4. **Setup** (run once after clone): `bash scripts/setup-git-filters.sh`

---

## Project Scope

Ongoing multi-paper review project. Each paper in `target-papers/` gets its own slide deck (30-40 slides, ~30 min). Target audience: basic deep learning knowledge. Presentations cover main ideas, technical details, and personal insights. When official code is available, include implementation-level observations.

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
├── Figures/                     # Per-paper subdirectories
│   └── PaperName/               # PDF (Beamer) + SVG (Quarto)
├── Preambles/header.tex         # Shared Beamer preamble
├── Slides/                      # Beamer .tex files (one per paper)
├── Quarto/                      # RevealJS .qmd files + theme
├── pages/                       # Landing page source (deployed via CI/CD)
├── scripts/                     # Utility scripts
├── quality_reports/             # Plans, session logs, merge reports
├── explorations/                # Research sandbox
└── templates/                   # Session log, quality report templates
```

---

## Commands

```bash
# LaTeX (3-pass, XeLaTeX only)
cd Slides && TEXINPUTS=../Preambles:$TEXINPUTS xelatex -interaction=nonstopmode PaperName.tex
BIBINPUTS=..:$BIBINPUTS bibtex PaperName
TEXINPUTS=../Preambles:$TEXINPUTS xelatex -interaction=nonstopmode PaperName.tex
TEXINPUTS=../Preambles:$TEXINPUTS xelatex -interaction=nonstopmode PaperName.tex

# Quarto render
cd Quarto && quarto render PaperName.qmd

# Deploy to GitHub Pages (automatic via CI/CD on push to main)
git push  # GitHub Actions renders Quarto, strips notes, deploys

# Local deploy preview (optional, for testing before push)
./scripts/sync_to_docs.sh PaperName

# Quality score
python scripts/quality_score.py Quarto/PaperName.qmd
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
| `/qa-quarto [PaperName]` | Adversarial Quarto vs Beamer QA |
| `/slide-excellence [file]` | Combined multi-agent review |
| `/translate-to-quarto [file]` | Beamer → Quarto translation |
| `/validate-bib` | Cross-reference citations |
| `/devils-advocate` | Challenge slide design |
| `/create-lecture` | Full lecture creation |
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
| `/write-speaker-notes [PaperName] [--lang en\|ko]` | Generate presentation script (speaker notes) for Quarto slides |
| `/deep-audit` | Repository-wide consistency audit |

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

## Current Project State

| Paper | Beamer | Quarto | Key Content |
|-------|--------|--------|-------------|
| DreamZero | `DreamZero.tex` | `DreamZero.qmd` | NVIDIA — World Action Models as Zero-shot Policies |
| DreamDojo | `DreamDojo.tex` | `DreamDojo.qmd` | NVIDIA — A Generalist Robot World Model from Large-Scale Human Videos |
