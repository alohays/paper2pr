# DGIST W13 authoring setup, November 18

The reviewed outline is ready for production. The local branch `codex/dgist-w13` starts at `dc364cb`, the merge that includes the delivered W09 deck and its figures. The W13 source currently renders seven starter slides. The course hub in the presenter's vault links to the working handoff.

## Resume on this Mac

From `~/maangeek/paper2pr-w13`, read `.local/w13-prep/codex-handoff.md` and `.local/w13-prep/outline-draft-2026-11-18.md`. Open `.local/dgist-w13-source-library/catalog.html` to look up a candidate by ID. These two directories link to the existing vault and library. The exact Claude session mapping and the relevant transcript ranges are in `.local/claude-session.md`.

The draft has 56 active content rows across ten chapters. Their clocks sum to 50 minutes, with ten more minutes for Q&A. Start with the Atlas opening and the W09 action-chunk callback, then draw the journey from target to contact for row 1.1. Rows 1.2, 2.3, 5.9, and 7.1 need their own figures. The itemized outstanding decisions and source qualifications are in the vault handoff.

## Checks

| Check | Observed result |
| --- | --- |
| Series, configuration and local render | W13 resolves to November 20. The calendar callback resolves to W12. W09 supplies the technical callback. Quarto 1.8.27 renders the starter. |
| Browser and site assembly | Seven slides fit the 1280 × 720 frame. The local presenter HTML contains one starter note. The assembled audience HTML contains zero notes. All 392 local references across the assembled site resolve. The starter scored 100/100 on the lecture-scoped checks. |
| Research library | 654 distinct sources, 495 with local material. All 745 catalog file paths exist. The 373 videos each have a contact-sheet verdict. The catalog supports looking up the exact clip ID from the outline with duplicate hiding enabled. |
| Opening and closing clip | The 1920 × 1080 Atlas original plays muted at 0:00–0:16 and 1:24–1:36. The gamepad is on screen alongside a simulated robot. The operator of the filmed warehouse run is unspecified. |
| Instructor tools | The study site's own checks passed. In Chrome, changing the gear ratio and feedback gain updated the displayed values, and choosing another task updated BodySelector. |

Run `quarto render Quarto/lectures/dgist-2026f-w13.qmd` after the next edit. The repository's notes filter and pre-commit hook cover this path.
