# SUNY Multi-LLM Visual QA Report

**Date:** 2026-03-26
**Models:** Claude Opus 4.6, Codex GPT-5.4, Gemini 2.5/3.1 Pro
**Scope:** All 12 standalone TikZ diagrams + 3 PNGs + 2 inline-only TikZ
**Method:** Screenshot-based multimodal evaluation via /ccg tri-model orchestration

---

## Summary

| Severity | Count | Status |
|----------|-------|--------|
| CRITICAL | 1 figure (3 sub-issues) | Needs fix |
| MAJOR | 4 figures (6 sub-issues) | Needs fix |
| MINOR | 4 sub-issues across 3 figures | Nice to fix |
| PASS | 7 figures (confirmed by all 3 LLMs) | No action |

---

## CRITICAL Issues

### 1. gint_progression (Slide 26, PDF p.28) -- 3 sub-issues

All 3 LLMs unanimously agree:

| Sub-Issue | Claude | Codex | Gemini | Consensus |
|-----------|--------|-------|--------|-----------|
| 6/7 x-axis labels missing (only "Sim only" visible) | CRITICAL | MAJOR | CRITICAL | **CRITICAL** |
| "29.16" value overlaps Y-axis "Success Rate (%)" label | CRITICAL | MAJOR | MAJOR | **CRITICAL** |
| Left-edge clipping (first bar extends beyond plot area) | CRITICAL | CRITICAL | MAJOR | **CRITICAL** |

**Root cause:** Standalone PDF bounding box is too tight. The chart's x-axis labels and left margin are clipped in the original PDF generation. The inline Beamer version (SUNY.tex:882) uses `width=0.88\textwidth` which fits the frame, but the standalone (gint_progression.tex:27) uses `width=0.92\textwidth` relative to a standalone document page.

---

## MAJOR Issues

### 2. job_matrix (Slide 5, PDF p.5) -- 1 issue

| Issue | Claude | Codex | Gemini | Consensus |
|-------|--------|-------|--------|-----------|
| "Build"/"Analyze" vertical axis labels clipped at left/right edges | MAJOR | MAJOR | CRITICAL | **MAJOR** |

### 3. funding_chart (Slide 9, PDF p.9) -- 2 issues

| Issue | Claude | Codex | Gemini | Consensus |
|-------|--------|-------|--------|-----------|
| "H1 2025" Y-axis label completely missing for bottom bar | MAJOR | MAJOR | CRITICAL | **MAJOR** |
| Logical discrepancy: subtitle "More than all of 2024" but H1 2025=$6.0B < 2024=$6.1B | -- | -- | MAJOR | **MAJOR** (Gemini unique find) |

### 4. interview_pyramid (Slide 47, PDF p.50) -- 1 issue

| Issue | Claude | Codex | Gemini | Consensus |
|-------|--------|-------|--------|-----------|
| "Behavioral" text at pyramid tip too small for presentation distance | MAJOR | MAJOR | MINOR | **MAJOR** |

### 5. salary_chart (Slide 6, PDF p.6) -- 1 issue

| Issue | Claude | Codex | Gemini | Consensus |
|-------|--------|-------|--------|-----------|
| "AI" x-axis label missing on BOTH US and Korea charts (only "Non-AI" shown) | -- | PASS | MAJOR | **MAJOR** (verified by screenshot) |

---

## MINOR Issues

| Figure | Issue | Models |
|--------|-------|--------|
| interview_pyramid | "the differentiator" side annotation -- tan text low contrast on white | Gemini: MAJOR, Codex: MINOR |
| funding_chart | Bottom bar value "6" vs "6.0" -- inconsistent precision | Codex/Gemini: MINOR |
| gint_progression | "eval set changed" annotation small | Codex/Gemini: MINOR |
| fork_paths | Word hyphenation in standalone PDF ("em-pathy", "Deploy-ment") | Claude only (not in Beamer slide) |

---

## PASS (Confirmed by All 3 LLMs)

| Figure | Slide | PDF Page | Notes |
|--------|-------|----------|-------|
| career_timeline | 2 | 2 | Clean -- all boxes, arrows, text correct |
| fork_paths | 11 | 11 | Clean in Beamer (hyphenation only in standalone) |
| rag_pipeline | 15 | 16 | Clean -- pipeline flow correct |
| voice_timeline | 16 | 17 | Clean -- Day 0/3/14 timeline correct |
| lean_cycle | 22 | 23 | Clean -- 5-node cycle correct |
| venn_diagram | 34 | 36 | Clean -- overlap blending correct |
| thirty_day | 54 | 57 | Clean -- 2x2 grid with arrows correct |

---

## SSOT Divergences (Pre-existing, from Phase 0)

| Item | Status | Action |
|------|--------|--------|
| gint_progression dimensions (inline vs standalone) | Confirmed different | Fix standalone bounding box |
| salary_chart Korea chart absent from standalone/QMD | Confirmed | Create korea_salary_chart standalone |
| Beamer 64 frames vs QMD 65 slides | Confirmed | Document as intentional |

---

## Fix Priority

1. **gint_progression** -- Fix standalone bounding box, ensure all x-axis labels visible
2. **salary_chart** -- Add "AI" x-axis label to both US and Korea charts
3. **job_matrix** -- Widen bounding box for "Build"/"Analyze" axis labels
4. **funding_chart** -- Add "H1 2025" Y-axis label; verify data vs subtitle consistency
5. **interview_pyramid** -- Enlarge "Behavioral" text or move outside pyramid
