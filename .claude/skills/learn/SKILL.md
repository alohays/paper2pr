---
name: learn
description: |
  Extract reusable knowledge from the current session into a persistent skill.
  Use when you discover something non-obvious, create a workaround, or develop
  a multi-step workflow that future sessions would benefit from.
author: Claude Code Academic Workflow
version: 1.0.0
argument-hint: "[skill-name (kebab-case)]"
allowed-tools: ["Read", "Write", "Bash", "Glob", "Grep"]
---

# /learn — Skill Extraction Workflow

Extract non-obvious discoveries into reusable skills that persist across sessions.

## When to Use This Skill

Invoke `/learn` when you encounter:

- **Non-obvious debugging** — Investigation that took significant effort, not in docs
- **Misleading errors** — Error message was wrong, found the real cause
- **Workarounds** — Found a limitation with a creative solution
- **Tool integration** — Undocumented API usage or configuration
- **Trial-and-error** — Multiple attempts before success
- **Repeatable workflows** — Multi-step task you'd do again
- **User-facing automation** — Reports, checks, or processes users will request

## Workflow Phases

### PHASE 1: Evaluate (Self-Assessment)

Before creating a skill, answer these questions:

1. "What did I just learn that wasn't obvious before starting?"
2. "Would future-me benefit from this being documented?"
3. "Was the solution non-obvious from documentation alone?"
4. "Is this a multi-step workflow I'd repeat?"

**Continue only if YES to at least one question.**

### PHASE 2: Check Existing Skills

Search for related skills to avoid duplication:

```bash
# Check project skills
ls .claude/skills/ 2>/dev/null

# Search for keywords
grep -r -i "KEYWORD" .claude/skills/ 2>/dev/null
```

**Outcomes:**
- Nothing related → Create new skill (continue to Phase 3)
- Same trigger & fix → Update existing skill (bump version)
- Partial overlap → Update with new variant

### PHASE 3: Create Skill

Create the skill file at `.claude/skills/[skill-name]/SKILL.md`:

```yaml
---
name: descriptive-kebab-case-name
description: |
  [CRITICAL: Include specific triggers in the description]
  - What the skill does
  - Specific trigger conditions (exact error messages, symptoms)
  - When to use it (contexts, scenarios)
author: Claude Code Academic Workflow
version: 1.0.0
argument-hint: "[expected arguments]"  # Optional
---

# Skill Name

## Problem
[Clear problem description — what situation triggers this skill]

## Context / Trigger Conditions
[When to use — exact error messages, symptoms, scenarios]
[Be specific enough that you'd recognize it again]

## Solution
[Step-by-step solution]
[Include commands, code snippets, or workflows]

## Verification
[How to verify it worked]
[Expected output or state]

## Example
[Concrete example of the skill in action]

## References
[Documentation links, related files, or prior discussions]
```

### PHASE 4: Quality Gates

Before finalizing, verify:

- [ ] Description has specific trigger conditions (not vague)
- [ ] Solution was verified to work (tested)
- [ ] Content is specific enough to be actionable
- [ ] Content is general enough to be reusable
- [ ] No sensitive information (credentials, personal data)
- [ ] Skill name is descriptive and uses kebab-case

## Output

After creating the skill, report:

```
✓ Skill created: .claude/skills/[name]/SKILL.md
  Trigger: [when to use]
  Problem: [what it solves]
```

## Example: Creating a Skill

User discovers that a level-1 heading inside a RevealJS deck changes the slide structure:

```markdown
---
name: reveal-level1-heading-vertical-stack
description: |
  Diagnose a Quarto RevealJS deck whose slides after some point all appear
  under one horizontal position (vertical stack). Use when: slide count in
  the browser is far below the `##` count, or the arrow keys suddenly move
  down instead of right.
author: Claude Code Academic Workflow
version: 1.0.0
---

# Level-1 Heading Collapses Slides into a Vertical Stack

## Problem
A `#` (level-1) heading anywhere after the title slide makes RevealJS treat
every following `##` slide as a vertical child of that section, so the
deck loses its left-to-right flow and the rendered slide count drops.

## Context / Trigger Conditions
- `quality_score.py` reports BLOCKER `[level1_heading]` and forces the score to 0
- Arrow-right stops advancing; arrow-down does
- The deck recently gained a section divider written as `# Title`

## Solution
1. `grep -n '^# ' Quarto/<genre>/<deck>.qmd` to find the heading
2. Rewrite section dividers as `## Title {.divider}` (the `slide-types.lua`
   filter maps the class to a full-bleed background)
3. Re-render and walk the deck with `bash scripts/preview.sh <deck>`

## Verification
`bash scripts/preview.sh <deck>` shows one horizontal slide per `##`; the PNG
count from `python3 scripts/shoot_slides.py <deck>` matches the `##` count.

## References
- `Quarto/_filters/slide-types.lua`
- `.claude/rules/slide-design-principles.md`
```
