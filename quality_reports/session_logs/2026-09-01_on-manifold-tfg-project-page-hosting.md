# Session Log: On-Manifold TFG project-page hosting

**Date:** 2026-09-01
**Status:** COMPLETED

## Objective

Move the presentation's canonical public location beneath the existing ManLuML project page while preserving Paper2PR as the source and preventing duplicate Paper2PR Pages publication.

## Decisions

- Canonical URL: `https://manluml.github.io/on-manifold-tfg/slides/`.
- One-time static copy, with no cross-repository token or automatic synchronization.
- The Paper2PR source stays directly renderable but is excluded from its landing page and Pages artifact.
- No push or pull request is authorized in this session.

## Changes

- Added a note-free 16-slide static bundle, canonical metadata, `.nojekyll`, and `Slides` links to a project-page branch based on the latest remote `gh-pages` state.
- Added a strict, default-true, deck-only `publish` configuration field to Paper2PR.
- Updated full-site rendering, landing generation, and site assembly to omit `publish: false` decks while preserving explicit one-deck rendering.
- Marked `talks/on-manifold-tfg` as externally hosted and regenerated the Paper2PR landing page.
- Updated the framework documentation, scaffold guidance, tests, and publishing learning.

## Verification

| Check | Result | Status |
|---|---|---|
| Project bundle closure | 70/70 local references resolve from a clean Git archive | PASS |
| Browser smoke test | `/slides/` stays canonical; 16 slides, 0 broken slide images, 0 speaker-note elements | PASS |
| Project-page discovery | Two visible `Slides` links; no horizontal overflow | PASS |
| Bundle fidelity | Support files, fonts, CSS, and figures are byte-identical to the validated Paper2PR export; HTML differs only by approved path and canonical rewrites | PASS |
| Publish configuration | strict boolean, default true, explicit false, CLI lists, and filtering tests | PASS |
| Full Paper2PR render | 6 publishable decks rendered; `talks/on-manifold-tfg` skipped | PASS |
| Paper2PR site assembly | 261 references resolve; no On-Manifold HTML, files directory, loose CSS, figures, or landing entry | PASS |
| Direct external render | explicit `render_decks.sh talks/on-manifold-tfg` still succeeds | PASS |
| Deck quality | 84/100 PASS with the five previously documented source-fidelity deductions | PASS |
| External mutation | local commits only; no push or PR | PASS |

## Operational note

Because the user selected a one-time copy, future deck edits do not propagate automatically. Re-export a freshly validated, speaker-note-stripped bundle and replace the project-page `slides/` subtree manually whenever the QMD changes.
