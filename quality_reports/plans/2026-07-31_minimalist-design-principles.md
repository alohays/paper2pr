# Plan: Embed Minimalist Design Principles + Quarto-First Pivot

**Date:** 2026-07-31
**Status:** COMPLETED (all 5 steps done and verified; see session log of the same date)
**Scope:** Full infrastructure — theme SCSS, rules, agents, skills, quality gate, AGENTS.md

---

## The Three Principles (user directive)

1. **Extreme minimalism** — never pack much content onto one slide.
2. **Bigger type than feels natural** — never shrink fonts to cram text into blocks.
3. **Center main content under the title** — vertically and horizontally, so the
   presentation screen feels full.

## Decisions from Q&A

| Topic | Decision |
|-------|----------|
| Scope | Full infra: theme + rules/agents/skills + quality_score.py + AGENTS.md |
| Source of truth | **Quarto becomes primary going forward.** Beamer demoted to optional export (files/skills kept, rules rewritten) |
| Vertical centering | Title (h2) fixed at top; body content centered in remaining space |
| Horizontal centering | Element-wise: figures/tables/math/short statements fully centered; bullet lists block-centered with left-aligned text |
| Root font size | 30px → **40px** (Quarto RevealJS default) |
| .smaller/.smallest | Kept for legacy compatibility; forbidden in new slides; quality deduction -1 → -5; overflow must be solved by splitting slides |
| Density budget (moderate) | ≤5 bullets/slide (each ≤2 lines), ≤1 colored box/slide, with a figure present ≤3 bullets, nesting ≤1 level |
| Slide count | 40–60 slides allowed for a ~30 min talk (split > cut) |
| Existing decks | Pin DreamZero/DreamDojo/RoboTTT to a legacy snapshot of the current theme; new principles go into the main theme. SUNY has its own theme — untouched |
| Commits | Commit incrementally in logical units; **no push** |

## Steps

1. **Legacy pinning** — snapshot `Quarto/clean-academic.scss` →
   `Quarto/clean-academic-legacy.scss`; point DreamZero/DreamDojo/RoboTTT at the
   legacy file; render-verify one legacy deck. Commit.
2. **New main theme** — rewrite `clean-academic.scss`: 40px root,
   title-fixed + content-centered flex layout, element-wise horizontal centering,
   spacing retuned for large type. Verify with a test deck render + browser
   screenshots. Commit.
3. **Rules & agents** — new `.claude/rules/slide-design-principles.md`;
   rewrite `single-source-of-truth.md` and `beamer-quarto-sync.md` for
   Quarto-first; update `quality-gates.md`; flip slide-auditor/visual-audit from
   spacing-first to split-first; retag translate-to-quarto/create-lecture/qa-quarto
   as legacy-direction workflows. Commit.
4. **Quality gate** — `scripts/quality_score.py`: font-reduction penalty 1→5,
   add density checks (bullets/boxes per slide). Verify by scoring a deck. Commit.
5. **Docs & memory** — AGENTS.md (principles, Quarto-first, slide-count range,
   legacy-theme note), session log, auto-memory update. Commit.

## Verification

- `quarto render` of a legacy deck (unchanged output) and a test deck on the new
  theme (centering + type scale verified via browser screenshots).
- `python scripts/quality_score.py` runs clean with new checks.
