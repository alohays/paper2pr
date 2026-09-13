# Plan: Official English course name (SCCC) across Paper2PR, the personal site and the vault

**Status:** APPROVED (decisions aligned with the presenter through AskUserQuestion, 2026-09-13 to 09-14)
**Date:** 2026-09-14

## Goal

The DGIST HSS118 course was called "Future Literacy" in English everywhere (a gloss of
the Korean course name). Its official English name is **Seminar for Comprehensive Competency
Cultivation** (abbreviation **SCCC**), as shown on the DGIST portal / LMS (presenter
confirmed 2026-09-13). Replace the old name in every live document so the mistake cannot
recur, and record the source.

## Decisions

| Question | Decision | Rationale |
|---|---|---|
| Course page H1 (theme title) | `Physical AI for Everyone` | "for Everyone" is the idiom for an intro course with no prerequisites (AI For Everyone, Python for Everybody); "for All" reads like a public campaign; "Introduction to" reads like a major's first course |
| Where the official name goes on the site | meta line under the H1, the description, the scope paragraph, the teaching index | the H1 stays short and inviting; the official name is always one line below |
| Slide subtitle and landing heading | full official name via the series `course:` field | the title slide is the one place an outsider learns which course this is; verify it fits one line |
| Vault folder `dgist-future-literacy-2026fall` | keep the slug, edit contents, add frontmatter fields and aliases | the slug is not public and every daily note / plan / script path points at it |
| W02 speaker script (delivered 2026-09-04, local-only) | the spoken opening names the course by its official Korean name instead of "Future Literacy" | Korean speech; the file is the template for W06. Scratch copies under `tmp/`, `_workspace/` stay |
| Published LinkedIn post (2026-08-17) | text untouched, dated correction note added in the vault record | the vault copy is the record of what was published |
| ASSIST CV build script | source string updated; `out/` documents (submitted 2026-08) untouched | submitted files stay as sent |
| HSS118 | confirmed official: pre-filled in the admin team's syllabus form (2026-06-29) | `reference/template-extracted.md` |

## Files

Paper2PR (`w02-design`): `Quarto/lectures/_series/dgist-2026f.yml` (`course:`), regenerated
`Figures/lectures/_series/dgist-2026f/series.json` and `pages/index.html`,
`scripts/test_series.py` (3 expectations), `Quarto/_fixtures/theme-mockups/w02-sample.qmd`,
`Quarto/lectures/dgist-2026f-w02.qmd` (title-slide notes, local-only), `AGENTS.md`,
`.claude/skills/new-deck/SKILL.md`, `MEMORY.md` ([LEARN:naming]); local-only:
`Quarto/_script/lectures/dgist-2026f-w02.md`, `.speaker-notes/lectures/dgist-2026f-w02.json`.

Personal site (`alohays.github.io`): `docs/teaching/dgist-hss118-2026f/index.md` (title,
description, H1, meta line, scope paragraph), `docs/teaching/index.md`.

Vault: `1-projects/maum/dgist-future-literacy-2026fall/` README (frontmatter fields, official
name callout, course row), `syllabus-draft.md`, `linkedin-post.md` (note), `course-webpage.md`
(dated record), `lectures/w02-paradigm-shift/deck-plan.md` (fallback literal);
`1-projects/maum/assist-physical-ai-2026fall/build/build_cv.py`.

Memory: `~/.claude/projects/-Users-iyunseong-maangeek-paper2pr/memory/dgist-course-official-name.md`.

## Verification

1. `python3 scripts/series_assets.py dgist-2026f --check`, `python3 scripts/test_series.py`
2. `quarto render Quarto/lectures/dgist-2026f-w02.qmd`; title slide screenshot: subtitle on one line
3. `python3 scripts/quality_score.py Quarto/lectures/dgist-2026f-w02.qmd` still >= 80
4. `mkdocs build` of the site; the course page header and the teaching row render without overflow
5. Residual sweep: no "Future Literacy" outside archives, scratch dirs, and the published LinkedIn record
6. Independent review workflow (residual sweep, site copy, paper2pr checks, vault consistency)

Not in scope: committing or pushing either repository (both carry unrelated uncommitted work;
the presenter decides the commit scope), rebuilding the submitted ASSIST CV, the vault git
repository's missing object (`f6b154b9`, reported separately).
