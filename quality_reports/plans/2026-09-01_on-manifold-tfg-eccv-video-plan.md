# On-Manifold TFG ECCV video deck plan

## Objective

Port Hyeongmin Lee's exported On-Manifold TFG deck into Paper2PR for the ECCV 2026 five-minute paper video. The exported HTML and `slides-as-pdf.pdf` are the content and visual specification. Fidelity takes priority over Paper2PR's usual semantic slide idiom.

## Locked source facts

- The source has 21 top-level sections and 19 fragment groups.
- Sections 07-20 contain 14 slides and 18 fragment groups.
- The authoritative PDF is a 1920 x 1080 raster capture reduced to 1280 x 720 by a factor of two thirds.
- The source contains 76 one-to-one LaTeX annotations; the retained literal section set contains 75.
- The port must extract every formula from `annotation[encoding="application/x-tex"]`. No formula may be retyped.
- Sections 07-20 keep their words, order, figures, color decisions, build grouping, and attribution text.
- The title and final slides are the only content rewrites.

## Resolved decisions

1. Add one zero-build "Our paper" transition using the exact paper title and project alias `on-manifold tfg`. This gives 17 slides while preserving the 18 inherited build groups.
2. Use the two author references supplied by Yunsung: `alohays.github.io` and `hyeongminlee.github.io`.
3. Do not add a separate "original deck by" line; Hyeongmin remains named as a paper author and linked through his site.
4. Yunsung approved cutting source section 19 only and confirmed no separate original-deck credit. The final narration set keeps the alias transition.

## Target artifacts

- `Quarto/talks/on-manifold-tfg.qmd`
- `Quarto/talks/on-manifold-tfg.deck.yml`
- `Quarto/talks/on-manifold-tfg.css`
- `Quarto/talks/on-manifold-tfg.forbidden.txt`
- `Figures/talks/on-manifold-tfg/` with only the retained source assets and the required QR asset
- `Figures/talks/on-manifold-tfg/figures.yml`
- `quality_reports/handoffs/` note if that directory is established by repository precedent; otherwise a concise final handoff in this plan's completion section

## Timing decision

Before cuts, the deck had 17 physical slides and 18 inherited reveal groups: 35 visual states in 300 seconds, or 8.57 seconds per state. Yunsung approved cutting source section 19 only. The narration set therefore has 16 physical slides and 18 reveal groups: 34 visual states, or 8.82 seconds per state. Starting from the already-visible title, there are 33 `next` actions, averaging 9.09 seconds each.

Ranked optional cuts presented to Yunsung:

1. Source section 19, "Why it works: statements and proofs": the slide itself says it is reference material and not part of the spoken talk. **Approved and applied**, giving 16 slides and 34 states.
2. The added `on-manifold tfg` transition: it carries no scientific claim, but gives the narration a pacing breath and keeps the approved alias prominent. Cutting it together with proofs gives 15 slides and 33 states.
3. Source section 07, "Diffusion: repeated denoising": ECCV viewers can reasonably be assumed to know this background, although the original brief explicitly retained it.
4. Source section 10, "Generating only what you want": adjacent slides already establish the goal and classifier direction. This cut saves one physical slide and one reveal state.
5. Source section 13, "A classifier that has never seen noise": source section 14 retains the formal manifold explanation. This cut saves one physical slide and two reveal states.

## Implementation

