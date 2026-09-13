# DGIST W02 optimistic speaker-notes revision (2026-09-04)

## Audience and intent

The audience is 93 first- and second-year undergraduates outside AI-related
majors. The revision keeps the early autonomy-versus-teleoperation exercise as
one media-literacy lesson, then moves the rest of the lecture toward an
optimistic, capability-first reading of embodied AI.

## Narrative changes

- The early Atlas comparison now says explicitly that it is the lecture's one
  detailed autonomy exercise. It treats company descriptions as usable evidence
  with source labels, not as claims to rebut.
- Later demos now have distinct technical jobs: model-based whole-body control,
  web-knowledge transfer, closed-loop long-horizon manipulation, environment
  generalization, shared policies across two robots, multi-humanoid
  synchronization, industrial productization, home-task integration, and
  value-aware navigation plus bimanual coordination.
- The closing frame changed from "ask first: was it autonomous?" to "what
  capability can scale?" The three takeaways now end on "generalize and scale."
- The no-question Q&A fallback now asks which demo showed the greatest AI
  potential and why.

## Repetition audit

| Spoken-note pattern | Before | After |
|---|---:|---:|
| Korean autonomy-term occurrences | 24 | 7 |
| English `autonom*` occurrences | 23 | 5 |
| Korean teleoperation-term occurrences | 13 | 8 |
| Explicit company-claim phrasing | 2 | 0 |
| Explicit public-material caveats | 3 | 0 |
| Explicit not-stated phrasing | 5 | 0 |
| Repeated must-verify phrasing | 4 | 0 |

The manifest captions still carry the source-specific autonomy labels. The
speaker no longer repeats those labels for every demo.

## Currency context

The industry passage preserves every original dollar figure and adds two
rounded won anchors: USD 39 billion is about KRW 53 trillion, and USD 1.4
billion is about KRW 1.9 trillion. The spoken conversion uses KRW 1,360 per USD,
rounded from Woori Bank's 2026-09-03 base rate of KRW 1,356.50:
https://spot.wooribank.com/pot/jcc?__ID=c012349&withyou=CMCOM0185

## `humanize-korean` (`im-not-ai`) pass

- Run directory: `_workspace/2026-09-04-001/`
- Genre: spoken lecture; conservative intensity
- Deterministic style-only change rate: 3.7% (below the 30% warning threshold)
- Grade: B. The source had already received a prior humanizing pass, so this
  run avoided forcing the 10% minimum required for grade A.
- Self-check: 6/6 passed. Proper names, figures, dates, direct quotations, and
  the formal conversational register were preserved.
- Selected deltas: relative-clause nesting 19 to 14; antithesis patterns 9 to
  7; formal-noun emphasis 4 to 0; connective-ending commas 34 to 30.

## Verification

- Quarto render: pass, 47 slides and 47 note payloads.
- `quality_score.py`: 100/100, zero blockers.
- `test_note_filter.sh`, `test_korean_gate.sh`, `test_series.py`, and
  `test_profiles.py`: pass.
- Rendered views of the changed Atlas-history, Helix, deployment, and takeaway
  slides were inspected at the presentation canvas; no clipping or wrapping
  regression was found.
- The local assembled site resolves all 259 referenced assets.
- The classroom directories and all three classroom ZIPs contain the polished
  notes, local video paths, and current Wooclap QR.
- The refreshed local TTS is 41:26, decodes end to end in both M4A and MP3, and
  contains no silence interval of five seconds or longer.
