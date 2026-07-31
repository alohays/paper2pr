---
name: qa-quarto
description: "Adversarial Quarto vs Beamer QA for decks imported from a Beamer twin (legacy import path). Critic finds issues, fixer applies fixes, loops until APPROVED (max 5 rounds). Quarto-only decks should use /visual-audit or /slide-excellence instead."
argument-hint: "[PaperName]"
allowed-tools: ["Read", "Grep", "Glob", "Write", "Edit", "Bash", "Task"]
context: fork
---

# Adversarial Quarto vs Beamer QA Workflow (Import QA)

Compare Quarto HTML slides against their Beamer PDF benchmark using an iterative critic/fixer loop.

**Scope:** only decks that were imported from a Beamer twin
(`/translate-to-quarto`). Quarto is the project's source of truth; for
Quarto-only decks use `/visual-audit` or `/slide-excellence` instead.

**Philosophy:** During an import, the Beamer PDF is the content benchmark.
The Quarto version must lose nothing — but it follows the Quarto design
principles, so layout differences that come from the minimalist theme
(bigger type, centered content, split slides) are expected, not regressions.

---

## Workflow

```
Phase 0: Pre-flight → Phase 1: Critic audit → Phase 2: Fixer → Phase 3: Re-audit → Loop until APPROVED (max 5 rounds)
```

## Hard Gates (Non-Negotiable)

| Gate | Condition |
|------|-----------|
| **Overflow** | NO content cut off |
| **Plot Quality** | Interactive charts >= static plots |
| **Content Parity** | No missing slides/equations/text |
| **Visual Regression** | Quarto >= Beamer in all dimensions |
| **Slide Centering** | Content centered, no jumping |
| **Notation Fidelity** | All math verbatim from Beamer |

## Phase 0: Pre-flight

1. Locate Beamer (.tex/.pdf) and Quarto (.qmd/.html) files
2. Check freshness (re-render if QMD newer than HTML)
3. Verify TikZ SVGs if applicable

## Phase 1: Initial Audit

Launch the `quarto-critic` agent to compare Beamer vs Quarto comprehensively. Report saved to `quality_reports/[Lecture]_qa_critic_round1.md`.

## Phase 2: Fix Cycle

If not APPROVED, launch `quarto-fixer` agent to apply fixes (Critical → Major → Minor), re-render, and verify.

## Phase 3: Re-Audit

Re-launch critic to verify fixes. Loop back to Phase 2 if needed.

## Iteration Limits

Max 5 fix rounds. After that, escalate to user with remaining issues.

## Final Report

Save to `quality_reports/[Lecture]_qa_final.md` with hard gate status, iteration summary, and remaining issues.
