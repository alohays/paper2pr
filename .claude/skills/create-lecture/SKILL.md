---
name: create-lecture
description: Create a new lecture/paper-review deck, authored directly in Quarto RevealJS. Guided workflow with notation consistency and the minimalist design principles.
argument-hint: "[Topic name]"
allowed-tools: ["Read", "Grep", "Glob", "Write", "Edit", "Bash", "Task"]
context: fork
---

# Lecture Creation Workflow

Create a beautiful, pedagogically excellent slide deck, **authored directly
in Quarto RevealJS** (`Quarto/PaperName.qmd`, main theme). Beamer is an
optional export produced only on explicit request.

**This is a collaborative, iterative process. The instructor drives the vision; Claude is a thinking partner.**

---

## CONSTRAINTS (Non-Negotiable)

1. **Read the knowledge base FIRST** — notation registry, narrative arc, applications database
2. **Follow `.claude/rules/slide-design-principles.md`** — one idea per
   slide, ≤5 one-line bullets (≤3 with a figure; one less again if a
   bullet wraps to two lines, and only one may wrap), max 1 colored box,
   never shrink fonts to fit; split slides instead (40–60 slides for ~30 min is fine)
3. Every new symbol MUST be checked against the notation registry
4. Motivation before formalism — no exceptions
5. Worked example within 2 slides of every definition
6. No `\pause`-style all-at-once reveals that fight the layout (check project rules)
7. Transition slides at major conceptual pivots
8. Thread at least 1 running empirical application throughout
9. All citations verified against the bibliography
10. **Work in batches of 5-10 slides** — share for feedback, don't bulk-dump

---

## WORKFLOW

### Phase 0: Intake & Context
- Read knowledge base and creation guide
- Inventory provided materials (papers, slides, code)
- Read previous lecture's structure and ending
- State pedagogical goal, get user confirmation

### Phase 1: Paper Analysis (When Papers Provided)
- Split into chunks, extract key ideas
- Map paper notation → course notation
- Identify slide-worthy content
- Present summary for approval

### Phase 2: Structure Proposal
- Propose outline (5-Act or 3-Part template)
- List TikZ diagrams and R figures needed
- List new notation to introduce
- **GATE: User approves before Phase 3**

### Phase 3: Draft Slides (Iterative)
- Create the QMD with the required YAML from
  `.claude/rules/slide-design-principles.md` (`center: false`,
  `auto-stretch: false`, main theme)
- Work in batches of 5-10 slides
- Check notation, apply creation patterns
- Quality checks during drafting (density budget on every slide)

### Phase 4: Figures & Code
- R scripts following conventions; save RDS for plotly integration
- TikZ diagrams in `Figures/PaperName/extract_tikz.tex` → PDF → SVG
  (`/extract-tikz`)

### Phase 5: Polish & Render
- `quarto render`, open in browser, walk every slide
- Run Devil's Advocate
- Run Substance Review (if domain reviewer configured)
- Update knowledge base with new notation

---

## Post-Creation Checklist

```
[ ] Deck renders without errors
[ ] No slide overflows at 1280x720
[ ] All citations resolve
[ ] Every definition has motivation + worked example
[ ] Density budget respected (≤5 one-line bullets, ≤1 wrapped bullet
    which costs a slot, ≤1 colored box per slide)
[ ] No .smaller/.smallest anywhere in the deck
[ ] 2-3 Socratic questions embedded
[ ] Transition slides between sections
[ ] At least 1 running application threaded throughout
[ ] New notation added to knowledge base
[ ] Session log updated
[ ] Devil's Advocate run
```
