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

[LEARN:course-continuity] W13 introduced policy, feedback and inference delay again after students had worked examples in W02, W06 and W09 → check the delivered slides and recordings before adding a recap. Name the familiar example in one sentence and give the student a new physical quantity to measure.

[LEARN:w13-breadth] Promoting the presenter's choice of a recurring grasp example into the W13 structure displaced history, actuation, sensing and whole-body control → the November 18 ten-chapter hardware survey governs the lecture. Adjust the depth of each explanation for freshmen. Rotate examples across arms, mobile manipulators, quadrupeds and humanoids, and use a grasp only where it teaches contact.

[LEARN:w13-audience] A mixed first- and second-year audience and a joint-design syllabus were assumed for W13 → teach first-years in their second semester. Draw on the presenter's computer-vision and robot-learning expertise to explain what a policy can observe and command, how the body responds and which evidence would explain an outcome.

[LEARN:course-architecture] Put hardware foundations early as the bridge into robot learning → teach the robot-learning sequence first, then use hardware, control, and mechanical engineering as a late special module that synthesizes the physical stack.

[LEARN:authoring] Shortened personal-site labels can silently change an explicitly supplied public identity reference → when the presenter supplies exact author URLs, preserve the scheme and trailing slash in visible copy unless they ask for display aliases.

[LEARN:qa] `scripts/shoot_slides.py` stops when `Reveal.isLastSlide()` becomes true, before revealing fragments on the last physical slide → an all-state audit must continue until the last slide has no `.fragment:not(.visible)` elements.

[LEARN:authoring] Preserving source slide markup after cuts can leave stale audience-facing section numbers → keep original section numbers only in provenance attributes, and renumber every visible section-local label from 01 in the delivered sequence.

[LEARN:publishing] Moving only a deck's public endpoint does not move source ownership → when the project repository must own the presentation completely, transfer the editable source, assets, validation history, and note-free bundle together, then remove the deck-specific tree from Paper2PR; `publish: false` alone only excludes a deck from Paper2PR Pages.

[LEARN:design] A faithful 1920 x 1080 port can still look undersized after fitting inside Reveal's 1280 x 720 canvas → measure each fully revealed content bound and scale the centered inner block per slide; never apply one global zoom when dense result slides have less safety margin than sparse title or closing slides.

[LEARN:script-tone] Repeating autonomy and provenance caveats for every robot demo → teach source literacy once, let manifest captions carry later labels, and use each subsequent demo for a distinct capability-first insight; add only a few rounded local-currency anchors when dollar figures need intuition.

[LEARN:naming] Calling the DGIST HSS118 course "Future Literacy" (a gloss of the Korean course name) → its official English name is "Seminar for Comprehensive Competency Cultivation" (SCCC; DGIST portal, confirmed 2026-09-13): write it in full on first use and SCCC after, let the series `course:` field be the single source for slide subtitles and the landing page, and keep "Physical AI for Everyone" as the term's theme title only, never as the course name.

[LEARN:publishing] Checking only the visible page after a course rename → also check document titles, descriptions, Open Graph and Twitter metadata, preview images, generated search indexes, series locks, roadmap slides, and linked external decks; a current page does not prove that a third-party preview cache has refreshed.
[LEARN:pedagogy] Opening a first-year class with several scenes from earlier weeks made students depend on memory → establish a new scene and define the idea in everyday words first. Mention one earlier example in a complete sentence, and keep the rest of the prior-course evidence in instructor references.

[LEARN:terminology] Translating industry terms differently across the W13 plan, diagrams and speaker notes obscured the words students will find on real spec sheets → use the original English term, give a plain Korean explanation at first teaching use, and retain Korean names for glossary searches.

[LEARN:lecture-opening] Reintroducing the lecturer and recapping unrelated guest talks interrupted a returning class → open from the AI and data topics the students have studied, state today's hardware question directly, and give the answer to the first film during its own screen.

[LEARN:lecture-navigation] Unconnected component lessons and repeated rhetorical questions obscured the course structure → show the complete agenda with the current chapter highlighted, explain the practical reason to study each part, and reserve prediction time for questions the students can actually resolve.

[LEARN:hardware-examples] A single manufacturer's films dominated a cross-platform survey → choose Chinese, Korean and research platforms for their specific physical jobs, data collection methods and measured results, with a source beside each visual.

[LEARN:hardware-motion] A product still made it hard to see how a person controls a robot → show the input and response in the same short film, and let students watch the different interfaces together. Use actual task footage for comparisons whose meaning depends on motion.
