# Session Log: Repository-Wide Audit + Fixes

**Date:** 2026-08-03
**Trigger:** `/goal` — hard audit of the 2026-07-31 minimalist-design session and
the codebase as a whole, produce a decision-oriented report, fix only what is
unambiguous.

## Method

Direct verification (browser instrumentation, gate execution, git archaeology)
plus three parallel read-only auditors over `.claude/` infrastructure,
`scripts/`, and documentation. Every finding quoted below was reproduced
first-hand before being acted on — the auditors' claims were spot-checked, not
taken at face value.

## What the audit found about the 2026-07-31 session

Good: the legacy theme snapshot is **byte-identical** to the pre-pivot
`clean-academic.scss` (verified by diff), so the three already-presented decks
cannot render differently. Commit hygiene was solid — 4 of 5 commits carried a
full trailer set.

Two real misses:

1. **The new quality gate was off.** `get_deck_theme()` matched only
   `theme: [default, clean-academic.scss]`. YAML has three legal spellings and
   Quarto's own render log echoes the block form back, so a deck written either
   of the other two ways skipped every design check. Same violations scored
   89 one way and 100 the other.
2. **Verification was a single sample.** The commit says "verified in-browser at
   1280x720" — and 720px is the one window height at which the theme's `vh`
   image caps happen to equal their intended fraction of the slide. At 900px
   the cap becomes 56% of the slide and a bullet is silently clipped; at 1080px
   it is 68% and two are.

## Other findings worth recording

- The **Korean pre-commit gate had never fired**. `grep -cP` resolves to BSD
  grep under git's bare hook PATH (no `-P`), and `2>/dev/null || true` ate the
  error. `\uXXXX` is not PCRE syntax either. Staged Korean text exited 0.
- `quality_score.py` passed `--to html`, overriding `format: revealjs` and
  overwriting `<Name>.html` with a plain page — **scoring a deck destroyed it**.
  Observed live: the audit's own scoring run clobbered all four decks.
- The written density budget (≤5 bullets, each ≤2 lines) overflows the 720px
  canvas by 38px while scoring 100/100.
- `.speaker-notes/SUNY.json` — the full SUNY script — was tracked and public
  despite `.gitignore` listing the directory. gitignore does not apply to
  already-tracked files.
- A 72 MB pre-pivot worktree was living inside `.claude/`, so recursive searches
  there returned reverted guidance as if it were current.

## Fixed (8 commits, then pushed)

Only defects where inaction would silently undo a decision already taken, plus
the three decisions the user made in follow-up:

| Fix | Verified by |
|-----|-------------|
| Gate no longer fails open on valid YAML theme forms | one fixture, three spellings, all now 89 |
| Korean gate actually blocks | 5 cases: Korean/English/tracked-modified/exempt/empty |
| Scoring stops destroying rendered decks | reveal markers 0 → 50-52, all four re-rendered |
| `WORKFLOW_QUICK_REF` + `quarto-fixer` no longer contradict split-first | — |
| Image caps pinned to the canvas, not the window | cap constant 324/432px at 720, 900, 1200 |
| Density budget matches the frame | 8-slide fixture, fires on exactly the 4 that should |
| SUNY script untracked; `Quarto/videos/` ignored | `git ls-files .speaker-notes/` empty |
| `design-test.qmd` excluded from CI publish | loop simulated against the real file list |

## Decisions taken by the user

- Test deck: exclude from CI rather than rename or delete
- `vh` fix: keep the intended 45% / 60%, only change the unit
- Density: **tighter** than proposed — one-line bullets preferred, at most one
  wrapped bullet per slide, and it costs a slot (5 → 4, 3 → 2 with a figure)
- Script leak: remove from HEAD, leave the blob in history

## Not fixed — reported only

~71 findings, in the published audit report. The largest cluster is the
unfinished Quarto-first pivot: `pedagogy-reviewer`, `proofreader`,
`beamer-translator` and `quarto-critic` still carry pre-pivot limits, and the
TikZ source-of-truth is defined two contradictory ways across three files.
`/pdf-diff` hard-codes a nonexistent absolute path and then runs
`git stash --include-untracked`, which needs a scope decision (fix or delete)
now that Beamer is demoted. `strip_qmd_notes.py`'s regex misses eight note
forms — history is clean today only because both note-bearing decks are
machine-generated in one canonical shape.

## Open

- `quality_reports/suny_script_compression/` left untracked by choice — contains
  word counts and editing notes only, no script prose (checked).
- The `git rm --cached` removes the script from HEAD but the blob stays
  reachable in history, per the user's explicit decision.
