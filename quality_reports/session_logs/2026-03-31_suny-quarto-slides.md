# Session Log: SUNY Career Sprint 2026 — Quarto Slides from Vault

**Date:** 2026-03-31
**Goal:** Convert 62 polished HTML slides from vault into Quarto RevealJS format for paper2pr project
**Status:** COMPLETE

---

## Key Context

- **Source:** `/Users/iyunseong/Documents/vault/1-projects/personal/suny-career-sprint-2026/` — 62 custom HTML slides with navy/gold executive theme
- **Target:** Quarto RevealJS presentation at `Quarto/SUNY.qmd`
- **Event:** SUNY Korea IGC STEM Career Connect, April 4, 2026
- **This is NOT a paper review** — career guidance talk, Beamer rules don't apply

## Approach

Ralplan consensus planning (Planner → Architect → Critic, 2 iterations) established:
- **Full HTML embed** with ID-scoped CSS (`#sNN` selectors) — all 62 slides have complex bespoke CSS
- **Viewport 960×540** matching vault's 720pt × 405pt — zero dimension scaling
- **tinycss2-based preprocessing script** (`prefix_slide_css.py`) for automated conversion
- **Self-hosted fonts** (Pretendard woff2 + Instrument Serif TTF)

## User Decisions (9 locked)

| Decision | Choice |
|----------|--------|
| Timeline | Start immediately |
| Korean text | Translate to English |
| Videos | Git LFS + poster fallback |
| Quality gate | 90/100 |
| Font deploy | sync_to_docs.sh modification |
| Slide titles | `## Title` + remove HTML `<h1>` |
| Asset scope | 11 referenced files only |
| CSS isolation | `#sNN` ID-scoped selectors |
| Viewport | 960×540 |

## Artifacts Created

| File | Lines | Purpose |
|------|-------|---------|
| `Quarto/SUNY.qmd` | 7,354 | 62-slide career talk presentation |
| `Quarto/suny-career.scss` | 631 | Navy/gold RevealJS theme |
| `Quarto/suny-theme-compat.css` | 101 | Theme.css rewritten for RevealJS |
| `scripts/prefix_slide_css.py` | 411 | HTML→QMD preprocessing script |
| `Quarto/fonts/` | 10 files | Self-hosted Pretendard + Instrument Serif |
| `Figures/SUNY/` | 11+4 files | 6 images + 1 vendor JS + 4 videos (LFS) + 4 posters |

## Verification

- Quarto render: exits code 0, 63 sections, 316KB HTML
- CSS isolation: 0 unprefixed selectors across 7,354 lines
- Background split: 35 dark + 23 light + 4 deep navy = 62 slides
- All image/video paths resolve, poster fallbacks work
- 62 speaker notes from slide-outline.md
- No Korean text in committed files
- Architect review: APPROVED
- Deslop pass: prefix_slide_css.py reduced 581→411 lines (29%)
- Quality score: 100/100 (all 16 criteria passed)

## Learnings

- [LEARN:quarto] Full HTML embed in Quarto RevealJS works well — use `#sNN` ID-scoped CSS for isolation when embedding multiple bespoke HTML slides
- [LEARN:workflow] tinycss2 is the right tool for CSS selector prefixing — regex fails on minified CSS and pseudo-elements
- [LEARN:viewport] Match vault dimensions exactly (960×540 = 720pt×405pt) to avoid dimension scaling — simpler than converting all CSS values
- [LEARN:theme] When porting theme.css with `body.deck-slide` selectors to RevealJS, rewrite to `.suny-slide` wrapper class
