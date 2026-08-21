---
paths:
  - "Quarto/**/*.qmd"
  - "quality_reports/**"
---

# Proofreading Agent Protocol (MANDATORY)

**Every deck (`Quarto/<genre>/*.qmd`) MUST be reviewed before any commit or PR.**

**CRITICAL RULE: The agent must NEVER apply changes directly. It proposes all changes for review first.**

## What the Agent Checks

1. **Grammar** -- subject-verb agreement, missing articles, wrong prepositions
2. **Typos** -- misspellings, search-and-replace corruption, duplicated words
3. **Overflow** -- content exceeding the 1280x720 slide canvas
4. **Consistency** -- notation, citation style (`@key` vs `[@key]`), terminology
5. **Register** -- informal abbreviations, missing words, phrasing that the
   declared audience would trip over

## Three-Phase Workflow

### Phase 1: Review & Propose (NO EDITS)

Each agent:
1. Reads the entire file
2. Produces a **report** with every proposed change:
   - Location (line number or slide title)
   - Current text
   - Proposed fix
   - Category (grammar / typo / overflow / consistency / register)
3. Saves report to `quality_reports/reviews/<Deck>-proofread-<YYYY-MM-DD>.md`
   (create the directory if it does not exist)
4. **Does NOT modify any source files**

### Phase 2: Review & Approve

The user reviews the proposed changes:
- Accepts all, accepts selectively, or requests modifications
- **Only after explicit approval** does the agent proceed

### Phase 3: Apply Fixes

Apply only approved changes:
- Use Edit tool; use `replace_all: true` for issues with multiple instances
- Verify each edit succeeded
- Report completion summary
