# Session Log: Quarto Math Rendering Fix (MathJax → KaTeX)

**Date:** 2026-03-15
**Goal:** Fix broken math rendering in Quarto RevealJS slides
**Status:** COMPLETED

---

## Problem

Quarto RevealJS slides had consistently broken math: tofu squares instead of symbols, broken horizontal braces. Affected both `quarto preview` and direct `file://` opening.

## Root Cause

reveal.js default math plugin uses MathJax 2.7.9 from CDN — incompatible with current reveal.js version bundled by Quarto 1.8.27.

## Solution

Set `html-math-method: katex` in QMD YAML header. KaTeX replaces MathJax entirely (disables RevealMath plugin, adds inline KaTeX render script). All LaTeX commands in DreamZero.qmd are KaTeX-compatible — zero math expression changes needed.

## Files Changed

- `Quarto/DreamZero.qmd` — added `html-math-method: katex` to YAML
- `Quarto/_quarto.yml` — new file, project-level KaTeX default

## Key Learnings

- `html-math-method: katex` works for revealjs but the `url:` parameter is ignored (always CDN)
- `embed-resources: true` breaks revealjs (can't embed reveal.js core libs)
- `self-contained-math: true` requires `embed-resources` which doesn't work for revealjs
- Opening HTML via `file://` blocks CDN scripts — always use `quarto preview` or web server

## Open Items

- Consider adding post-render script to replace CDN URLs with local KaTeX for offline `file://` support
- Update `/translate-to-quarto` skill to include `html-math-method: katex` by default
