# Session Log: 2026-09-01 -- On-Manifold TFG ECCV video deck

**Status:** COMPLETED

## Objective

Port Hyeongmin Lee's workshop deck into Paper2PR as a faithful five-minute ECCV 2026 paper video deck, preserving source sections 07-20 verbatim, rebuilding the title and final slides, and verifying every rendered state before speaker-note authoring.

## Changes Made

| File | Change | Reason | Quality Score |
|------|--------|--------|---|
| `Quarto/talks/on-manifold-tfg.qmd` | Added the final 16-slide Reveal deck, including exact retained source HTML, 18 fragment groups, title/final rewrites, the approved transition, proof cut, and local-only notes | Paper2PR QMD is the single source of truth | 84/100 |
| `Quarto/talks/on-manifold-tfg.css` | Added the scoped source Tailwind subset, exact two-thirds reference geometry, Inter/KaTeX loading, and Reveal compatibility fixes | Preserve the authoritative 1920 x 1080 design at 1280 x 720 without preflight leakage | 84/100 |
| `Quarto/talks/on-manifold-tfg.deck.yml` | Declared five-minute remote expert delivery, English slides/notes, sources, and alias | Drive the profile, gate, fact review, and notes budget | 84/100 |
| `Quarto/talks/on-manifold-tfg.forbidden.txt` | Guarded removed workshop/bio/lab promotional strings | Prevent accidental framing regressions | 84/100 |
| `Figures/talks/on-manifold-tfg/` | Copied 26 exact source rasters, added two presenter-supplied affiliation logos, and recorded provenance metadata | Keep every figure byte-faithful and make the title affiliations explicit | 84/100 |
| `pages/index.html` | Added the generated `on-manifold tfg` talk entry | Keep the landing page consistent with the new deck | 84/100 |
| `quality_reports/plans/2026-09-01_on-manifold-tfg-eccv-video-plan.md` | Recorded architecture, resolved decisions, timing math, and ranked optional cuts | Preserve the plan and user-owned decision gates | N/A |

## Design Decisions

| Decision | Alternatives Considered | Rationale |
|----------|------------------------|-----------|
| Scale a 1920 x 1080 virtual source canvas by exactly two thirds | Reflow source utilities directly at 1280 x 720 | The PDF geometry proves the original 1920 x 1080 capture; scaling preserves every source placement and type size. |
| Generate source sections 07-20 as raw HTML with static KaTeX DOM and source annotations, then apply the approved proof cut | Retype or reconstruct formulas in Markdown | The generator extracts all 75 candidate formulas without transcription; the final proof-cut deck retains the exact 35 annotations on its remaining inherited slides. |
| Add a zero-build paper transition before source section 17, then cut only source section 19 | Keep the literal 16-slide enumeration or restore source section 06 | The approved sequence ends at 16 physical slides while retaining all 18 inherited reveal groups and the project alias. |
| Use exact author URLs on title/final | Formal affiliations or shortened site labels | The user supplied `https://alohays.github.io/` and `https://hyeongminlee.github.io/` as the author references. |
| Preserve five gate deductions | Rewrite inherited punctuation or add visible source labels to reused-image slides | Three dash forms and two attribution-context findings are source-verbatim; changing visible copy would violate the explicit fidelity constraint. |

## Incremental Work Log

**04:11 UTC:** Consolidated the source/PDF/repository audit, created `codex/on-manifold-tfg` from `main`, and saved the implementation plan without disturbing the user's `w02-authoring` checkout.

**04:11 UTC:** Extracted sections 07-20 structurally, preserved 75 LaTeX annotations and 18 build groups, copied 26 source assets byte-for-byte, and removed the complete Tailwind `@layer base` block.

**04:11 UTC:** Corrected Reveal theme leakage, KaTeX loading, source spacing selectors, proof-card wrapping, and the final-slide fragment capture; geometry now matches the source exactly on most slides and within 4.47 output pixels on the remaining browser-raster cases.

**04:11 UTC:** Applied the user-approved alias/author references and zero-build transition, producing 17 physical slides and 35 visual states. Exported and rendered a 17-page PDF.

**04:11 UTC:** Presented the timing math and ranked cuts. Yunsung approved cutting source section 19 only and confirmed no separate original-deck credit. The narration set is 16 slides, 18 reveals, and 34 visual states.

**04:11 UTC:** Drafted and independently reviewed 15 English speaker-note scripts totaling 635 standard words. The word-rate estimate is 4:53 and the final local 130-wpm TTS rehearsal ran 4:43.9. The final resources slide is intentionally silent.

**04:11 UTC:** Added the presenter-supplied MaumAI and SeoulTech logos to the title, mapped Yunsung Lee to MaumAI and Hyeongmin Lee to SeoulTech without rank labels, and updated the opening narration. The final script is 640 words.

**04:11 UTC:** Audited every audience-facing section label after the source cuts. Renumbered the retained background slides from stale source labels 04/05 to delivered labels 01/02; Setting 01-04 and The catch 01-02 were already contiguous.

## Learnings & Corrections

- [LEARN:authoring] Shortened personal-site labels changed explicitly supplied author references -> preserve exact visible URLs, including scheme and trailing slash.
- [LEARN:qa] `Reveal.isLastSlide()` becomes true before the final slide's fragments are revealed -> all-state capture must also require that no hidden fragments remain.

## Verification Results

| Check | Result | Status |
|-------|--------|--------|
| Quarto render | 16 direct slides; sequence `01,07-16,paper-transition,17,18,20,21`; no nested sections | PASS |
| Visible section numbering | Background 01-02, Setting 01-04, and The catch 01-02; original provenance IDs remain hidden | PASS |
| Source fidelity | Normalized visible source text equal on all 13 inherited slides remaining after the approved proof cut | PASS |
| Formula recovery | 35/35 final LaTeX annotations equal and in source order; 75/75 candidate annotations were parser-extracted before the cut | PASS |
| Fragments | 18 groups; 34 current 1280 x 720 states captured | PASS |
| Geometry/runtime | All 16 roots are 1280 x 720 from a 1920 x 1080 virtual canvas; no root overflow or broken image | PASS |
| Asset integrity | 26/26 inherited rasters byte-equal the source export; 2/2 affiliation logos byte-equal the presenter attachments | PASS |
| Visual audit | All browser states and PDF pages inspected; no clipping, overlap, formula corruption, controls, or unintended fragment reflow | PASS |
| Quality gate | 84/100, zero critical issues; five fidelity-mandated deductions explained above | PASS |
| Focused deploy assets | 60 local references resolve; both affiliation logos and exact author URLs present | PASS |
| Site-wide preview | Six unrelated landing links are absent because this isolated preview assembled only the requested deck | EXPECTED WARNING |
| PDF export | 16 pages, 960 x 540 pt, no Hangul or English note-phrase leak | PASS |
| Push/PR | Branch remains local; no push or PR | PASS |
| Speaker-note budget | 640 words, 4:55 estimated; 4:45.8 final local TTS rehearsal; 15/16 slides narrated | PASS |
| Notes backup | 15 blocks in `.speaker-notes/talks/on-manifold-tfg.json` | PASS |

## Open Questions / Blockers

- None. The presenter should still perform the manual `S` speaker-view check and one human rehearsal before recording.

## Next Steps

- [x] Apply the approved proof-slide cut.
- [x] Draft and back up the five-minute English speaker notes.
- [x] Re-render, recapture every state, rerun the gate/note-leak checks, and complete the concise handoff.
