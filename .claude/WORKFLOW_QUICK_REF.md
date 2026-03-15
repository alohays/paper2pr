# Workflow Quick Reference

**Model:** Contractor (you direct, Claude orchestrates)

---

## The Loop

```
Your instruction
    ↓
[PLAN] (if multi-file or unclear) → Show plan → Your approval
    ↓
[EXECUTE] Implement, verify, done
    ↓
[REPORT] Summary + what's ready
    ↓
Repeat
```

---

## I Ask You When

- **Design forks:** "Option A (fast) vs. Option B (robust). Which?"
- **Content scope:** "Include code-level insights for this paper, or paper-only?"
- **Ambiguity:** "Paper claims X but code shows Y. How to present?"
- **Scope question:** "Also review related work section, or focus on method?"

---

## I Just Execute When

- Slide fix is obvious (typo, formatting, citation)
- Verification (compilation, rendering, quality scoring)
- Documentation (logs, commits)
- Figure conversion (PDF → SVG)
- Deployment (after you approve, I ship automatically)

---

## Quality Gates (No Exceptions)

| Score | Action |
|-------|--------|
| >= 80 | Ready to commit |
| < 80  | Fix blocking issues |

---

## Non-Negotiables

- **Figures:** Per-paper subdirectories in `Figures/PaperName/`, PDF for Beamer + SVG for Quarto
- **Color palette:** Primary blue `#012169`, Gold `#B9975B`, Yellow `#F2A900`
- **Source of truth:** Beamer `.tex` is authoritative; Quarto `.qmd` derives from it
- **Notation:** Follow the original paper's notation exactly
- **Attribution:** All figures from papers must be attributed

---

## Preferences

**Visual:** Figures from original paper PDFs, converted to SVG. Custom TikZ diagrams for explanatory visuals.
**Reporting:** Concise bullets. Details on request.
**Session logs:** Always (post-plan, incremental, end-of-session)
**Code insights:** When official code available, include interesting implementation details

---

## Exploration Mode

For experimental work, use the **Fast-Track** workflow:
- Work in `explorations/` folder
- 60/100 quality threshold (vs. 80/100 for production)
- No plan needed — just a research value check (2 min)
- See `.claude/rules/exploration-fast-track.md`

---

## Next Step

You provide task → I plan (if needed) → Your approval → Execute → Done.
