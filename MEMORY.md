# Project Memory

Corrections and learned facts that persist across sessions.
When a mistake is corrected, append a `[LEARN:category]` entry below.

---

<!-- Append new entries below. Most recent at bottom. -->

## Workflow Patterns

[LEARN:workflow] Requirements specification phase catches ambiguity before planning → reduces rework 30-50%. Use spec-then-plan for complex/ambiguous tasks (>1 hour or >3 files).

[LEARN:workflow] Spec-then-plan protocol: AskUserQuestion (3-5 questions) → write the MUST/SHOULD/MAY requirements at the top of the plan file `quality_reports/plans/YYYY-MM-DD_description.md` → declare clarity status (CLEAR/ASSUMED/BLOCKED) → get approval → then draft the rest of the plan.

[LEARN:workflow] Context survival before compression: (1) Update MEMORY.md with [LEARN] entries, (2) Ensure session log current (last 10 min), (3) Active plan saved to disk, (4) Open questions documented. The pre-compact hook displays checklist.

[LEARN:workflow] Plans, specs, and session logs must live on disk (not just in conversation) to survive compression and session boundaries. Quality reports only at merge time.

## Documentation Standards

[LEARN:documentation] When adding new features, update BOTH README.md and AGENTS.md immediately to prevent documentation drift. Stale docs break user trust. (The upstream `guide/` this entry used to name was removed in 2026-08; AGENTS.md is the single canonical description.)

[LEARN:documentation] Always document new templates in the AGENTS.md folder tree with a purpose description. Template inventory must be complete and accurate.

[LEARN:documentation] (Historical; the upstream `guide/` was removed in 2026-08.) The guide was meant to be generic (framework-oriented) not prescriptive, with templates for multiple workflows. This repo's docs now describe one framework, single Quarto path, and are allowed to be prescriptive.

[LEARN:documentation] Date fields in frontmatter and README must reflect latest significant changes. Users check dates to assess currency.

## Design Philosophy

[LEARN:design] (Historical; the constitutional-governance and requirements-spec templates this entry described were removed in 2026-08.) The upstream template favored framework-oriented rules users customize to their domain. This repo is one framework for one presenter, single Quarto path, and its rules are allowed to be prescriptive; requirements are free-form markdown in the plan file (see `plan-first-workflow.md`).

[LEARN:design] Quality standard for documentation additions (AGENTS.md, README.md): useful + pedagogically strong + drives usage + leaves great impression + improves upon starting fresh + no redundancy + not slow. All 7 criteria must hold.

[LEARN:design] (Historical; the LaTeX/Beamer and R paths were removed in 2026-08.) The upstream template aimed to serve any academic workflow. This repo targets exactly one: Quarto RevealJS decks for paper reviews, invited talks and course lectures. Test recommendations against those three genres, not against other toolchains.

## File Organization

[LEARN:files] Specifications are free-form markdown at the top of the plan file in `quality_reports/plans/`, not a separate specs document.

[LEARN:files] Templates belong in `templates/` directory with descriptive names. Currently have: session-log.md, speaker-notes-report.md (the upstream template set was removed in 2026-08).

## Constitutional Governance

[LEARN:governance] (Historical; the constitutional-governance template this described was removed in 2026-08.) Constitutional articles distinguish immutable principles (non-negotiable for quality/reproducibility) from flexible user preferences. Keep to 3-7 articles max.

[LEARN:governance] (Historical; the constitutional-governance template this described was removed in 2026-08.) Example articles: Primary Artifact (which file is authoritative), Plan-First Threshold (when to plan), Quality Gate (minimum score), Verification Standard (what must pass), File Organization (where files live).

[LEARN:governance] (Historical; the constitutional-governance template this described was removed in 2026-08.) Amendment process: Ask user if deviating from article is "amending Article X (permanent)" or "overriding for this task (one-time exception)". Preserves institutional memory.

## Skill Creation

[LEARN:skills] Effective skill descriptions use trigger phrases users actually say: "check citations", "format results", "validate protocol" → Claude knows when to load skill.

[LEARN:skills] Skills need 3 sections minimum: Instructions (step-by-step), Examples (concrete scenarios), Troubleshooting (common errors) → users can debug independently.

[LEARN:skills] Domain-specific examples beat generic ones: citation checker (psychology), protocol validator (biology), regression formatter (economics) → shows adaptability.

## Memory System

[LEARN:memory] (Historical; personal-memory.md was never carried into v2.) MEMORY.md commits generic patterns; machine-local state lives in `CLAUDE.local.md` and `.claude/settings.local.json`, both gitignored → cross-machine sync + local privacy.

[LEARN:memory] (Historical; upstream-template behaviour, removed in 2026-08 - no merge-related hook exists; the only .git hook installed is the pre-commit Korean gate.) Post-merge hooks prompt reflection, don't auto-append → user maintains control while building habit.

## Meta-Governance

[LEARN:meta] (Historical; the repo stopped being a fork-me template in 2026-08.) Repository dual nature requires explicit governance: what's generic (commit) vs specific (gitignore) → prevents template pollution.

[LEARN:meta] (Historical; the guide/ this pointed at was removed in 2026-08 - the kernel stands: we follow our own rules.) Dogfooding principles must be enforced: plan-first, spec-then-plan, quality gates, session logs.

[LEARN:meta] (Historical framing; the fork-me rationale went with the template in 2026-08, but the rule itself stands.) Infrastructure and docs work doesn't create session logs in quality_reports/ → those are for deck work (slides, analysis), not meta-work.

## Course Architecture

[LEARN:course-architecture] Put hardware foundations early as the bridge into robot learning → teach the robot-learning sequence first, then use hardware, control, and mechanical engineering as a late special module that synthesizes the physical stack.
