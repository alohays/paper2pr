# TTA 2026 Korean Speaker-Script Humanization Review

**Completed:** 2026-08-31
**Deck:** `Quarto/talks/tta-2026.qmd`
**Profile:** invited-talk
**Audience:** practitioner
**Final QMD SHA-256:** `0da7de4c38ca0caf62a5aeb05ec1b30718fabfcae2a6084744429959a6758ed0`
**Disposition:** PASS

## Scope

This pass reviewed and rewrote all 38 delivered-screen scripts: the title-slide `data-notes` payload and 37 note divs. The nine appendix screens remain intentionally unscripted because they are Q&A backup. Script length was measured for rehearsal awareness but was not an acceptance criterion.

The review used four independent lenses before and after the rewrite:

1. Humanizer and Korean oral-style patterns.
2. Verbatim read-aloud speakability.
3. Added explanatory value and factual boundaries.
4. Whole-talk narrative and presenter voice.

## Baseline

The original script was factually careful but sounded highly constructed when read aloud. The baseline contained 267 sentences and 5,930 Hangul syllables. Latin-script words accounted for 35.9% of word-like tokens. Four repeated Korean transition templates occurred 12, 10, 9, and 6 times respectively. Twenty-six sentences were at least 80 characters long, and nine were at least 100 characters long.

The main qualitative problems were:

- English ordinary nouns carried too much of the Korean sentence grammar.
- Metaphors, punchline framing, and uniform transition templates signaled generated prose.
- Presenter ownership was sparse even where interpretation was genuinely personal.
- Several table notes narrated rows instead of explaining the comparison.
- Full-screen videos lacked a consistent cue-before and interpretation-after structure.
- The final WoRV and CostNav material mixed model-reporting information with field-performance metrics.

## Changes

The complete script was rewritten in warm formal Korean intended to be read verbatim at a technical seminar. Canonical terms such as VLA, WAM, world model, teleop, rollout, policy, benchmark, method names, and model names were retained where the English form carries a technical distinction. Ordinary scaffolding such as model, robot, video, data, team, evaluation, success, and cost was converted to natural Korean where appropriate.

The rewrite also:

- removed slogan-like metaphors and staged punchlines;
- varied transitions and limited first-person phrasing to actual judgments;
- gave all seven full-screen videos a specific viewing cue, a blank breathing beat, and a post-video interpretation;
- encoded difficult symbols, units, and model names in directly speakable Korean;
- made the Dyna data-hours table interpret heterogeneous collection regimes instead of ranking them;
- kept action-only latency, 1.55x success, 380-episode, Elo, ROI, Zero-WAM, and Hybrid-row claims within their documented scope;
- separated model-reporting information from field-performance metrics in the TTA coda; and
- ended with a standards discussion question rather than repeating the opening thesis.

## Final Metrics

| Check | Final result |
|---|---:|
| Delivered scripts | 38 / 38 |
| Sentences | 277 |
| Hangul syllables | 6,233 |
| Latin-script words | 470 / 2,761 word-like tokens (17.0%) |
| Sentences at least 80 characters | 0 |
| Longest sentence | 79 characters |
| Full-screen video cue/resume pairs | 7 / 7 |
| Generic viewing cue / sequential cue / brief-attention cue | 0 / 0 / 0 |
| Split-focus construction / formal point-ending | 2 / 1 |
| First-person nominative variants | 2 / 6 / 4 |
| Em dash / en dash / double-hyphen prose | 0 / 0 / 0 |
| Connective-ending commas | 2 |

The remaining Latin-script words are predominantly canonical terminology and proper names. No deck-wide English-density or translated-cadence pattern remains.

## Independent Final Gates

All four reviewers inspected the same final QMD hash.

| Lens | High | Medium | Result |
|---|---:|---:|---|
| Humanizer and Korean oral style | 0 | 0 | Pass |
| Verbatim speakability | 0 | 0 | Pass |
| Technical content and public/private boundary | 0 | 0 | Pass |
| Narrative and presenter voice | 0 | 0 | Pass |

The final speakability audit covered 38 scripts and 277 sentences. It found no stage directions, punctuation blockers, ambiguous number readings, or unresolved breath problems.

## Build, Privacy, and Backup Verification

- `quarto render Quarto/talks/tta-2026.qmd`: pass.
- `quality_score.py`: 100/100, no critical issues.
- `test_note_filter.sh` and `test_korean_gate.sh`: pass against the clone's installed common hook from the primary checkout.
- Rendered deck: 47 sections, 37 `<aside class="notes">` blocks, and one title `data-notes` payload.
- Clean-filter output: zero Hangul characters and zero note markers.
- Final backup: 37 note divs plus title notes.
- QMD SHA-1: `d43cb8393d3a2b2e25e092da82b8595c6820c7fb`.
- Backup `original_sha1`: `d43cb8393d3a2b2e25e092da82b8595c6820c7fb`.
- Stripped QMD SHA-1: `ad7b7ac8d0ceba94003e93932cd6a87d273319e8`.
- Backup `stripped_sha1`: `ad7b7ac8d0ceba94003e93932cd6a87d273319e8`.

The linked-worktree copies of the two regression wrappers still refer to `.git/hooks` directly, although `.git` is a file in a linked worktree. The actual hook path returned by `git rev-parse --git-path hooks` is installed, executable, and byte-identical to `scripts/pre-commit.sh`; the same regression scripts pass from the primary checkout that owns the common hook directory.

## Informational Timing

The final extracted script measured 1,416.414785 seconds, or 23.61 minutes, with `say -v Yuna`. This is a rehearsal reference only. The presenter explicitly owns final pacing and trimming.

## Conclusion

The final script is stage-ready. It reads as one technically informed researcher-practitioner speaking to standards professionals, not as generated slide narration. It adds interpretation and caveats without inventing private claims, and it can be read verbatim without on-stage sentence repair.
