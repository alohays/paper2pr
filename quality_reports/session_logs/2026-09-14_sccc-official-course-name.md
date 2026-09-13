# Session Log: 2026-09-14 -- Official English course name (SCCC)

**Status:** COMPLETED (edits and verification; commit/push scope left to the presenter)

## Objective

Replace "Future Literacy" with the official English name of the DGIST HSS118 course,
"Seminar for Comprehensive Competency Cultivation" (SCCC), across Paper2PR, the personal
site and the vault; record the source so the name is never guessed again.
Plan: `quality_reports/plans/2026-09-14_sccc-official-course-name.md`.

## Design Decisions

| Decision | Alternatives Considered | Rationale |
|----------|------------------------|-----------|
| Theme title `Physical AI for Everyone` | `Physical AI for All` (presenter's first idea), `for All Majors`, `Introduction to Physical AI` | intro-course idiom, no campaign flavour, signals no prerequisites |
| Full official name in the slide subtitle | `SCCC` + a new `course_short` series field | the title slide is the one place the full name matters; no schema change needed |
| Keep the vault folder slug | rename to `dgist-sccc-2026fall` | slug is private; every path reference would break; vault git history is damaged (missing object) so `git mv` cannot be tracked |

## Incremental Work Log

**2026-09-13:** Scouted all four working directories; found the old name in the series yml,
the landing page, the tests, the deck's local notes, the site's course page, and the vault
project docs. HSS118 traced to the admin team's syllabus form (2026-06-29).
**2026-09-14:** Presenter chose the theme title and the full-name subtitle; edits applied,
lock and landing regenerated, notes backup refreshed.

## Learnings & Corrections

- [LEARN:naming] "Future Literacy" was a gloss, not the course name; the official English
  name is on the DGIST portal, and the series `course:` field is the single source for slides.

## Verification Results

| Check | Result | Status |
|-------|--------|--------|
| `series_assets.py dgist-2026f --check` | lock and images current | PASS |
| `test_series.py`, `test_profiles.py`, `test_minyaml.py`, `test_korean_gate.sh`, `test_note_filter.sh`, `test_media.py` | all passed (re-run independently by the review workflow) | PASS |
| `quality_score.py` on dgist-2026f-w02 | >= 95, 0 critical | PASS |
| Title slide screenshot | official name on line 1, `HSS118 · W02 · DGIST` on line 2, nothing clipped (subtitle break moved after the name; the one-line form wrapped at "Competency / Cultivation") | PASS |
| Personal site `mkdocs build` | 0 old-name hits; description 172 chars; live site checked at 375 px width, header wraps cleanly | PASS |
| Residual sweep (four roots, live areas) | old name remains only where it is named as superseded (README callout, LinkedIn note, course-webpage record, syllabus note, MEMORY.md, plan/log, memory) plus the published LinkedIn text and archives/scratch | PASS |
| Review workflow (sweep, site copy, paper2pr, vault, critic; 5 agents) | 6 must-fix (stale mockup render, 5 daily-note link aliases) and 6 should-fix, all applied | PASS |

Known leftovers (by design or out of reach): deployed Paper2PR landing and W02 slides and the deployed course page keep the old name until the branches are pushed; the submitted ASSIST `RESUME_Yunsung Lee.docx` carries "Future Literacy Seminar (HSS118)" once (left as sent); two other paper2pr worktrees (`paper2pr-tta`, the merged codex branch) are behind main; Wooclap event title and LinkedIn profile not checkable from this machine; AGENTS.md line 233 and the yml header still describe the Wooclap code as PLACEHOLDER (belongs to the in-progress Wooclap change set on this branch).

## Open Questions / Blockers

- [ ] Commit and push scope for `w02-design` and the personal site (both carry unrelated
      uncommitted work) -- presenter's call.
- [ ] Vault git repository: `git status` fails on a missing object `f6b154b9`; not touched.
