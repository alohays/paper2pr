# Paper2PR

A Claude Code multi-agent workflow that converts AI/ML papers into presentation-ready Beamer + Quarto (RevealJS) slide decks with automated quality control, adversarial review, and deployment.

**Organization:** WoRV / MaumAI

---

## Papers

| Paper | Topic | Beamer | Quarto |
|-------|-------|--------|--------|
| DreamZero | World Action Models as Zero-shot Policies (NVIDIA) | [`Slides/DreamZero.tex`](Slides/DreamZero.tex) | [`Quarto/DreamZero.qmd`](Quarto/DreamZero.qmd) |

Each paper gets a ~30-slide deck (~30 min) covering main ideas, technical details, and implementation observations. Target audience: basic deep learning knowledge.

---

## Quick Start

### Prerequisites

- [Claude Code](https://code.claude.com/docs/en/overview)
- XeLaTeX ([TeX Live](https://tug.org/texlive/) / [MacTeX](https://tug.org/mactex/))
- [Quarto](https://quarto.org)

### Build

```bash
# Beamer (3-pass XeLaTeX)
cd Slides
TEXINPUTS=../Preambles:$TEXINPUTS xelatex -interaction=nonstopmode DreamZero.tex
BIBINPUTS=..:$BIBINPUTS bibtex DreamZero
TEXINPUTS=../Preambles:$TEXINPUTS xelatex -interaction=nonstopmode DreamZero.tex
TEXINPUTS=../Preambles:$TEXINPUTS xelatex -interaction=nonstopmode DreamZero.tex

# Quarto
cd Quarto && quarto render DreamZero.qmd

# Deploy to GitHub Pages
./scripts/sync_to_docs.sh DreamZero
```

### With Claude Code

```bash
claude
```

Then use skills like `/create-lecture`, `/translate-to-quarto`, `/slide-excellence`, `/deploy`.

---

## Project Structure

```
paper2pr/
├── CLAUDE.md                    # Project config for Claude Code
├── target-papers/               # Source papers (gitignored)
│   └── YYMM-papername/
│       ├── paper/               # LaTeX source, figures, bib
│       └── code/                # Official implementation
├── Bibliography_base.bib        # Centralized bibliography
├── Figures/                     # Per-paper subdirectories (PDF + SVG)
├── Preambles/header.tex         # Shared Beamer preamble
├── Slides/                      # Beamer .tex + compiled .pdf
├── Quarto/                      # RevealJS .qmd + theme
├── docs/                        # GitHub Pages (auto-generated)
├── scripts/                     # Build & deploy utilities
├── quality_reports/             # Plans, session logs, audit reports
├── guide/                       # Workflow guide (from upstream)
└── .claude/                     # Agents, skills, rules, hooks
```

---

## Workflow

This project uses a multi-agent Claude Code workflow:

- **10 specialized agents** — proofreader, slide-auditor, pedagogy-reviewer, domain-reviewer, tikz-reviewer, beamer-translator, quarto-critic, quarto-fixer, verifier, r-reviewer
- **Adversarial QA** — critic and fixer agents loop until approved (max 5 rounds)
- **Quality gates** — 80 (commit) / 90 (PR) / 95 (excellence)
- **Plan-first** — enter plan mode before non-trivial tasks
- **Context survival** — plans and session logs persist across compression

### Key Skills

| Command | What It Does |
|---------|-------------|
| `/create-lecture` | Full lecture creation from paper |
| `/translate-to-quarto` | Beamer → Quarto translation |
| `/slide-excellence` | Combined multi-agent review |
| `/compile-latex` | 3-pass XeLaTeX + bibtex |
| `/deploy` | Render Quarto + sync to docs/ |
| `/qa-quarto` | Adversarial Quarto vs Beamer QA |
| `/proofread` | Grammar/typo/overflow review |
| `/visual-audit` | Slide layout audit |

See [CLAUDE.md](CLAUDE.md) for the full skill reference.

---

## Attribution

This project is built on [**claude-code-my-workflow**](https://github.com/pedrohcgs/claude-code-my-workflow) by [Pedro H. C. Sant'Anna](https://github.com/pedrohcgs), originally developed for Econ 730 at Emory University. The multi-agent architecture, quality gates, orchestrator protocol, and infrastructure (agents, skills, rules, hooks) are from that foundation.

Thank you for making it open source.

---

## License

MIT License. See [LICENSE](LICENSE).