1. Work from `main` in the isolated `codex/on-manifold-tfg` worktree. Preserve the user's `w02-authoring` checkout and its untracked files.
2. Parse the source HTML structurally. Select section 01, sections 07-20, and section 21, insert the approved zero-build paper transition before source section 17, then remove source section 19 under the approved timing cut.
3. Replace source outer `section` nodes with deck-local `div` wrappers. Nested sections are forbidden because Reveal would interpret them as vertical stacks.
4. Convert each distinct `data-frag` group to the equivalent Reveal fragment group without changing the grouped content or order. Preserve the source highlight fragment on the clean-image estimate.
5. Replace every retained rendered KaTeX subtree with its annotation LaTeX in Pandoc math delimiters or a raw HTML form that Quarto's pinned KaTeX renders identically. Assert 75 retained formulas before and after generation.
6. Rewrite asset paths into `../../Figures/talks/on-manifold-tfg/` and copy the exact retained raster assets. Do not modify either reference directory.
7. Vendor the source Tailwind theme/property/utility subset into one deck-local CSS file. Remove the complete Tailwind `@layer base` block and omit the duplicated KaTeX portion of `SectionHeader.*.css`.
8. Scope every rule to `.on-manifold-tfg` and add a Reveal compatibility layer. Reproduce the reference's two-thirds geometry, Inter typography, alternating paper backgrounds, palette, margins, and fragment behavior without allowing source scroll-snap or key handlers to leak into Reveal.
9. Author a manual Paper2PR title slide and final slide using the exact paper title, alias, and approved author-site references. Use `pagetitle`, not front-matter `title`, so Quarto does not create an extra slide.
10. Add forbidden-term guards for workshop framing and removed promotional content. Keep slide numbers off because the reference has none.

## Verification

1. Assert the approved 16-slide sequence, 18 fragment groups, 35 retained formulas after the proof cut, and the absence of workshop, speaker-bio, and ViViD Lab promotional text.
2. Run `python3 scripts/deckprofile.py talks/on-manifold-tfg`.
3. Render with `quarto render Quarto/talks/on-manifold-tfg.qmd`.
4. Capture every base slide and every fragment state at 1280 x 720. Compare all fully revealed slides against their corresponding PDF pages; inspect each image at full size.
5. Repair all clipping, overlap, unexpected wrapping, formula drift, font substitution, and broken asset paths. Source sections 07, 12, 13, and 17 receive explicit high-risk checks; source section 19 was audited before its approved removal.
6. Run `python3 scripts/quality_score.py Quarto/talks/on-manifold-tfg.qmd`. Preserve verbatim source wording even if the legacy typography causes a documented dash-lint deduction; do not rewrite it to game the gate.
7. Run the local deploy preview and asset checks with `./scripts/sync_to_docs.sh talks/on-manifold-tfg` and `python3 scripts/check_site_assets.py docs`.
8. Export the local PDF handout, confirm its page count and absence of note leakage, and visually inspect the latest render.
9. Present the corrected 300-second timing math and ranked optional cuts. Wait for Yunsung's decision before writing speaker notes.
10. Draft English five-minute notes for the approved slide set, back them up with the repository notes tool, rehearse against the word/time budget, then rerun render, screenshots, gate, and note-leak checks.

## Completion evidence

Completion requires the final QMD and deck-local assets/CSS, clean full-size renders for every slide and build, an explained quality-gate result, the approved timing decision, local-only speaker notes for five minutes, and a concise handoff listing the approved cuts and deliberate deviations. No push or pull request is authorized.

## Completion handoff

- **Changed:** rebuilt the ECCV title and final resources slides; ported the retained source markup, builds, formulas, colors, and figures; renumbered visible section-local labels after the cuts while retaining hidden source provenance IDs; added the approved zero-build `on-manifold tfg` transition; added exact clickable author URLs; placed the presenter-supplied MaumAI and SeoulTech logos with explicit author-affiliation mapping on the title; and registered the deck on the landing page.
- **Cut:** source sections 02-06 per the enumerated brief, then source section 19 only under Yunsung's timing decision. No other inherited slide or reveal was cut.
- **Deliberate deviations:** the final soft-paper RGB value follows the authoritative PDF; attribution paragraphs use semantic `figcaption` tags without visual changes; one proof-card width compensation became irrelevant after the proof cut; no separate original-deck credit was added.
- **Quality:** 84/100 PASS. The three inherited dash expressions and two inherited image-reuse slides remain as explained fidelity exceptions; rewriting them would violate verbatim carryover.
- **Notes:** 15 local-only English scripts, 640 words, 4:55 word-rate estimate and 4:45.8 local TTS rehearsal; final resources slide is silent; backup saved under `.speaker-notes/`.
- **Remaining presenter action:** open the local deck, press `S`, confirm the speaker view, and run one human rehearsal before recording. No push or PR was made.
