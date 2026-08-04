---
name: translate-to-quarto
description: "LEGACY IMPORT — translate an existing Beamer LaTeX deck to Quarto RevealJS. New decks are authored directly in Quarto (see /new-deck); use this only to import a pre-existing .tex deck."
argument-hint: "[PaperName.tex]"
allowed-tools: ["Read", "Grep", "Glob", "Write", "Edit", "Bash", "Task"]
context: fork
---

# Beamer → Quarto Translation Workflow (Legacy Import)

Full translation of a pre-existing Beamer LaTeX deck to Quarto RevealJS HTML
slides.

**Since 2026-07 Quarto is the project's source of truth** — new decks are
authored directly in Quarto and this skill is only for importing legacy
Beamer decks. During the translation itself the Beamer .tex is treated as
the content source; after import, the QMD becomes authoritative and the
.tex is marked legacy/frozen in `.claude/rules/beamer-quarto-sync.md`.

Imported decks join the new design system, so target the main theme and
`.claude/rules/slide-design-principles.md` — split any frame that exceeds
the density budget rather than shrinking type.

---

## Phase 0: Pre-Flight Checks

### 0A. Environment Parity Audit
Scan Beamer for all custom environments. Verify CSS equivalents exist in your theme SCSS. If any are missing, create them FIRST.

### 0B. TikZ Freshness Verification
Run `/extract-tikz` to verify SVGs match current Beamer source.

### 0C. RDS Data Inventory
List all RDS files needed for interactive charts.

### 0D. Citation Key Mapping
Extract all citations from Beamer, map to bibliography keys.

## Phase 1: Pre-Translation Preparation
- Read complete Beamer source, count frames
- Inventory figures (TikZ → SVG, R plots → plotly, other → SVG)

## Phase 2: Create QMD File with YAML Header
- Standard RevealJS YAML with theme, logo, footer, bibliography
- Setup chunk for R data loading if needed

## Phase 3: Slide-by-Slide Translation
- Delegate to `beamer-translator` agent
- 1:1 frame-to-slide mapping
- Verbatim math, environment parity, no font reduction

## Phase 4: TikZ Diagram Integration
Reference extracted SVGs with 0-based indexing.

## Phase 5: R Figure Integration (Plotly-First)
Interactive plotly from RDS data, static SVG for TikZ/complex figures.

## Phase 6: First Render & Content Fidelity Check
Render, count slides, go through EVERY slide checking for issues.

## Phase 6.5: Pedagogical Review
Run pedagogy-reviewer before visual polish.

## Phase 7: Visual Polish
Semantic colors, transition slides, framing sentences.

## Phase 8: Proofreading
Run `/proofread` on the QMD file.

## Phase 9: Final Verification & Deployment
Render, open in browser, verify all elements.

## Phase 10: Handoff of Authority
Mark the .tex as legacy/frozen in the deck inventory
(`.claude/rules/beamer-quarto-sync.md`). From here on the QMD is the
source of truth; corrections found during QA go into the QMD only.

## Phase 11: Documentation
Update CLAUDE.md, session log, create PR.
